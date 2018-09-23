from panda3d.core import Vec3, Point3, TransformState, GeomNode, CollisionNode, NodePath, BitMask32
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletTriangleMesh, BulletTriangleMeshShape, BulletGhostNode
from panda3d.bsp import BSPFaceAttrib

from src.coginvasion.globals import CIGlobals

def isLocalAvatar(collider):
    return collider.hasPythonTag("localAvatar")

def getHitPosFromCamera(mask = CIGlobals.WallGroup | CIGlobals.FloorGroup | CIGlobals.StreetVisGroup, dist = 1000.0):
    pFrom = base.camera.getPos(render)
    pTo = pFrom + (base.camera.getQuat(render).xform(Vec3.forward()) * dist)
    result = base.physicsWorld.rayTestClosest(pFrom, pTo, mask)
    if result.hasHit():
        return result.getHitPos()
    return pTo

def extentsFromMinMax(min, max):
    return Vec3((max.getX() - min.getX()) / 2.0,
                (max.getY() - min.getY()) / 2.0,
                (max.getZ() - min.getZ()) / 2.0)

def centerFromMinMax(min, max):
    return (min + max) / 2.0

def makeBulletBoundingBoxColl(node):
    """
    Creates and attaches a BulletRigidBodyNode underneath `node` which contains
    a BulletBoxShape that covers the tight bounds of `node`.
    Useful for quick prop collisions and such.
    """
    mins = Point3(0)
    maxs = Point3(0)
    node.calcTightBounds(mins, maxs)

    extents = extentsFromMinMax(mins, maxs)
    tsCenter = TransformState.makePos(centerFromMinMax(mins, maxs))

    shape = BulletBoxShape(extents)
    rbnode = BulletRigidBodyNode(node.getName() + "_bulletBoundingBoxColl")
    rbnode.addShape(shape, tsCenter)
    rbnode.setKinematic(True)
    rbnodeNp = render.attachNewNode(rbnode)
    rbnodeNp.wrtReparentTo(node)
    rbnodeNp.setCollideMask(WallGroup)
    base.physicsWorld.attachRigidBody(rbnode)

def makeBulletBoxColl(node, extents):

    shape = BulletBoxShape(extents)
    rbnode = BulletRigidBodyNode(node.getName() + "_bulletBoxColl")
    rbnode.addShape(shape)
    rbnode.setKinematic(True)
    rbnodeNp = node.attachNewNode(rbnode)
    rbnodeNp.setCollideMask(WallGroup)
    base.physicsWorld.attachRigidBody(rbnode)

def makeBulletCollFromGeoms(rootNode, exclusions = []):
    """
    Creates and attaches bullet triangle mesh nodes underneath each GeomNode
    of `rootNode`, which contains the same mesh as the Geoms.
    This can be expensive if the geometry contains lots of triangles or GeomNodes.
    """

    # BulletRigidBodyNode -> triangle index -> material
    # (it's so we know which surface we are walking on)
    result = {}

    for faceNp in rootNode.findAllMatches("**"):
        if faceNp.getName() in exclusions:
            continue
        if faceNp.node().getType() != GeomNode.getClassType():
            continue

        # Create a separate list of geoms for each possible face type
        # ( a wall or floor )
        type2geoms = {}
        for i in xrange(faceNp.node().getNumGeoms()):
            geom = faceNp.node().getGeom(i)
            state = faceNp.node().getGeomState(i)
            if not geom.getPrimitive(0).isIndexed():
                continue
            if state.hasAttrib(BSPFaceAttrib.getClassSlot()):
                bca = state.getAttrib(BSPFaceAttrib.getClassSlot())
                facetype = bca.getFaceType()
                if not type2geoms.has_key(facetype):
                    type2geoms[facetype] = [(geom, state)]
                else:
                    type2geoms[facetype].append((geom, state))

        # Now create a separate body node to group each face type,
        # and assign the correct bit
        for facetype, geoms in type2geoms.items():
            data = {}
            numGeoms = 0
            mesh = BulletTriangleMesh()
            for i in xrange(len(geoms)):
                geom, state = geoms[i]
                mesh.addGeom(geom, True)
                bca = state.getAttrib(BSPFaceAttrib.getClassSlot())
                mat = bca.getMaterial()
                for j in xrange(geom.getNumPrimitives()):
                    prim = geom.getPrimitive(j)
                    prim = prim.decompose()
                    tris = prim.getNumVertices() / 3
                    for tidx in xrange(tris):
                        data[numGeoms] = mat
                        numGeoms += 1
            shape = BulletTriangleMeshShape(mesh, False)
            rbnode = BulletRigidBodyNode(faceNp.getName() + "_bullet_type" + str(facetype))
            rbnode.setKinematic(True)
            rbnode.addShape(shape)
            rbnodeNp = NodePath(rbnode)
            rbnodeNp.reparentTo(faceNp)
            if facetype == BSPFaceAttrib.FACETYPE_WALL:
                rbnodeNp.setCollideMask(CIGlobals.WallGroup)
            elif facetype == BSPFaceAttrib.FACETYPE_FLOOR:
                rbnodeNp.setCollideMask(CIGlobals.FloorGroup)
            base.physicsWorld.attachRigidBody(rbnode)
            result[rbnode] = data

    return result

def makeBulletCollFromPandaColl(rootNode, exclusions = []):
    """
    Replaces all of the CollisionNodes underneath `rootNode` with static
    BulletRigidBodyNodes/GhostNodes which contain the shapes from the CollisionNodes.

    Applies the same transform as the node it is replacing, goes underneath same parent,
    has same name, has same collide mask.

    If the Panda CollisionNode is intangible, a BulletGhostNode is created.
    Else, a BulletRigidBodyNode is created.
    """

    for pCollNp in rootNode.findAllMatches("**"):
        if pCollNp.getName() in exclusions:
            continue
        if pCollNp.node().getType() != CollisionNode.getClassType():
            continue
        if pCollNp.node().getNumSolids() == 0:
            continue

        mask = pCollNp.node().getIntoCollideMask()
        group = CIGlobals.WallGroup
        if mask == CIGlobals.FloorBitmask:
            group = CIGlobals.FloorGroup
        elif mask == CIGlobals.EventBitmask:
            group = CIGlobals.LocalAvGroup
        elif mask == CIGlobals.CameraBitmask:
            group = CIGlobals.CameraGroup

        isGhost = not pCollNp.node().getSolid(0).isTangible()
        if isGhost:
            rbnode = BulletGhostNode(pCollNp.getName())
            group = CIGlobals.LocalAvGroup
        else:
            rbnode = BulletRigidBodyNode(pCollNp.getName())
        rbnode.addShapesFromCollisionSolids(pCollNp.node())
        for shape in rbnode.getShapes():
            if shape.isOfType(BulletTriangleMeshShape.getClassType()):
                shape.setMargin(0.1)
        rbnode.setKinematic(True)
        rbnodeNp = NodePath(rbnode)
        rbnodeNp.reparentTo(pCollNp.getParent())
        rbnodeNp.setTransform(pCollNp.getTransform())
        rbnodeNp.setCollideMask(group)
        # Now that we're using bullet collisions, we don't need the panda collisions anymore.
        pCollNp.removeNode()

def rayTestAllSorted(pFrom, pTo, mask = BitMask32.allOn()):
    result = base.physicsWorld.rayTestAll(pFrom, pTo, mask)
    sortedHits = None
    if result.hasHits():
        sortedHits = sorted(result.getHits(), key = lambda hit: (pFrom - hit.getHitPos()).length())
    return [result, sortedHits]

def rayTestClosestNotMe(me, pFrom, pTo, mask = BitMask32.allOn()):
    _, hits = rayTestAllSorted(pFrom, pTo, mask)
    if hits is not None:
        for i in xrange(len(hits)):
            hit = hits[i]
            hitNp = NodePath(hit.getNode())
            if not me.isAncestorOf(hitNp) and me != hitNp:
                return hit
    return None


def isChildOfLA(node):
    return hasattr(base, 'localAvatar') and base.localAvatar.isAncestorOf(node)

def detachBulletNodes(rootNode):
    for rbnode in rootNode.findAllMatches("**/+BulletRigidBodyNode"):
        if isChildOfLA(rbnode):
            print "Tried to detach body node of local avatar!"
            continue
        base.physicsWorld.removeRigidBody(rbnode.node())
    for ghostnode in rootNode.findAllMatches("**/+BulletGhostNode"):
        if isChildOfLA(ghostnode):
            print "Tried to detach ghost node of local avatar!"
            continue
        base.physicsWorld.removeGhost(ghostnode.node())

def attachBulletNodes(rootNode):
    for rbnode in rootNode.findAllMatches("**/+BulletRigidBodyNode"):
        base.physicsWorld.attachRigidBody(rbnode.node())
    for ghostnode in rootNode.findAllMatches("**/+BulletGhostNode"):
        base.physicsWorld.attachGhost(ghostnode.node())
        
def removeBulletNodes(rootNode):
    for rbnode in rootNode.findAllMatches("**/+BulletRigidBodyNode"):
        if isChildOfLA(rbnode):
            print "Tried to remove body node of local avatar!"
            continue
        rbnode.removeNode()
    for ghostnode in rootNode.findAllMatches("**/+BulletGhostNode"):
        if isChildOfLA(ghostnode):
            print "Tried to remove ghost node of local avatar!"
            continue
        ghostnode.removeNode()
        
def detachAndRemoveBulletNodes(rootNode):
    detachBulletNodes(rootNode)
    removeBulletNodes(rootNode)

def __ghostNodeWatcherTask(triggerNp, callback, extraArgs, task):
    if triggerNp.isEmpty() or not triggerNp.node().isOfType(BulletGhostNode.getClassType()):
        return task.done

    for node in triggerNp.node().getOverlappingNodes():
        if node.hasPythonTag("localAvatar") and base.localAvatar.walkControls.getCollisionsActive():
            callback(*extraArgs)
            return task.done
    return task.cont

def watchForLocalAvatarTrigger(triggerNp, callback, extraArgs = []):
    if triggerNp.isEmpty():
        return
    taskMgr.add(__ghostNodeWatcherTask, "triggerWatch-" + str(id(triggerNp.node())), extraArgs = [triggerNp, callback, extraArgs], appendTask = True)

def stopWatchingTriggerColls(triggerNp):
    if triggerNp.isEmpty():
        return
    taskMgr.remove("triggerWatch-" + str(id(triggerNp.node())))

def enableLocalAvatarTriggerEvents(ghostNode, extraArgs = []):
    if ghostNode is None or ghostNode.isEmpty() or not ghostNode.node().isOfType(BulletGhostNode.getClassType()):
        return

    GhostNodeLocalAvBroadcaster(ghostNode, extraArgs)
    
def getNearestGroundSurfaceZ(rootNode, height):
    """ Uses a ray test to find the nearest ground surface. Returns the found surface's Z value or -1 if no surface is found. """
    
    if isinstance(rootNode, NodePath) and not rootNode.isEmpty():
        pFrom = Point3(rootNode.getPos(render))
        pDown = Point3(pFrom - Point3(0, 0, height))
        downTest = base.physicsWorld.rayTestClosest(pFrom, pDown, CIGlobals.FloorGroup | CIGlobals.StreetVisGroup)
        
        return downTest.getHitPos().z
    else:
        raise Exception("#getNearestGroundSurfaceZ(): Requires a non-empty NodePath to ray test on!")
    
    return -1

class GhostNodeLocalAvBroadcaster:
    """Fires events when the local avatar enters and leaves the ghost node."""

    def __init__(self, ghostNode, extraArgs = []):
        self.ghostNode = ghostNode
        self.extraArgs = extraArgs
        self.prevOverlapping = []

        taskMgr.add(self.__update, "ghostNodeWatch-" + str(id(self)))

    def __update(self, task):
        if self.ghostNode.isEmpty():
            del self.ghostNode
            del self.prevOverlapping
            del self.extraArgs
            return task.done

        if self.ghostNode.getTopNode() != base.localAvatar.getTopNode():
            # The ghost node is not in the same scene graph (hidden or something).
            # Don't check for collisions
            return task.cont

        overlapping = []

        result = base.physicsWorld.contactTest(self.ghostNode.node())
        for contact in result.getContacts():
            overlapping.append(contact.getNode1())

        for node in overlapping:
            if node not in self.prevOverlapping and node.hasPythonTag("localAvatar") and base.localAvatar.walkControls.getCollisionsActive():
                # The avatar has entered this ghost node.
                messenger.send('enter' + self.ghostNode.getName(), self.extraArgs)
                break

        for node in self.prevOverlapping:
            if node not in overlapping and node.hasPythonTag("localAvatar") and base.localAvatar.walkControls.getCollisionsActive():
                # The avatar has exited this ghost node.
                messenger.send('exit' + self.ghostNode.getName(), self.extraArgs)
                break

        self.prevOverlapping = list(overlapping)
        return task.cont