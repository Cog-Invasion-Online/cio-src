from panda3d.core import Vec3, Point3, Quat, BitMask32, TransformState, MeshDrawer, Vec4, LineSegs, NodePath
from panda3d.bullet import BulletCapsuleShape, BulletRigidBodyNode, BulletGhostNode, BulletSphereShape

from direct.showbase.DirectObject import DirectObject

from src.coginvasion.globals import CIGlobals

import math

class BulletCharacterController(DirectObject):
    """
    The custom kinematic character controller for Panda3D, replacing the Bullet's default character controller and providing more stability and features.
    
    Features included:
        * Walking with penetration prevention
        * Jumping with active and passive jump limiter. Active means limiting the max jump height based on the distance to the "ceiling". Passive means falling automatically when a "ceiling" is hit.
        * Crouching with stand up limiter which prevents the character from standing up if inside a tunnel or other limited space
        * Slope limiter of arbitrary maximum slope values which may or may not affect the movement speed on slopes smaller than maximum
        * Stepping, supports walking steps up and down (prevents "floating" effect)
        * Flying support for no-clip, ladders, swimming or simply flying
        * Simplified state system. Makes double/multiple jumps impossible by default 
        * Callbacks for landing and standing up from crouch
    
    The controller is composed of a levitating capsule (allowing stepping), a kinematic body and numerous raycasts accounting for levitation and spacial awareness.
    The elements are set up automatically.
    """
    def __init__(self, world, parent, walkHeight, crouchHeight, stepHeight, radius, gravity=None):
        """
        World -- (BulletWorld) the Bullet world.
        Parent -- (NodePath) where to parent the KCC elements
        walkHeight -- (float) height of the whole controller when walking
        crouchHeight -- (float) height of the whole controller when crouching
        stepHeight -- (float) maximum step height the caracter can walk.
        radius -- (float) capsule radius
        gravity -- (float) gravity setting for the character controller, currently as float (gravity is always down). The KCC may sometimes need a different gravity setting then the rest of the world. If this is not given, the gravity is same as world's
        """

        DirectObject.__init__(self)
        
        self.__world = world
        self.__parent = parent
        self.__timeStep = 0
        self.__targetPos = Vec3(0, 0, 0)
        self.__currentPos = Vec3(0, 0, 0)
        self.__radius = radius
        self.__walkHeight = walkHeight
        self.__spam = False
        self.__aboveGround = True
        self.__prevOverlapping = []

        self.currLineSegsGeom = None
        
        self.movementParent = self.__parent.attachNewNode("Movement Parent")
        self.__setup(walkHeight, crouchHeight, stepHeight, radius)
        self.__mapMethods()
        
        self.gravity = self.__world.getGravity().z if gravity is None else gravity
        self.setMaxSlope(50.0, True)
        self.setActiveJumpLimiter(True)
        
        self.movementState = "ground"
        self.movementStateFilter = {
            "ground": ["ground", "jumping", "falling"],
            "jumping": ["ground", "falling"],
            "falling": ["ground"],
            "flying": [],
        }
        
        # Prevent the KCC from moving when there's not enough room for it in the next frame
        # It doesn't work right now because I can't figure out how to add sliding. Sweep test could work, but it would cause problems with penetration testing and steps
        # That said, you probably won't need it, if you design your levels correctly
        self.predictFutureSpace = True
        self.futureSpacePredictionDistance = 10.0
        
        self.isCrouching = False
        
        self.__fallTime = 0.0
        self.__fallStartPos = self.__currentPos.z
        self.__linearVelocity = Vec3(0, 0, 0)
        self.__headContact = None
        self.__footContact = None
        self.__enabledCrouch = False
        
        self.__standUpCallback = [None, [], {}]
        self.__fallCallback = [None, [], {}]

    def enableSpam(self):
        self.__spam = True
        
    def setPythonTag(self, *args):
        self.__walkCapsuleNP.setPythonTag(*args)
        self.__crouchCapsuleNP.setPythonTag(*args)
    
    def setCollideMask(self, *args):
        self.__walkCapsuleNP.setCollideMask(*args)
        self.__crouchCapsuleNP.setCollideMask(*args)
    
    def setFallCallback(self, method, args=[], kwargs={}):
        """
        Callback called when the character falls on thge ground.
        
        The position where falling started is passed as the first argument, the additional argument and keyword arguments follow.
        """
        self.__fallCallback = [method, args, kwargs]
    
    def setStandUpCallback(self, method, args=[], kwargs={}):
        """
        Callback called when the character stands up from crouch. This is needed because standing up might be prevented by spacial awareness. 
        """
        self.__standUpCallback = [method, args, kwargs]
    
    def setMaxSlope(self, degs, affectSpeed):
        """
        degs -- (float) maximum slope in degrees. 0, False or None means don't limit slope.
        affectSpeed -- (bool) if True, the character will walk slower up slopes
        
        Both options are independent.
        
        By default, affectSpeed is enabled and maximum slope is 50 deg.
        """
        if not degs:
            self.minSlopeDot = None
            return
        self.minSlopeDot = round(math.cos(math.radians(degs)), 2)
        
        self.__slopeAffectsSpeed = affectSpeed
    
    def setActiveJumpLimiter(self, val):
        """
        Enable or disable the active jump limiter, which is the mechanism that changes the maksimum jump height based on the space available above the character's head.
        """
        self.__intelligentJump = val
    
    def startCrouch(self):
        self.isCrouching = True
        self.__enabledCrouch = True
        
        self.capsule = self.__crouchCapsule
        self.capsuleNP = self.__crouchCapsuleNP
        
        self.__capsuleH, self.__levitation, self.__capsuleR, self.__h = self.__crouchCapsuleH, self.__crouchLevitation, self.__crouchCapsuleR, self.__crouchH
        
        self.__world.removeRigidBody(self.__walkCapsuleNP.node())
        self.__world.attachRigidBody(self.__crouchCapsuleNP.node())
        
        self.__capsuleOffset = self.__capsuleH * 0.5 + self.__levitation
        self.__footDistance = self.__capsuleOffset + self.__levitation
    
    def stopCrouch(self):
        """
        Note that spacial awareness may prevent the character from standing up immediately, which is what you usually want. Use stand up callback to know when the character stands up.
        """
        self.__enabledCrouch = False
    
    def isOnGround(self):
        """
        Check if the character is on ground. You may also check if the movementState variable is set to 'ground'
        """
        if self.__footContact is None:
            return False
        elif self.movementState == "ground":
            elevation = self.__targetPos.z - self.__footContact[0].z
            return (elevation <= 0.02)
        else:
            return self.__targetPos.z <= self.__footContact[0].z
    
    def startJump(self, maxHeight=3.0):
        """
        max height is 3.0 by default. Probably too much for most uses.
        """
        self.__jump(maxHeight)
    
    def startFly(self):
        self.movementState = 'flying'
    
    def stopFly(self):
        """
        Stop flying and start falling
        """
        self.__fall()
    
    def setAngularMovement(self, omega):
        self.movementParent.setH(self.movementParent, omega * self.__timeStep)
    
    def setLinearMovement(self, speed, *args):
        self.__linearVelocity = speed
    
    def update(self):
        """
        Update method. Call this around doPhysics.
        """
        processStates = {
            "ground": self.__processGround,
            "jumping": self.__processJumping,
            "falling": self.__processFalling,
            "flying": self.__processFlying,
        }

        self.__currentPos = self.movementParent.getPos(render)
        self.__targetPos = Vec3(self.__currentPos)
        
        pFrom = self.capsuleNP.getPos(render)
        pTo = pFrom - (0, 0, 2000)
        result = base.physicsWorld.rayTestClosest(pFrom, pTo, CIGlobals.WallGroup | CIGlobals.FloorGroup | CIGlobals.StreetVisGroup)
        # Only fall if there is a ground for us to fall onto.
        # Prevents the character from falling out of the world.
        self.__aboveGround = result.hasHit()
        
        self.__timeStep = globalClock.getDt()
        
        self.__updateEventSphere()
        self.__updateFootContact()
        self.__updateHeadContact()
        
        processStates[self.movementState]()
        
        self.__applyLinearVelocity()
        self.__preventPenetration()
        
        self.__updateCapsule()
        
        if self.isCrouching and not self.__enabledCrouch:
            self.__standUp()

    def __updateEventSphere(self):
        overlapping = []

        result = base.physicsWorld.contactTest(self.eventSphereNP.node())
        for contact in result.getContacts():
            overlapping.append(contact.getNode1())

        for node in overlapping:
            if node not in self.__prevOverlapping:
                # The avatar has entered this node.
                messenger.send('enter' + node.getName(), [NodePath(node)])

        for node in self.__prevOverlapping:
            if node not in overlapping:
                # The avatar has exited this node.
                messenger.send('exit' + node.getName(), [NodePath(node)])

        self.__prevOverlapping = list(overlapping)
    
    def __land(self):
        self.movementState = "ground"
    
    def __fall(self):
        self.movementState = "falling"
        
        self.__fallStartPos = self.__targetPos.z
        self.fallDelta = 0.0
        self.__fallTime = 0.0

    def removeCapsules(self):
        self.__world.removeRigidBody(self.__crouchCapsuleNP.node())
        self.__world.removeRigidBody(self.__walkCapsuleNP.node())
    
    def __jump(self, maxZ = 3.0):
        if "jumping" not in self.movementStateFilter[self.movementState]:
            return
        
        maxZ += self.__targetPos.z
        
        if self.__intelligentJump and self.__headContact is not None and self.__headContact[0].z < maxZ + self.__h:
            maxZ = self.__headContact[0].z - self.__h * 1.2
        
        maxZ = round(maxZ, 2)
        
        self.jumpStartPos = self.__targetPos.z
        self.jumpTime = 0.0
        
        bsq = -4.0 * self.gravity * (maxZ - self.jumpStartPos)
        try:
            b = math.sqrt(bsq)
        except:
            return
        self.jumpSpeed = b
        self.jumpMaxHeight = maxZ
        
        self.movementState = "jumping"
        messenger.send("jumpStart")
    
    def __standUp(self):
        self.__updateHeadContact()
        
        if self.__headContact is not None:
            z = self.__targetPos.z + self.__walkLevitation + self.__walkCapsuleH
            if z >= self.__headContact[0].z:
                return
        
        self.isCrouching = False
        
        self.capsule = self.__walkCapsule
        self.capsuleNP = self.__walkCapsuleNP
        
        self.__capsuleH, self.__levitation, self.__capsuleR, self.__h = self.__walkCapsuleH, self.__walkLevitation, self.__walkCapsuleR, self.__walkH
        
        self.__world.removeRigidBody(self.__crouchCapsuleNP.node())
        self.__world.attachRigidBody(self.__walkCapsuleNP.node())
        
        self.__capsuleOffset = self.__capsuleH * 0.5 + self.__levitation
        self.__footDistance = self.__capsuleOffset + self.__levitation
        
        if self.__standUpCallback[0] is not None:
            self.__standUpCallback[0](*self.__standUpCallback[1], **self.__standUpCallback[2])
    
    def __processGround(self):
        if not self.isOnGround():
            self.__fall()
        else:
            self.__targetPos.z = self.__footContact[0].z
    
    def __processFalling(self):
        if not self.__aboveGround:
            # Don't fall if we don't have a ground to fall onto!
            return
            
        self.__fallTime += self.__timeStep
        self.fallDelta = self.gravity * (self.__fallTime) ** 2
        
        newPos = Vec3(self.__targetPos)
        newPos.z = self.__fallStartPos + self.fallDelta
        
        self.__targetPos = newPos
        
        if self.isOnGround():
            self.__land()
            if self.__fallCallback[0] is not None:
                self.__fallCallback[0](self.__fallStartPos - newPos.z, *self.__fallCallback[1], **self.__fallCallback[2])
    
    def __processJumping(self):
        if self.__headContact is not None and self.__capsuleTop >= self.__headContact[0].z:
            # This shouldn't happen, but just in case, if we hit the ceiling, we start to fall
            self.__fall()
            return
        
        if not self.__aboveGround:
            # Don't jump either if we are not above a ground.
            # Emulate the original toontown mechanisms.
            return
        
        oldPos = float(self.__targetPos.z)
        
        self.jumpTime += self.__timeStep
        
        self.__targetPos.z = (self.gravity * self.jumpTime**2) + (self.jumpSpeed * self.jumpTime) + self.jumpStartPos
        
        if round(self.__targetPos.z, 2) >= self.jumpMaxHeight:
            self.__fall()
    
    def __processFlying(self):
        if self.__footContact and self.__targetPos.z - 0.1 < self.__footContact[0].z and self.__linearVelocity.z < 0.0:
            self.__targetPos.z = self.__footContact[0].z
            self.__linearVelocity.z = 0.0
        
        if self.__headContact and self.__capsuleTop >= self.__headContact[0].z and self.__linearVelocity.z > 0.0:
            self.__linearVelocity.z = 0.0
    
    
    
    def __checkFutureSpace(self, globalVel):
        globalVel = globalVel * self.futureSpacePredictionDistance
        
        pFrom = Point3(self.capsuleNP.getPos(render) + globalVel)
        pUp = Point3(pFrom + Point3(0, 0, self.__capsuleH * 2.0))
        pDown = Point3(pFrom - Point3(0, 0, self.__capsuleH * 2.0 + self.__levitation))
        
        upTest = self.__world.rayTestClosest(pFrom, pUp, CIGlobals.WallGroup)
        downTest = self.__world.rayTestClosest(pFrom, pDown, CIGlobals.FloorGroup | CIGlobals.StreetVisGroup)
        
        if not (upTest.hasHit() and downTest.hasHit()):
            return True
        
        upNode = upTest.getNode()
        if upNode.getMass() or upNode.isOfType(BulletGhostNode.getClassType()):
            return True
        
        space = abs(upTest.getHitPos().z - downTest.getHitPos().z)
        
        if space < self.__levitation + self.__capsuleH + self.capsule.getRadius():
            return False
        
        return True
    
    
    def __updateFootContact(self):
        if not self.__aboveGround:
            pFrom = self.capsuleNP.getPos(render)
            pTo = pFrom + (0, 0, 2000)
            result = base.physicsWorld.rayTestClosest(pFrom, pTo, CIGlobals.WallGroup | CIGlobals.FloorGroup | CIGlobals.StreetVisGroup)
            if result.hasHit():
                self.__footContact = [result.getHitPos(), result.getNode(), result.getHitNormal()]
                self.__targetPos.z = self.__footContact[0].z
                self.movementState = "ground"
                return

        pFrom = Point3(self.capsuleNP.getPos(render))
        pTo = Point3(pFrom - Point3(0, 0, self.__footDistance))
        result = self.__world.rayTestAll(pFrom, pTo, CIGlobals.WallGroup | CIGlobals.FloorGroup | CIGlobals.StreetVisGroup)
        
        if not result.hasHits():
            self.__footContact = None
            return
        
        sorted_hits = sorted(result.getHits(), key = lambda hit: (pFrom - hit.getHitPos()).length())
        
        for hit in sorted_hits:
            if type(hit.getNode()) is BulletGhostNode:
                continue
            
            if self.__spam and False:
                dat = base.materialData.get(hit.getNode(), None)
                if dat:
                    mat = dat.get(hit.getTriangleIndex(), None)
                    if mat:
                        if base.player.getCurrentSurface() != mat:
                            base.player.setCurrentSurface(mat)
            self.__footContact = [hit.getHitPos(), hit.getNode(), hit.getHitNormal()]
            break
    
    def __updateHeadContact(self):
        pFrom = Point3(self.capsuleNP.getPos(render))
        pTo = Point3(pFrom + Point3(0, 0, self.__capsuleH * 20.0))
        result = self.__world.rayTestAll(pFrom, pTo, CIGlobals.WallGroup)
        
        if not result.hasHits():
            self.__headContact = None
            return
        
        sorted_hits = sorted(result.getHits(), key = lambda hit: (pFrom - hit.getHitPos()).length())
        
        for hit in sorted_hits:
            if type(hit.getNode()) is BulletGhostNode:
                continue
            
            self.__headContact = [hit.getHitPos(), hit.getNode()]
            break
    
    def __updateCapsule(self):
        self.movementParent.setPos(render, self.__targetPos)
        self.capsuleNP.setPos(0, 0, self.__capsuleOffset)
        
        self.__capsuleTop = self.__targetPos.z + self.__levitation + self.__capsuleH * 2.0
    
    def __applyLinearVelocity(self):
        globalVel = self.movementParent.getQuat(render).xform(self.__linearVelocity) * self.__timeStep
        
        if self.predictFutureSpace and not self.__checkFutureSpace(globalVel):
            return
        
        if self.__footContact is not None and self.minSlopeDot and self.movementState != "flying":
            normalVel = Vec3(globalVel)
            normalVel.normalize()
            
            floorNormal = self.__footContact[2]
            absSlopeDot = round(floorNormal.dot(Vec3.up()), 2)
            
            def applyGravity():
                self.__targetPos -= Vec3(floorNormal.x, floorNormal.y, 0.0) * self.gravity * self.__timeStep * 0.1
            
            if absSlopeDot <= self.minSlopeDot:
                applyGravity()
                
                if globalVel != Vec3():
                    globalVelDir = Vec3(globalVel)
                    globalVelDir.normalize()
                    
                    fn = Vec3(floorNormal.x, floorNormal.y, 0.0)
                    fn.normalize()
                    
                    velDot = 1.0 - globalVelDir.angleDeg(fn) / 180.0
                    if velDot < 0.5:
                        self.__targetPos -= Vec3(fn.x * globalVel.x, fn.y * globalVel.y, 0.0) * velDot
                    
                    globalVel *= velDot
            
            elif self.__slopeAffectsSpeed and globalVel != Vec3():
                applyGravity()
        
        self.__targetPos += globalVel

    def __computeReflectionDirection(self, dir, normal):
        refl = dir - (normal * (dir.dot(normal) * 2.0))
        return refl

    def __parallelComponent(self, dir, normal):
        mag = dir.dot(normal)
        return normal * mag

    def __perpendicularComponent(self, dir, normal):
        return dir - self.__parallelComponent(dir, normal)
    
    def __preventPenetration(self):
        maxIter = 10
        fraction = 1.0

        if self.__spam:
            lines = LineSegs()
            lines.setColor(1, 0, 0, 1)
            lines.setThickness(2)
        
        collisions = Vec3(0)
        
        offset = Point3(0, 0, self.__capsuleOffset)
        
        while (fraction > 0.01 and maxIter > 0):
        
            currentTarget = self.__targetPos + collisions
        
            tsFrom = TransformState.makePos(self.__currentPos + offset)
            tsTo = TransformState.makePos(currentTarget + offset)
            result = self.__world.sweepTestClosest(self.capsuleNP.node().getShape(0), tsFrom, tsTo, CIGlobals.WallGroup, 1e-7)
            if result.hasHit() and (type(result.getNode()) is not BulletGhostNode):
                if result.getNode().getCollisionResponse():
                    fraction -= result.getHitFraction()
                    normal = result.getHitNormal()
                    direction = result.getToPos() - result.getFromPos()
                    distance = direction.length()
                    direction.normalize()
                    if distance != 0:
                        reflDir = self.__computeReflectionDirection(direction, normal)
                        reflDir.normalize()
                        collDir = self.__parallelComponent(reflDir, normal)
                        if self.__spam:
                            lines.moveTo(result.getFromPos())
                            lines.drawTo(result.getHitPos())
                        collisions += collDir * distance
                
            maxIter -= 1
            
        collisions.z = 0.0

        if collisions.length() != 0 and self.__spam:
            if self.currLineSegsGeom:
                self.currLineSegsGeom.removeNode()
                self.currLineSegsGeom = None
            self.currLineSegsGeom = render.attachNewNode(lines.create())

        self.__targetPos += collisions
    
    def __mapMethods(self):
        self.getHpr = self.movementParent.getHpr
        self.getH = self.movementParent.getH
        self.getP = self.movementParent.getP
        self.getR = self.movementParent.getR
        
        self.getPos = self.movementParent.getPos
        self.getX = self.movementParent.getX
        self.getY = self.movementParent.getY
        self.getZ = self.movementParent.getZ
        
        self.getQuat = self.movementParent.getQuat
        
        self.setHpr = self.movementParent.setHpr
        self.setH = self.movementParent.setH
        self.setP = self.movementParent.setP
        self.setR = self.movementParent.setR
        
        self.setQuat = self.movementParent.setQuat
    
    def setPos(self, *args):
        self.movementParent.setPos(*args)
        self.__currentPos = self.movementParent.getPos(render)
    
    def setX(self, *args):
        self.movementParent.setX(*args)
        self.__currentX = self.movementParent.getX(render)
    
    def setY(self, *args):
        self.movementParent.setY(*args)
        self.__currentY = self.movementParent.getY(render)
    
    def setZ(self, *args):
        self.movementParent.setZ(*args)
        self.__currentZ = self.movementParent.getZ(render)
    
    def __setup(self, walkH, crouchH, stepH, R):
        def setData(fullH, stepH, R):
            if fullH - stepH <= R * 2.0:
                length = 0.1
                R = (fullH * 0.5) - (stepH * 0.5)
                lev = stepH
            else:
                length = fullH - (R * 2.0)
                lev = R + stepH
            
            return length, lev, R
        
        self.__walkH = walkH
        self.__crouchH = crouchH
        
        self.__walkCapsuleH, self.__walkLevitation, self.__walkCapsuleR = setData(walkH, stepH, R)
        self.__crouchCapsuleH, self.__crouchLevitation, self.__crouchCapsuleR = setData(crouchH, stepH, R)
        
        self.__capsuleH, self.__levitation, self.__capsuleR, self.__h = self.__walkCapsuleH, self.__walkLevitation, self.__walkCapsuleR, self.__walkH
        
        self.__capsuleOffset = self.__capsuleH * 0.5 + self.__levitation
        self.__footDistance = self.__capsuleOffset + self.__levitation
        
        self.__addElements()
    
    def __addElements(self):
        # Walk Capsule
        self.__walkCapsule = BulletCapsuleShape(self.__walkCapsuleR, self.__walkCapsuleH)
        
        self.__walkCapsuleNP = self.movementParent.attachNewNode(BulletRigidBodyNode('Capsule'))
        self.__walkCapsuleNP.node().addShape(self.__walkCapsule)
        self.__walkCapsuleNP.node().setKinematic(True)
        self.__walkCapsuleNP.node().setCcdMotionThreshold(1e-7)
        self.__walkCapsuleNP.node().setCcdSweptSphereRadius(self.__walkCapsuleR)
        self.__walkCapsuleNP.setCollideMask(BitMask32.allOn())
        
        self.__world.attachRigidBody(self.__walkCapsuleNP.node())
        
        # Crouch Capsule
        self.__crouchCapsule = BulletCapsuleShape(self.__crouchCapsuleR, self.__crouchCapsuleH)
        
        self.__crouchCapsuleNP = self.movementParent.attachNewNode(BulletRigidBodyNode('crouchCapsule'))
        self.__crouchCapsuleNP.node().addShape(self.__crouchCapsule)
        self.__crouchCapsuleNP.node().setKinematic(True)
        self.__crouchCapsuleNP.node().setCcdMotionThreshold(1e-7)
        self.__crouchCapsuleNP.node().setCcdSweptSphereRadius(self.__crouchCapsuleR)
        self.__crouchCapsuleNP.setCollideMask(BitMask32.allOn())
        
        # Set default
        self.capsule = self.__walkCapsule
        self.capsuleNP = self.__walkCapsuleNP

        # Make the event sphere a tiny bit bigger than the capsule
        # so our capsule doesn't block the event sphere from entering triggers.
        eventSphere = BulletSphereShape(self.__walkCapsuleR * 1.06)
        self.eventSphereNP = self.movementParent.attachNewNode(BulletGhostNode('eventSphere'))
        self.eventSphereNP.node().addShape(eventSphere, TransformState.makePos(Point3(0, 0, self.__walkCapsuleR - 0.1)))
        self.eventSphereNP.node().setKinematic(True)
        self.eventSphereNP.setCollideMask(CIGlobals.EventGroup)
        self.__world.attach(self.eventSphereNP.node())
        
        # Init
        self.__updateCapsule()
