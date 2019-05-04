
class Motor:

    def __init__(self, node):
        self.node = node
        self.task = None
        self.fwdSpeed = 10.0
        self.rotSpeed = 75.0
        self.waypoints = []
        self.lookAtWaypoints = True

    def setFwdSpeed(self, spd):
        self.fwdSpeed = spd

    def setRotSpeed(self, spd):
        self.rotSpeed = spd

    def addWaypoints(self, waypoints):
        self.waypoints += waypoints
    
    def setWaypoints(self, waypoints):
        self.waypoints = waypoints

    def getWaypoints(self):
        return self.waypoints

    def clearWaypoints(self):
        self.waypoints = []

    def cleanup(self):
        self.stopMotor()
        del self.node
        del self.task
        del self.fwdSpeed
        del self.rotSpeed
        del self.waypoints

    def startMotor(self):
        self.stopMotor()

        self.task = taskMgr.add(self.__update, "MotorUpdate-" + str(id(self)))

    def stopMotor(self):
        if self.task:
            self.task.remove()
            self.task = None

    def __update(self, task):
        if len(self.waypoints) == 0:
            return task.cont

        dt = globalClock.getDt()

        # Step towards goal waypoint
        waypoint = self.waypoints[0]
        currPos = self.node.getPos(render)
        delta = waypoint - currPos
        # Distance from here to waypoint
        ooLen = delta.lengthSquared()
        dir = delta.normalized()
        moveAmount = (dir * self.fwdSpeed) * dt

        if moveAmount.lengthSquared() >= ooLen:
            # We would move past our waypoint
            # snap to the waypoint, then complete this waypoint
            self.node.setPos(waypoint)
            self.waypoints.pop(0)

            # Look at the new waypoint
            if len(self.waypoints) > 0 and self.lookAtWaypoints:
                self.node.makeIdealYaw(self.waypoints[0])
        else:
            self.node.setPos(currPos + moveAmount)

        return task.cont
