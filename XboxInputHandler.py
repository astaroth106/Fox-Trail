from panda3d.core import *
import pygame
import math, os, sys
from contextlib import contextmanager

class XboxControllerState:
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5
    BACK = 6
    START = 7
    LS = 8
    RS = 9

    def __init__(self, joy):
		self.joy = joy
		self.leftStick = Vec2()
		self.rightStick = Vec2()
		self.dpad = Vec2()
		self.triggers = 0.0
		self.buttons = [False] * self.joy.get_numbuttons()

    def update(self):
		self.leftStick.setX(self.joy.get_axis(0))
		self.leftStick.setY(self.joy.get_axis(1))
		self.rightStick.setX(self.joy.get_axis(4))
		self.rightStick.setY(self.joy.get_axis(3))
		self.triggers = self.joy.get_axis(2)

		for i in range(self.joy.get_numbuttons()):
			self.buttons[i] = self.joy.get_button(i)

class XboxOneControllerState:
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5
    BACK = 6
    START = 7
    LS = 8
    RS = 9

    def __init__(self, joy):
        self.joy = joy
        self.leftStick = Vec2()
        self.rightStick = Vec2()
        self.dpad = Vec2()
        self.triggers = 0.0
        self.buttons = [False] * self.joy.get_numbuttons()

    def update(self):
		self.leftStick.setX(self.joy.get_axis(0))
		self.leftStick.setY(self.joy.get_axis(1))
		self.rightStick.setX(self.joy.get_axis(5))
		self.rightStick.setY(self.joy.get_axis(4))
		self.triggers = -self.joy.get_axis(3)

        #for i in range(self.joy.get_numbuttons()):
        #    self.buttons[i] = self.joy.get_button(i)


class PhillipControllerState:
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5
    BACK = 6
    START = 7
    LS = 8
    RS = 9

    def __init__(self, joy):
		self.joy = joy
		self.leftStick = Vec2()
		self.rightStick = Vec2()
		self.dpad = Vec2()
		self.triggers = 0.0
		self.buttons = [False] * self.joy.get_numbuttons()

    def update(self):
		self.leftStick.setX(self.joy.get_axis(0))
		self.leftStick.setY(self.joy.get_axis(1))
		self.rightStick.setX(self.joy.get_axis(3))
		self.rightStick.setY(self.joy.get_axis(2))
		#self.triggers = self.joy.get_button(7)
		self.buttons[7] = self.joy.get_button(7)
		
		#for i in range(self.joy.get_numbuttons()):
		#	self.buttons[i] = self.joy.get_button(i)


class PS3ControllerState:
	A = 0
	B = 1
	X = 2
	Y = 3
	LB = 4
	RB = 5
	BACK = 6
	START = 7
	LS = 8
	RS = 9

	def __init__(self, joy):
		self.joy = joy
		self.leftStick = Vec2()
		self.rightStick = Vec2()
		self.dpad = Vec2()
		self.triggers = 0.0
		self.buttons = [False] * self.joy.get_numbuttons()

	def update(self):
		self.leftStick.setX(self.joy.get_axis(0))
		self.leftStick.setY(self.joy.get_axis(1))
		self.rightStick.setX(self.joy.get_axis(2))
		self.rightStick.setY(self.joy.get_axis(3))
		self.triggers = 0

		for i in range(self.joy.get_numbuttons()):
			self.buttons[i] = self.joy.get_button(i)




class ControllerHandler():
    def __init__(self, i):
		
        self.wasWalking = False
        self.wasReversing = False

        pygame.init()
        pygame.joystick.init() 
        joystick_count = pygame.joystick.get_count()
        if pygame.joystick.get_count() != 0:
			
			#for i in range(pygame.joystick.get_count()):
			joy = pygame.joystick.Joystick(i)
			name = joy.get_name()

			if "Xbox 360" in name or "XBOX 360" in name:
				joy.init()
				self.controller = joy
				self.state = XboxControllerState(joy)
			elif "PLAYSTATION(R)3 Controller" in name:
				joy.init()
				self.controller = joy
				self.state = PS3ControllerState(joy)
			elif "Xbox One For Windows" in name:
				joy.init()
				self.controller = joy
				self.state = XboxOneControllerState(joy)
			else:
				joy.init()
				self.controller = joy
				self.state = PhillipControllerState(joy)
				
