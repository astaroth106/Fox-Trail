# Author: Ryan Myers
# Models: Jeff Styers, Reagan Heller


# Last Updated: 6/13/2005
#
# This tutorial provides an example of creating a character
# and having it walk around on uneven terrain, as well
# as implementing a fully rotatable camera.

#for directx window and functions
import direct.directbase.DirectStart
#for most bus3d stuff
from pandac.PandaModules import *
#for directx object support
from direct.showbase.DirectObject import DirectObject
#for intervals
from direct.interval.IntervalGlobal import *
#for FSM
from direct.fsm import FSM
from direct.fsm import State
#for tasks
from direct.task import Task
#for Actors
from direct.actor.Actor import Actor
#for math
import math
#for system commands
import random, sys, os, math
#for directGUI
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText

#for Pandai
from panda3d.ai import *

#************************GLOBAL**********************************************
speed = 0.75

# Figure out what directory this program is in.
MYDIR=os.path.abspath(sys.path[0])
MYDIR=Filename.fromOsSpecific(MYDIR).getFullpath()

tiles = []

font = loader.loadFont("cmss12")

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1), font = font,
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1), font = font,
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)

class World(DirectObject):

    def __init__(self):
        
        self.keyMap = {"left":0, "right":0, "up":0, "down":0}
        
        self.title = addTitle("Testing Map Editor - Grid System")
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[Enter]: Start Pathfinding")
        self.inst21 = addInstructions(0.85, "[Arrow Keys]: Move Arrow")
        # self.inst3 = addInstructions(0.80, "[1]: Small box")
        # self.inst4 = addInstructions(0.75, "[2]: Big box")
        # self.inst5 = addInstructions(0.70, "[Space]: Place box")
        
        #base.disableMouse()
        base.cam.setPosHpr(0,-200,350,0,300,0)
        self.box = 0
        self.pointer_move = False
        
        self.loadModels()
        self.setAI()
       
    def loadModels(self):

        # self.environ1 = loader.loadModel("models/skydome")
        # self.environ1.reparentTo(render)
        # self.environ1.setPos(0,0,0)
        # self.environ1.setScale(1)
        #
        # self.environ2 = loader.loadModel("models/skydome")
        # self.environ2.reparentTo(render)
        # self.environ2.setP(180)
        # self.environ2.setH(270)
        # self.environ2.setScale(1)
        #
        # self.environ = loader.loadModel("models/groundPlane")
        # self.environ.reparentTo(render)
        # self.environ.setPos(0, 0, 0)
        # self.environ.setScale(.1)

        # x = 11
        # y = 11
        # file = open('maps/map1.txt', 'r')
        # lines = (line.rstrip('\n') for line in open('maps/map1.txt'))
        lines = []
        with open("maps/map1.txt", mode="r") as my_file:
            for line in my_file:
                lines.append(line)
                #print(line.rstrip("\n"))
        self.size = int(lines[0])+1
        self.Matrix = [[0 for x in range(self.size+1)] for y in range(self.size+1)]
        self.Matrix1 = [[0 for x in range(self.size+1)] for y in range(self.size+1)]

        #print self.size


        #self.size = 10
        # self.Matrix = [[0 for x in range(self.size+1)] for y in range(self.size+1)]
        
        # **BUILD WALL**
        for i in range(0, self.size+1):
            j = 0
            self.Matrix1[i][j] = loader.loadModel("models/box")
            self.Matrix1[i][j].setScale(1)
            self.Matrix1[i][j].reparentTo(render)
            self.Matrix1[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)

        for i in range(0, self.size+1):
            j = self.size
            self.Matrix1[i][j] = loader.loadModel("models/box")
            self.Matrix1[i][j].setScale(1)
            self.Matrix1[i][j].reparentTo(render)
            self.Matrix1[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)

        for j in range(1, self.size):
            i = 0
            self.Matrix1[i][j] = loader.loadModel("models/box")
            self.Matrix1[i][j].setScale(1)
            self.Matrix1[i][j].reparentTo(render)
            self.Matrix1[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)

        for j in range(1, self.size):
            i = self.size
            self.Matrix1[i][j] = loader.loadModel("models/box")
            self.Matrix1[i][j].setScale(1)
            self.Matrix1[i][j].reparentTo(render)
            self.Matrix1[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)


        # BUILD MAP from file:
        m = 1
        n = 1
        for l in lines:
            if l[0].isdigit(): pass
            else:
                for c in l:
                    if c == "#":
                        self.Matrix[m][n] = 0
                    elif c == "@":
                        self.Matrix[m][n] = 1
                    n = n + 1
                n = 1
                m = m + 1
            print l

        #print self.Matrix
        # obstacles -- need to add collision...
        #tile = self.environ
        # self.boxx = loader.loadModel("models/box")
        # tex = loader.loadTexture("Texture/stone_text.jpg")
        # self.boxx.setTexture(tex)
        # self.boxx.setScale(1)
        # self.boxx.reparentTo(render)
        # self.boxx.setPos(-70+15, -80+15, 0)
        for i in range(1, self.size):
            for j in range(1, self.size):
                if self.Matrix[i][j] == 0:
                    self.Matrix1[i][j] = loader.loadModel("models/groundPlane")
                    tex = loader.loadTexture("Texture/grass_t.png")
                    self.Matrix1[i][j].setTexture(tex)
                    self.Matrix1[i][j].setScale(.15)
                    self.Matrix1[i][j].reparentTo(render)
                    self.Matrix1[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)
                elif self.Matrix[i][j] == 1:
                    self.Matrix1[i][j] = loader.loadModel("models/box")
                    tex = loader.loadTexture("Texture/stone_text.jpg")
                    self.Matrix1[i][j].setTexture(tex)
                    self.Matrix1[i][j].setScale(1)
                    self.Matrix1[i][j].reparentTo(render)
                    self.Matrix1[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)
                # if i%2 == 0 and j%2 == 0:
                #     self.Matrix[i][j] = loader.loadModel("models/box")
                #     tex = loader.loadTexture("Texture/stone_text.jpg")
                #     self.Matrix[i][j].setTexture(tex)
                #     self.Matrix[i][j].setScale(1)
                #     self.Matrix[i][j].reparentTo(render)
                #     self.Matrix[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)
        # for i in range(1, self.size):
        #     for j in range(1, self.size):
                
        #         self.Matrix[i][j] = loader.loadModel("models/groundPlane")
        #         tex = loader.loadTexture("Texture/grass_t.png")
        #         self.Matrix[i][j].setTexture(tex)
        #         self.Matrix[i][j].setScale(.15)
        #         self.Matrix[i][j].reparentTo(render)
        #         self.Matrix[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)
        #         if i%2 == 0 and j%2 == 0:
        #             self.Matrix[i][j] = loader.loadModel("models/box")
        #             tex = loader.loadTexture("Texture/stone_text.jpg")
        #             self.Matrix[i][j].setTexture(tex)
        #             self.Matrix[i][j].setScale(1)
        #             self.Matrix[i][j].reparentTo(render)
        #             self.Matrix[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)
                # elif random.randint(0, self.size) > self.size/2:
                #     for x in range(15):
                #         if i > 1 or j > 1:
                #             self.Matrix[i][j] = loader.loadModel("models/box")
                #             tex = loader.loadTexture("Texture/woodceiling.jpg")
                #             self.Matrix[i][j].setTexture(tex)
                #             self.Matrix[i][j].setScale(1)
                #             self.Matrix[i][j].reparentTo(render)
                #             self.Matrix[i][j].setPos(-70 + i * 14.5, -80 + j * 14.5, 0)

        # Create the main character, Ralph

        #ralphStartPos = self.environ.find("**/start_point").getPos()
        ralphStartPos = Vec3(-51,-64,0)
        self.ralph = Actor("models/ralph",
                                 {"run":"models/ralph-run",
                                  "walk":"models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setScale(2)
        self.ralph.setPos(ralphStartPos)
        
        self.pointer = loader.loadModel("models/arrow")
        self.pointer.setColor(1,0,0)
        self.pointer.setPos(60,-60,0)
        self.pointer.setScale(3)
        self.pointer.reparentTo(render)

    def setAI(self):
        #Creating AI World
        self.AIworld = AIWorld(render)
        
        self.accept("enter", self.setMove)
        #self.accept("1", self.addBlock)
        #self.accept("2", self.addBigBlock)
        #self.accept("space", self.addStaticObstacle)
        
        #movement
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["up",1])
        self.accept("arrow_down", self.setKey, ["down",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["up",0])
        self.accept("arrow_down-up", self.setKey, ["down",0])
        
        self.AIchar = AICharacter("ralph",self.ralph, 60, 0.05, 15)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()
        
        self.AIbehaviors.initPathFind("models/navmesh.csv")
        
        #AI World update        
        taskMgr.add(self.AIUpdate,"AIUpdate")
        
        #movement task
        taskMgr.add(self.Mover,"Mover")
        
        self.dirnlight1 = DirectionalLight("dirn_light1")
        self.dirnlight1.setColor(Vec4(1.0,1.0,1.0,1.0))
        self.dirnlightnode1 = render.attachNewNode(self.dirnlight1)
        self.dirnlightnode1.setHpr(0,317,0)
        render.setLight(self.dirnlightnode1)
        
    def setMove(self):
        self.AIbehaviors.pathFindTo(self.pointer)
        self.ralph.loop("run")
    
    def addBlock(self):
        self.pointer_move = True
        self.box = loader.loadModel("models/box")
        self.box.setPos(0,-60,0)
        self.box.setScale(1)
        self.box.reparentTo(render)
        
    def addBigBlock(self):
        self.pointer_move = True
        self.box = loader.loadModel("models/box")
        self.box.setPos(0,-60,0)
        self.box.setScale(2)
        self.box.setColor(1,1,0)
        self.box.reparentTo(render)
    
    def addStaticObstacle(self):
        if(self.box!=0):
            self.AIbehaviors.addStaticObstacle(self.box)
            self.box = 0
            self.pointer_move = False
            
    #to update the AIWorld    
    def AIUpdate(self,task):
        self.AIworld.update()
        #if(self.AIbehaviors.behaviorStatus("pathfollow") == "done"):
            #self.ralph.stop("run")
            #self.ralph.pose("walk", 0)
            
        return Task.cont
    
    def setKey(self, key, value):
        self.keyMap[key] = value
        
    def Mover(self,task):
        startPos = self.pointer.getPos()
        if (self.keyMap["left"]!=0):
            self.pointer.setPos(startPos + Point3(-speed,0,0))
        if (self.keyMap["right"]!=0):
            self.pointer.setPos(startPos + Point3(speed,0,0))
        if (self.keyMap["up"]!=0):
            self.pointer.setPos(startPos + Point3(0,speed,0))
        if (self.keyMap["down"]!=0):
            self.pointer.setPos(startPos + Point3(0,-speed,0))
            
        if(self.pointer_move == True and self.box != 0):
            self.box.setPos(self.pointer.getPos())
                
        return Task.cont


w = World()
base.run()

