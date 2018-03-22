from direct.fsm.FSM import FSM
from direct.gui.DirectGui import *
from panda3d.core import *
from direct.gui.OnscreenImage import OnscreenImage
import sys
from SplitScreenwithController import *
from direct.showbase.ShowBase import ShowBase

class AppState(FSM):

	def enterMenu(self):

		self.image = OnscreenImage(image="images/startmenu.jpg", pos=(0,0,0), scale=(2.3,2.3,1))
		self.intruction = None

		self.StartBtn = DirectButton(text = "Start",
									 scale = 0.12, 
									 pos = Vec3(0, 0, -0.5),
									 command = self.request,
									 extraArgs = ["Start"])

		self.InstructionsBtn = DirectButton(text = "Instructions",
									  scale = 0.1, 
									  pos = Vec3(0, 0, -0.65),
									  command = self.request,
									  extraArgs = ["Instructions"])

		self.QuitBtn = DirectButton(text = "Quit",
									scale = 0.1,
									pos = Vec3(0,0,-.8),
									command = self.request,
									extraArgs = ["Quit"])
		

	def exitMenu(self):
		self.StartBtn.destroy()
		self.InstructionsBtn.destroy()
		self.QuitBtn.destroy()
		self.image.destroy()


	def enterStart(self):
		self.game = FoxTrail()

	
	def enterInstructions(self):
		self.image = OnscreenImage(image="images/Instructions.jpg", pos=(0,0,0), scale=(1.4,1.4,1))
		self.menuBtn = DirectButton(text = "Menu",
									scale = 0.1, 
									pos = Vec3(0, 0, -0.8),
									command = self.request,
									extraArgs = ["Menu"])
	def exitInstructions(self):
		self.menuBtn.destroy()
		self.image.destroy()
	
	def enterQuit(self):
		sys.exit()

