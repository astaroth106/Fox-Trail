from panda3d.core import *

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from math import sin, cos, pi
from XboxInputHandler import *

import sys

font = TextNode.getDefaultFont()
focus=NodePath("tilerFocuse")
mouseControl = False

SPRITE_POS = 55     # At default field of view and a depth of 55, the screen
# dimensions is 40x30 units
SCREEN_X = 20       # Screen goes from -20 to 20 on X
SCREEN_Y = 15       # Screen goes from -15 to 15 on Y
TURN_RATE = 360     # Degrees ship can turn in 1 second
ACCELERATION = 10   # Ship acceleration in units/sec/sec
MAX_VEL = 6         # Maximum ship velocity in units/sec
MAX_VEL_SQ = MAX_VEL ** 2  # Square of the ship velocity
DEG_TO_RAD = pi / 180  # translates degrees to radians for sin and cos
BULLET_LIFE = 2     # How long bullets stay on screen before removed
BULLET_REPEAT = .2  # How often bullets can be fired
BULLET_SPEED = 50   # Speed bullets move

class keyTracker(DirectObject):
    """
    Borrowed Class
    """
    def __init__(self):
        DirectObject.__init__(self)
        self.keyMap = {}

    def setKey(self, key, value):
        """Records the state of key"""
        self.keyMap[key] = value

    def addKey(self,key,name,allowShift=True):
        self.accept(key, self.setKey, [name,True])
        self.accept(key+"-up", self.setKey, [name,False])
        self.accept(key.upper()+"-up", self.setKey, [name,False])

        if allowShift:
            self.addKey("shift-"+key,name,False)

        self.keyMap[name]=False

def loadObject(tex=None, pos=LPoint3(0, 0), depth=SPRITE_POS, scale=1,
					   transparency=True, actor=None):

		obj = loader.loadModel("models/" + tex)
		obj.reparentTo(render)

		# Set the initial position and scale.
		obj.setPos(actor.getX(), actor.getZ(), actor.getY())
		obj.setScale(scale)

		# This tells Panda not to worry about the order that things are drawn in
		# (ie. disable Z-testing).  This prevents an effect known as Z-fighting.
		obj.setBin("unsorted", 0)
		obj.setDepthTest(False)

		"""if transparency:
			# Enable transparency blending.
			actor.setTransparency(TransparencyAttrib.MAlpha)

		if tex:
			# Load and set the requested texture.
			tex = loader.loadTexture("textures/" + tex)
			actor.setTexture(tex, 1)"""

		return obj


class Application(ShowBase, keyTracker):
	def __init__(self):

		ShowBase.__init__(self)
		keyTracker.__init__(self)
		# self.pandaActors = [Actor("panda", {"walk": "panda-walk"}), Actor("panda", {"walk": "panda-walk"}), Actor("panda", {"walk": "panda-walk"}), Actor("panda", {"walk": "panda-walk"})]

		self.player1 = Actor("panda", {"walk": "panda-walk"})
		self.player2 = Actor("panda", {"walk": "panda-walk"})
		self.player3 = Actor("panda", {"walk": "panda-walk"})
		self.player4 = Actor("panda", {"walk": "panda-walk"})

		self.player1.reparentTo(render)
		self.player2.reparentTo(render)
		self.player3.reparentTo(render)
		self.player4.reparentTo(render)

		self.player1.setPos(-50, 5, 0)
		self.player2.setPos(5, 5, 0)
		self.player3.setPos(15, 5, 0)
		self.player4.setPos(25, 5, 0)

		self.loadModels()

		self.setupCameras()

		# Set up the camera
		self.disableMouse()

		self.isMoving = False

		self.setupControls()
		self.xboxKeys = XboxControllerHandler()

		# Stores the time at which the next bullet may be fired.
		self.nextLaser = 0.0

		# This list will stored fired bullets.
		self.Lasers = []

	def makeRegion(self, cam, dimensions, color):

		region = cam.node().getDisplayRegion(0)
		region.setDimensions(dimensions.getX(), dimensions.getY(), dimensions.getZ(), dimensions.getW())
		region.setClearColorActive(True)
		aspect = float(region.getPixelWidth()) / float(region.getPixelHeight())
		cam.node().getLens().setAspectRatio(aspect)

	def setupHud(self):
		self.hud1 = OnscreenImage(image="images/bluec.png", pos=(-.7, 0, -.55), scale=(.1, .1, .1)).setTransparency(TransparencyAttrib.MAlpha)
		self.hb1 = OnscreenImage(image = "images/BlueHB_red.png", pos = (-1.05, 0 , -.1), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
		self.hud2 = OnscreenImage(image="images/greenc.png", pos=(-.7, 0, .55), scale=(.1, .1, .1)).setTransparency(TransparencyAttrib.MAlpha)
		self.hud3 = OnscreenImage(image="images/redc.png", pos=(.7, 0, -.55), scale=(.1, .1, .1)).setTransparency(TransparencyAttrib.MAlpha)
		self.hud4 = OnscreenImage(image="images/yellowc.png", pos=(.7, 0, .55), scale=(.1, .1, .1)).setTransparency(TransparencyAttrib.MAlpha)


	def move(self, task):

		elapsed = globalClock.getDt()

		turnRightAmount = 0
		turnUpAmmount = 0
		forwardMove = 0
		rightMove = 0

		pygame.event.pump()
		if pygame.joystick.get_count() != 0:
			self.xboxKeys.state.update()

			lx, ly = self.xboxKeys.state.leftStick.getX(), self.xboxKeys.state.leftStick.getY()
			rx, ry = self.xboxKeys.state.rightStick.getX(), self.xboxKeys.state.rightStick.getY()
		else:
			lx, ly = (self.keyMap["right"] - self.keyMap["left"]), -(self.keyMap["forward"] -0.6 * self.keyMap["backward"])
			rx, ry = self.keyMap["turnRight"] - self.keyMap["turnLeft"], self.keyMap["turnUp"]-self.keyMap["turnDown"]

		if rx < -0.3 or rx > 0.3:
			turnRightAmount = rx
		if ry < -0.3 or ry > 0.3:
			turnUpAmmount = ry

		turnRightAmount*=elapsed*100
		turnUpAmmount*=elapsed*100

		self.player1.setH(self.player1.getH() - turnRightAmount)
		base.camera.setP(base.camera.getP() + turnUpAmmount)

		startpos = self.player1.getPos()

		if ly < -0.5 or ly > 0.5:
			forwardMove = -ly
		if lx < -0.5 or lx > 0.5:
			rightMove = .5*lx

		# Slow forward when moving diagonal
		forwardMove *= 1.0 - abs(rightMove)

		self.player1.setX(self.player1, -elapsed * 25 * rightMove)
		self.player1.setY(self.player1, -elapsed * 25 * forwardMove)

		def sign(n):
			if n >= 0: return 1
			return -1

		if rightMove or forwardMove:
			self.player1.setPlayRate(forwardMove + abs(rightMove) * sign(forwardMove), 'run')
			if self.isMoving is False:
				self.player1.loop("walk")

				# self.ralph.loop("walk")
				self.isMoving = True
		else:
			if self.isMoving:
				self.player1.stop()
				self.player1.pose("walk", 5)
				self.isMoving = False
		if self.player1.getZ() > 0:
			self.player1.stop()
			self.player1.pose("walk", 5)
			self.isMoving = False

		self.cameras[0].setPos(self.floaters[0], 0, 0, 0)
		self.cameras[0].setPos(self.cameras[0], 0, 0, 0)

		return Task.cont

	def setVelocity(self, obj, val):

		obj.setPythonTag("velocity", val)

	def getVelocity(self, obj):

		if obj.getPythonTag("velocity") is None:
			return LVector3(0, 0, 0)
		else:
			return obj.getPythonTag("velocity")

	def setExpires(self, obj, val):

		obj.setPythonTag("expires", val)

	def getExpires(self, obj):

		return obj.getPythonTag("expires")

	def updatePos(self, obj, dt):

		vel = self.getVelocity(obj)
		newPos = obj.getPos() + (vel * dt)

		obj.setPos(newPos)

	def shoot(self, time):

		print self.player1.getH()
		direction = DEG_TO_RAD * self.player1.getH()
		pos = self.player1.getPos()
		laser = loadObject(tex="LaserProj", actor=self.player1)  # Create the object
		laser.setPos(pos)
		# Velocity is in relation to the ship
		vel = (self.getVelocity(self.player1) + (LVector3(sin(direction), -cos(direction), 0) * BULLET_SPEED))
		self.setVelocity(laser, vel)
		# print self.getVelocity(bullet)

		# Set the bullet expiration time to be a certain amount past the
		# current time
		self.setExpires(laser, time + BULLET_LIFE)

		# Finally, add the new bullet to the list
		self.Lasers.append(laser)

	def loadModels(self):

		self.Matrix = [[0 for x in range(11)] for y in range(11)]

		#     **BUILD WALL**
		for i in range(0, 10):
			j = 0
			self.Matrix[i][j] = loader.loadModel("models/box")
			self.Matrix[i][j].setScale(1)
			self.Matrix[i][j].reparentTo(render)
			self.Matrix[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)
		for j in range(1, 10):
			i = 0
			self.Matrix[i][j] = loader.loadModel("models/box")
			self.Matrix[i][j].setScale(1)
			self.Matrix[i][j].reparentTo(render)
			self.Matrix[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)

		for i in range(0, 10):
			j = 10
			self.Matrix[i][j] = loader.loadModel("models/box")
			self.Matrix[i][j].setScale(1)
			self.Matrix[i][j].reparentTo(render)
			self.Matrix[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)

		for j in range(0, 11):
			i = 10
			self.Matrix[i][j] = loader.loadModel("models/box")
			self.Matrix[i][j].setScale(1)
			self.Matrix[i][j].reparentTo(render)
			self.Matrix[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)

		# obstacles -- need to add collision...
		#tile = self.environ
		for i in range(1, 10):
			for j in range(1, 10):
				self.Matrix[i][j] = loader.loadModel("models/groundPlane")
				self.Matrix[i][j].setScale(.1)
				self.Matrix[i][j].reparentTo(render)
				self.Matrix[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)
				if i%2 == 0 and j%2 == 0:
					self.Matrix[i][j] = loader.loadModel("models/box")
					self.Matrix[i][j].setScale(1)
					self.Matrix[i][j].reparentTo(render)
					self.Matrix[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)
		# skybox
		self.skybox = loader.loadModel("models/skydome.egg")
		# make big enough to cover whole terrain, else there'll be problems with the water reflections
		self.skybox.setScale(10)
		self.skybox.setBin('background', 1)
		self.skybox.setDepthWrite(0)
		self.skybox.setLightOff()
		self.skybox.reparentTo(render)

		self.setupHud()


	def setupControls(self):
		self.keys = {"fire": 0}   # set fire flag to zero meaning they are not firing

		self.accept("escape", exit)
		self.accept("space", self.setKey, ["fire", 1]) #turn flag on

		self.addKey("w", "forward")
		self.addKey("a", "left")
		self.addKey("s", "backward")
		self.addKey("d", "right")
		self.addKey("arrow_left", "turnLeft")
		self.addKey("arrow_right", "turnRight")
		self.addKey("arrow_down", "turnDown")
		self.addKey("arrow_up", "turnUp")
		#self.addKey("space", "place")

		self.setKey('zoom', 0)
		self.accept("wheel_up", self.setKey, ['zoom', 1])
		self.accept("wheel_down", self.setKey, ['zoom', -1])

		self.addKey("shift", "hyper")

		taskMgr.add(self.move, "moveTask")

	def setupCameras(self):
		self.cam.node().getDisplayRegion(0).setActive(0)

		self.cameras = [self.makeCamera(self.win), self.makeCamera(self.win), self.makeCamera(self.win), self.makeCamera(self.win)]

		self.floaters = [NodePath(PandaNode("floater0")), NodePath(PandaNode("floater1")), NodePath(PandaNode("floater2")), NodePath(PandaNode("floater3"))]
		self.floaters[0].reparentTo(self.player1)
		self.floaters[1].reparentTo(self.player2)
		self.floaters[2].reparentTo(self.player3)
		self.floaters[3].reparentTo(self.player4)
		self.floaters[0].setZ(7.0)
		self.floaters[0].setY(-5.0)
		self.floaters[1].setZ(7.0)
		self.floaters[1].setY(-5.0)
		self.floaters[2].setZ(7.0)
		self.floaters[2].setY(-5.0)
		self.floaters[3].setZ(7.0)
		self.floaters[3].setY(-5.0)

		self.cameras[0].setH(180)
		self.cameras[1].setH(180)
		self.cameras[2].setH(180)
		self.cameras[3].setH(180)
		base.cameras[0].reparentTo(self.player1)
		base.cameras[1].reparentTo(self.player2)
		base.cameras[2].reparentTo(self.player3)
		base.cameras[3].reparentTo(self.player4)

		self.cameras[0].setPos(self.floaters[0], 0, 0, 0)
		self.cameras[0].setPos(self.cameras[0], 0, 0, 0)
		self.cameras[1].setPos(self.floaters[1], 0, 0, 0)
		self.cameras[1].setPos(self.cameras[1], 0, 0, 0)
		self.cameras[2].setPos(self.floaters[2], 0, 0, 0)
		self.cameras[2].setPos(self.cameras[2], 0, 0, 0)
		self.cameras[3].setPos(self.floaters[3], 0, 0, 0)
		self.cameras[3].setPos(self.cameras[3], 0, 0, 0)

		self.makeRegion(self.cameras[0], Vec4(0, 0.5, 0, 0.5), Vec4(1, 0, 0, 1))
		self.makeRegion(self.cameras[1], Vec4(0.5, 1, 0, 0.5), Vec4(0, 1, 0, 1))
		self.makeRegion(self.cameras[2], Vec4(0, 0.5, 0.5, 1), Vec4(0, 0, 1, 1))
		self.makeRegion(self.cameras[3], Vec4(0.5, 1, 0.5, 1), Vec4(0, 1, 1, 1))

		def makeRegion(self, cam, dimensions, color):

			region = cam.node().getDisplayRegion(0)
			region.setDimensions(dimensions.getX(), dimensions.getY(), dimensions.getZ(), dimensions.getW())
			region.setClearColorActive(True)
			aspect = float(region.getPixelWidth()) / float(region.getPixelHeight())
			cam.node().getLens().setAspectRatio(aspect)

if __name__ == "__main__":
    gameApp = Application()
    gameApp.run()
