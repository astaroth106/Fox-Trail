# Intro to 3d with Panda3d

import sys, random

from direct.showbase.ShowBase import ShowBase
from panda3d.core import LVector3

from panda3d.core import Light, DirectionalLight
from panda3d.core import CollisionNode, CollisionSphere, CollisionTube, CollisionBox
from panda3d.core import CollisionTraverser, CollisionHandlerPusher

SPEED = 5

# panda samples extend ShowBase to provide specific application
class TutorialGame(ShowBase):

	def __init__(self):
		# call superclass init (no implicit chaining)
		ShowBase.__init__(self)

		######### load player model
		self.player = loader.loadModel("panda")
		self.player.setScale(0.1)
		self.player.reparentTo(render)
		self.player.setY(10)

		######### move camera for tilted overhead view
		base.disableMouse()
		base.camera.setPos(0, -10, 10)
		base.camera.lookAt(self.player)

		######### load "obstacle" model
		self.obs = loader.loadModel("models/box")
		self.obs.setScale(0.1)

		# re-use same model for multiple objects
		self.OBS = []
		for i in range(0, 4):
			n = render.attachNewNode("Obstacle")
			self.obs.instanceTo(n)
			n.reparentTo(render)
			n.setPos(-1.5 + random.random() * 8.0, 8.5 + random.random() * 8.0, 0)
			self.OBS.append(n)

		######### add directional light
		dlight = DirectionalLight('dlight')
		dlight.setColor((1, 1, 1, 1))
		self.dlnp = render.attachNewNode(dlight)

		render.setLight(self.dlnp)
		dlight.setDirection(LVector3(-0.8, 0, 0))

		######### setup other systems
		self.setupInput()
		self.setupCollision()

		# pre-frame update
		taskMgr.add(self.update, "update")

    # helper for taking in input
	def setKey(self, key, value):
		self.keyMap[key] = value

	def setupInput(self):
		self.keyMap = {
			"left": 0, "right": 0, "fwd": 0, "back": 0}

		# this sets values in keyMap to True when keys are pressed
		self.accept("escape", sys.exit)
		self.accept("w", self.setKey, ["fwd", True])
		self.accept("a", self.setKey, ["left", True])
		self.accept("s", self.setKey, ["back", True])
		self.accept("d", self.setKey, ["right", True])
		
		# this sets values in keyMap to False when keys are released
		self.accept("w-up", self.setKey, ["fwd", False])
		self.accept("a-up", self.setKey, ["left", False])
		self.accept("s-up", self.setKey, ["back", False])
		self.accept("d-up", self.setKey, ["right", False])

	def setupCollision(self):
		cs = CollisionSphere(0, 0, 0, 10)
		cnodePath = self.player.attachNewNode(CollisionNode('cnode'))
		cnodePath.node().addSolid(cs)
		cnodePath.show()
		for o in self.OBS:
			ct = CollisionBox(0, 1 ,1, 0.5)
			cn = o.attachNewNode(CollisionNode('ocnode'))
			cn.node().addSolid(ct)
			cn.show()
		pusher = CollisionHandlerPusher()
		pusher.addCollider(cnodePath, self.player)
		self.cTrav = CollisionTraverser()
		self.cTrav.addCollider(cnodePath, pusher)
		self.cTrav.showCollisions(render)

	# move the player based on the keyMap input
	def update(self, task):
		dt = globalClock.getDt()

		# user input
		if self.keyMap["fwd"]:
			self.player.setY(self.player.getY() + SPEED * dt)
		if self.keyMap["back"]:
			self.player.setY(self.player.getY() - SPEED * dt)
		if self.keyMap["left"]:
			self.player.setX(self.player.getX() - SPEED * dt)
		if self.keyMap["right"]:
			self.player.setX(self.player.getX() + SPEED * dt)

		return task.cont

demo = TutorialGame()
demo.run()



