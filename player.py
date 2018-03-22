from XboxInputHandler import *
import sys, os
from contextlib import contextmanager

class playerControl():
	def __init__(self, player, controller, keyMap, camera, floater, playerNum):
		self.player = player
		self.controller = controller
		self.keyMap = keyMap
		self.camera = camera
		self.floater = floater
		self.isMoving = False
		self.playerNum = playerNum
		self.run = False
		self.delta = 0

		
	def move(self):
		elapsed = globalClock.getDt()
		
		turnRightAmount = 0
		turnUpAmmount = 0
		forwardMove = 0
		rightMove = 0
		i = self.playerNum
		
		pygame.event.pump()
		
		if pygame.joystick.get_count() != 0 and self.controller != None and i < pygame.joystick.get_count():
			self.controller.state.update()
		
			lx, ly = self.controller.state.leftStick.getX(), self.controller.state.leftStick.getY()
			rx, ry = self.controller.state.rightStick.getX(), self.controller.state.rightStick.getY()
		else:
			lx, ly = (self.keyMap["right"] - self.keyMap["left"]), -(self.keyMap["forward"] -0.6 * self.keyMap["backward"])
			rx, ry = self.keyMap["turnRight"] - self.keyMap["turnLeft"], -(self.keyMap["turnUp"]-self.keyMap["turnDown"])
			
		if rx < -0.3 or rx > 0.3:
			turnRightAmount = rx
		if ry < -0.3 or ry > 0.3:
			turnUpAmmount = -ry
		
		
		turnRightAmount*=elapsed*100
		
		if self.camera.getP() < 75 and self.camera.getP() > -72:
			pass#turnUpAmmount*=elapsed*100

		self.player.setH(self.player.getH() - turnRightAmount)
		
		if self.camera.getP() < 75 and self.camera.getP() > -72:
			pass#self.camera.setP(self.camera.getP() + turnUpAmmount)
		elif self.camera.getP() < 17:
			self.camera.setP(-71.99)
		elif self.camera.getP() > -72:
			self.camera.setP(74.99)

		startpos = self.player.getPos()

		if ly < -0.5 or ly > 0.5:
			forwardMove = -ly
		if lx < -0.5 or lx > 0.5:
			rightMove = .5*lx

		# Slow forward when moving diagonal
		forwardMove *= 1.0 - abs(rightMove)
		
		speed=1+1.10*self.run
		
		if self.run:
			self.delta += elapsed
			if self.delta > 4:
				self.run = False
				self.delta = 0

		rightMove*=speed
		forwardMove*=speed

		self.player.setX(self.player, -elapsed * 3 * rightMove)
		self.player.setY(self.player, -elapsed * 3 * forwardMove)

		def sign(n):
			if n >= 0: return 1
			return -1

		if rightMove or forwardMove:
			self.player.setPlayRate(forwardMove + abs(rightMove) * sign(forwardMove), 'run')
			if self.isMoving is False:
				self.player.loop("walk")
				self.isMoving = True
		else:
			if self.isMoving:
				self.player.stop()
				self.player.pose("walk", 1)
				self.isMoving = False
		
		if self.player.getZ() != 0:
			self.player.setZ(0)
				
		self.camera.setPos(self.floater, 0, 0, 0)
		self.camera.setPos(self.camera, 0, 0, 0)
