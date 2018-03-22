from KeyTrackerClass import *

mouseControl = False

class player(ShowBase, keyTracker):

    def __init__(self):
        ShowBase.__init__(self)
        keyTracker.__init__(self)

        self.player = Actor("panda", {"walk": "panda-walk"})
        self.player.reparentTo(render)

        self.camera = self.makeCamera(self.win)
        self.floater = NodePath(PandaNode("floater"))

        self.floater.reparentTo(self.player)

        self.floater.setZ(7.0)
        self.floater.setY(-5.0)



        #set up the camera
        self.disableMouse()
        camLen = self.camLens
        camLen.setNear(1)

        self.maxDist = 0
        self.camDist = 0.0

        self.isMoving = False

        camLen.setFar(self.maxDist * 20)
        self.cam.node().setLens(camLen)

        self.addKey("w", "forward")
        self.addKey("a", "left")
        self.addKey("s", "backward")
        self.addKey("d", "right")
        self.addKey("arrow_left", "turnLeft")
        self.addKey("arrow_right", "turnRight")
        self.addKey("arrow_down", "turnUp")

        self.setKey('zoom', 0)
        self.accept("wheel_up", self.setKey, ['zoom', 1])
        self.accept("wheel_down", self.setKey, ['zoom', -1])

        self. addKey("shift", "hyper")

        taskMgr.add(self.move, "moveTask")

        self.fire = 0

        self.nextLaser = 0.0
        self.Lasers = []

        self.camera.setH(180)
        base.camera.reparentTo(self.player)

        self.camera.setPos(self.floater, 0,0,0)
        self.camera.setPos(self.camera, 0 , -self.camDist, 0)


    def move(self, task):

        elapsed = globalClock.getDt()

        campos = self.camera.getPos()

        turnRightAmount = self.keyMap["turnRight"] - self.keyMap["turnLeft"]

        turnRightAmount *= elapsed * 100

        if mouseControl and base.mouseWatcherNode.hasMouse():

            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            deltaX = md.getX() - 200
            deltaY = md.getY() - 200

            base.win.movePointer(0,200,200)

            turnRightAmount += 0.2 * deltaX
        self.player.setH(self.player.getH() - turnRightAmount)

        startpos = self.player.getPos()

        forwardMove =self.keyMap["forward"] - .5 * self.keyMap["backward"]
        rightMove = .5 * (self.keyMap["right"] - self.keyMap["left"])

        forwardMove *= 1.0 - abs(rightMove)

        speed = 1 + 4 * self.keyMap["hyper"]

        rightMove *= speed
        forwardMove *= speed

        self.player.setX(self.player, -elapsed * 25 * rightMove)
        self.player.setY(self.player, -elapsed * 25 * forwardMove)

        def sign(n):
            if n >= 0 : return 1
            return -1

        if rightMove or forwardMove:
            self.player.setPlayRate(forwardMove + abs(rightMove) * sign(forwardMove), "run")
            if self.isMoving is False:
                self.player.loop("walk")

                self.isMoving = True
            else:
                if self.isMoving:
                    self.player.stop()
                    self.player.pose("walk", 5)
                    self.isMoving = False
            if self.player.getZ() >0:
                self.player.stop()
                self.player.pose("walk", 5)
                self.isMoving = False

            self.camera.setPos(self.floater,0,0,0)
            self.camera.setPos(self.camera,0,-self.camDist, 0)

            return Task.cont

    def setVelocity(self, obj, val):
        obj.setPythonTag("velocity", val)

    def getVelocity(self, obj):
        if obj.getPythonTag("velocity") is None:
            return LVector3(0,0,0)
        else:
            return obj.getPythonTag("velocity")

    def setExpires(self, obj, val):
        obj.setPythonTag("expires", val)

    def getExpires(self, obj, val):
        obj.setPythonTag("expires", val)

    def updatePos(self, obj, dt):
        vel = self.getVelocity(obj)
        newPos = obj.getPos() + (vel * dt)

        obj.setPos(newPos)


Demo = player()
Demo.run()