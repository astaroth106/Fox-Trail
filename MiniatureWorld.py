from panda3d.core import *

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from math import sin, cos, pi
from XboxInputHandler import *
from player import *
import random, sys, os, math
from panda3d.core import loadPrcFileData
 
#loadPrcFileData('', 'fullscreen true')

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


class Application(ShowBase, keyTracker):
    def __init__(self):
        
        ShowBase.__init__(self)
        keyTracker.__init__(self)
        self.player = [Actor("models/Sadlow", {"walk": "models/Sadlow-walk"}), Actor("models/Angrylow", {"walk": "models/Angrylow-walk"}), 
                                Actor("models/Normlow", {"walk": "models/Normlow-walk"})]
        
        self.arm = loader.loadModel("models/cannon")
        self.arm.reparentTo(self.player[0])
        self.arm1 = loader.loadModel("models/cannon")
        self.arm1.reparentTo(self.player[1])
        self.arm2 = loader.loadModel("models/cannon")
        self.arm2.reparentTo(self.player[2])
        
        self.shield = loader.loadModel("models/shield_powerup.bam")
        self.speed = loader.loadModel("models/speed_powerup.bam")
        self.marsh = loader.loadModel("models/health_powerup.bam")
        
        base.cTrav = CollisionTraverser()
        #base.cTrav.showCollisions(render)
        self.notifier = CollisionHandlerEvent()
        self.notifier.addInPattern("%fn-in-%in")
        self.accept("bullet-in-box", self.BulletBox)
        self.accept("bullet-in-player1", self.healthBar1)
        self.accept("bullet-in-player2", self.healthBar2)
        self.accept("bullet-in-player3", self.healthBar3)
        
        self.accept("health-in-player1", self.health1)
        self.accept("health-in-player2", self.health2)
        self.accept("health-in-player3", self.health3)
        
        self.accept("speed-in-player1", self.speed1)
        self.accept("speed-in-player2", self.speed2)
        self.accept("speed-in-player3", self.speed3)
        
        self.accept("shield-in-player1", self.CollisionDetect)
        self.accept("shield-in-player2", self.CollisionDetect)
        self.accept("shield-in-player3", self.CollisionDetect)
        
        self.shield.hprInterval(1.5, LPoint3(360, 0, 0)).loop()
        self.speed.hprInterval(1.5, LPoint3(360, 0, 0)).loop()
        self.marsh.setHpr(0, 0, 45)
        self.marsh.hprInterval(1.5, LPoint3(360, 0, 45)).loop()
        
        self.shield.setZ(5)
        self.speed.setZ(1.5)
        self.marsh.setZ(3.8)
        
        self.shield.setScale(1)
        self.speed.setScale(1)
        self.marsh.setScale(.3)
        
        self.fire = [0]

        self.nextBullet = [0.0, 0.0, 0.0]
        self.bullets = []

        pygame.init()
        pygame.joystick.init() 
        
        if pygame.joystick.get_count() > 0:
            self.numOfPlayers = pygame.joystick.get_count()
        else:
            self.numOfPlayers = 3
        
        for i in range(0, self.numOfPlayers):
            self.player[i].reparentTo(render)

        self.loadMap()
        
        self.health = [.422, .422, .422]
        #self.health2 = .422
        #self.health3 = .422

        self.setupCameras()
        
        # Set up the camera
        self.disableMouse()

        self.setupControls()
        
        self.foxes = [0 for x in range(self.numOfPlayers)]
        
        #change self.controllerKeys[i] to None is no controller is connected
        #for i in range(0, self.numOfPlayers):
        #    self.foxes[i] = playerControl(self.player[i], self.controllerKeys[i], self.keyMap, self.cameras[i], self.floaters[i], i)
        
        self.foxes[0] = playerControl(self.player[0], None, self.keyMap, self.cameras[0], self.floaters[0], 0)
        self.foxes[1] = playerControl(self.player[1], None, self.keyMap, self.cameras[1], self.floaters[1], 1)
        self.foxes[2] = playerControl(self.player[2], None, self.keyMap, self.cameras[2], self.floaters[2], 2)
            
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.1, .1, .1, 1))
        
        directionalLight2 = DirectionalLight("directionalLight")
        directionalLight2.setDirection((2, -2, -2))
        directionalLight2.setColor((1, 1, 1, 1))
        directionalLight2.setSpecularColor((0.055, 0.055, 0.055, 1))

        render.setLight(render.attachNewNode(ambientLight))
        
        render.setLight(render.attachNewNode(directionalLight2))
         
        # Directional light 02
        directionalLight = DirectionalLight('directionalLight')
        directionalLight.setColor(Vec4(0.4, 0.4, 0.4, 1))
        directionalLight.setSpecularColor((0.5, 0.5, 0.5, 1))
        directionalLightNP = render.attachNewNode(directionalLight)
        # This light is facing forwards, away from the camera.
        directionalLightNP.setHpr(0, -90, 0)
        render.setLight(directionalLightNP)
        directionalLightNP.setPos(0, 90, 0)
        directionalLightNP.setHpr(0, -45, 0)
        render.setLight(directionalLightNP)

        self.setupCollision()
        self.delta = 0


    def setfire(self, fire, value):
        self.fire[0] = value

    def makeRegion(self, cam, dimensions):
        region = cam.node().getDisplayRegion(0)
        region.setDimensions(dimensions.getX(), dimensions.getY(), dimensions.getZ(), dimensions.getW())
        aspect = float(region.getPixelWidth()) / float(region.getPixelHeight())
        cam.node().getLens().setAspectRatio(aspect)

    def setupModels(self):
        
        # HEALTH BARS, HOW DO THEY WORK?
        # Well, since panda is weird, a full health bar is not 100 pixel points as I would of wanted, its .422 for the image to be full,
        # so instead of doing 100 points health bar, we are doing .422/(100) points health bar, that means 10 points is technically .0422 in this case.
        # every damage is just divied by 100 in the scale .422... very simple.

        if self.numOfPlayers == 3:      
            OnscreenImage(image = "images/BlueFox/BlueFox_HBred.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            # p1_health = OnscreenImage(image= "images/Healthbar_green.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            p1_health = OnscreenImage(image= "images/Healthbar_green.png", pos = (-1-.1, 0 , .89), scale = (.422,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/BlueFox/BlueFox_HB.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/Healthbar_reflection.png",pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)

            OnscreenImage(image = "images/RedFox/RedFox_HBred.png", pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            # p2_health = OnscreenImage(image= "images/Healthbar_green.png", pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            p2_health = OnscreenImage(image= "images/Healthbar_green.png", pos = (.3-.1, 0 , .89), scale = (.422,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/RedFox/RedFox_HB.png",pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/Healthbar_reflection.png",pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)

            OnscreenImage(image = "images/GreenFox/GreenFox_HBred.png", pos = (-1, 0 , -.12), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            #p3_health = OnscreenImage(image= "images/Healthbar_green.png",pos = (-1, 0 , -.12), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            p3_health = OnscreenImage(image= "images/Healthbar_green.png",pos = (-1-.1, 0 , -.12), scale = (.422,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/GreenFox/GreenFox_HB.png", pos = (-1, 0 , -.12), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/Healthbar_reflection.png",pos = (-1, 0 , -.12), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)

            OnscreenImage(image="images/BlueFox/bluec.png", pos=(-.7, 0, .55), scale=(.1, .1, .1)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image="images/RedFox/redc.png", pos=(.7, 0, .55), scale=(.1, .1, .1)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image="images/GreenFox/greenc.png", pos=(-.7, 0, -.55), scale=(.1, .1, .1)).setTransparency(TransparencyAttrib.MAlpha)
           
        elif self.numOfPlayers == 2:
            OnscreenImage(image = "images/BlueFox/BlueFox_HBred.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            #p1_health = OnscreenImage(image= "images/Healthbar_green.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            p1_health = OnscreenImage(image= "images/Healthbar_green.png", pos = (-1-.1, 0 , .89), scale = (.422,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/BlueFox/BlueFox_HB.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/Healthbar_reflection.png",pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)

            OnscreenImage(image = "images/RedFox/RedFox_HBred.png", pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            #p2_health = OnscreenImage(image= "images/Healthbar_green.png", pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            p2_health = OnscreenImage(image= "images/Healthbar_green.png", pos = (.3-.1, 0 , .89), scale = (.422,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/RedFox/RedFox_HB.png",pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/Healthbar_reflection.png",pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)

            OnscreenImage(image="images/BlueFox/bluec.png", pos=(-.7, 0, .55), scale=(.1, .1, .1)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image="images/RedFox/redc.png", pos=(.7, 0, .55), scale=(.1, .1, .1)).setTransparency(TransparencyAttrib.MAlpha)
           
        else:
            OnscreenImage(image = "images/BlueFox/BlueFox_HBred.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            #p1_health = OnscreenImage(image= "images/Healthbar_green.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            p1_health = OnscreenImage(image= "images/Healthbar_green.png", pos = (-1-.1, 0 , .89), scale = (.422,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/BlueFox/BlueFox_HB.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/Healthbar_reflection.png",pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image="images/BlueFox/bluec.png", pos=(-.7, 0, .55), scale=(.1, .1, .1)).setTransparency(TransparencyAttrib.MAlpha)
            
    def move(self, task):

        elapsed = globalClock.getDt()
        for i in range(0, self.numOfPlayers):
            self.foxes[i].move()
            
            #if self.foxes[i].controller.state.triggers  <= -0.9 and task.time > self.nextBullet:
            #if (self.foxes[i].controller.state.buttons[7] == 1 or self.foxes[i].controller.state.triggers  <= -0.5) and task.time > self.nextBullet[i]:
            if self.fire[0] == 1 and task.time > self.nextBullet[i]: 
				if self.health[i] > 0:
					#print "shooting"
					self.shoot(task.time, self.player[i])  # If so, call the shoot function
					# And disable shooting for a bit
					self.nextBullet[i] = task.time + BULLET_REPEAT

            self.fire[0] = 0

            newBulletArray = []
            for obj in self.bullets:
                self.updatePos(obj, elapsed)  # Update the bullet
                # Bullets have an experation time (see definition of fire)
                # If a bullet has not expired, add it to the new bullet list so
                # that it will continue to exist.
                if self.getExpires(obj) > task.time:
                    newBulletArray.append(obj)

                else:
                    obj.removeNode()  # Otherwise, remove it from the scene.
            # Set the bullet array to be the newly updated array
            self.bullets = newBulletArray
           
            i = random.randint(1, self.size-1)
            j = random.randint(1, self.size-1)
            k = random.randint(1, 10)
            self.delta+=elapsed
            
            if self.Matrix[i][j] == 0 and self.delta >=10:
                if k <= 6:
                    self.marsh.reparentTo(render)
                    self.marsh.setX(-70 + i * 14.5)
                    self.marsh.setY( -80 + j * 14.5)
                elif k > 6 and k <= 8:
                    self.speed.reparentTo(render)
                    self.speed.setX(-70 + i * 14.5)
                    self.speed.setY( -80 + j * 14.5)
                else:
                    self.shield.reparentTo(render)
                    self.shield.setX(-70 + i * 14.5)
                    self.shield.setY( -80 + j * 14.5)
                self.delta = 0
            
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

    def shoot(self, time, player):
        #for i in range(0,self.numOfPlayers):
        direction = DEG_TO_RAD * player.getH()
        bullet = loader.loadModel("models/icosphere")
        bullet.setScale(0.1)
        bullet.reparentTo(render)

        bullet.setPos(player.getX(), player.getY(), 0.5)
        # Velocity is in relation to the ship
        vel = (self.getVelocity(player) + (LVector3(sin(direction), -cos(direction), 0) * BULLET_SPEED))
        self.setVelocity(bullet, vel)
        # print self.getVelocity(bullet)
        # Set the bullet expiration time to be a certain amount past the
        # current time
        self.setExpires(bullet, time + BULLET_LIFE)

        # Finally, add the new bullet to the list
        self.bullets.append(bullet)

        col = bullet.attachNewNode(CollisionNode("bullet"))
        col.node().addSolid(CollisionSphere(0,0,0,1.1))
        #col.show()
        base.cTrav.addCollider(col, self.notifier)

    def BulletBox(self, entry):
        bullet = entry.getFrom()
        #print bullet

    def CollisionDetect(self, entry):
        pass#print "collision"
    def healthBar1(self, entry): 
        #print entry
        if self.health[0] > 0:
            self.health[0] -= .422/10
            print "Player1 got hit, Health1: " + str(self.health[0])
            OnscreenImage(image = "images/BlueFox/BlueFox_HBred.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image= "images/Healthbar_green.png", pos = (-1-.1, 0 , .89), scale = (self.health[0],.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/BlueFox/BlueFox_HB.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/Healthbar_reflection.png",pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        else:
            print "Player1 was Killed!"
            self.player[0].detachNode()
            OnscreenImage(image = "images/GameOver_Blue.png", pos =(-0.7, 0, 0.5), scale = (0.7, 0.5, 0.5)).setTransparency(TransparencyAttrib.MAlpha)
            # remove player.
        
    def healthBar2(self, entry): 
        #print entry
        if self.health[1] > 0:
            self.health[1] -= .422/10
            print "Player2 got hit, Health2: " + str(self.health[1])
            OnscreenImage(image = "images/RedFox/RedFox_HBred.png", pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image= "images/Healthbar_green.png", pos = (.3-.1, 0 , .89), scale = (self.health[1],.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/RedFox/RedFox_HB.png",pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/Healthbar_reflection.png",pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        else:
            print "Player2 was Killed!"
            self.player[1].detachNode()
            OnscreenImage(image = "images/GameOver_Red.png", pos =(0.7, 0, 0.5), scale = (0.7, 0.5, 0.5)).setTransparency(TransparencyAttrib.MAlpha)
            # remove player.
    def healthBar3(self, entry): 
        #print entry
        if self.health[2] > 0:
            self.health[2] -= .422/10
            print "Player3 got hit, Health3: " + str(self.health[2])
            OnscreenImage(image = "images/GreenFox/GreenFox_HBred.png", pos = (-1, 0 , -.12), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image= "images/Healthbar_green.png",pos = (-1-.1, 0 , -.12), scale = (self.health[2],.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/GreenFox/GreenFox_HB.png", pos = (-1, 0 , -.12), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
            OnscreenImage(image = "images/Healthbar_reflection.png",pos = (-1, 0 , -.12), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        else:
            print "Player3 was Killed!"
            self.player[2].detachNode()
            OnscreenImage(image = "images/GameOver_Green.png", pos =(-0.7, 0, -0.5), scale = (0.7, 0.5, 0.5)).setTransparency(TransparencyAttrib.MAlpha)
            # remove player

    def health1(self, entry):
        self.marsh.detachNode()
        if self.health[0] <= 0.3798: 
            self.health[0] += .422/10
        else:
            self.health[0] = .422
        print "Player1 recover, Health1: " + str(self.health[0])
        OnscreenImage(image = "images/BlueFox/BlueFox_HBred.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        OnscreenImage(image= "images/Healthbar_green.png", pos = (-1-.1, 0 , .89), scale = (self.health[0],.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        OnscreenImage(image = "images/BlueFox/BlueFox_HB.png", pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        OnscreenImage(image = "images/Healthbar_reflection.png",pos = (-1, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        
    def health2(self, entry):
        self.marsh.detachNode()
        if self.health[1] <= 0.3798: 
            self.health[1] += .422/10
        else:
            self.health[1] = .422
        print "Player2 recover, Health2: " + str(self.health[1])
        OnscreenImage(image = "images/RedFox/RedFox_HBred.png", pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        OnscreenImage(image= "images/Healthbar_green.png", pos = (.3-.1, 0 , .89), scale = (self.health[1],.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        OnscreenImage(image = "images/RedFox/RedFox_HB.png",pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        OnscreenImage(image = "images/Healthbar_reflection.png",pos = (.3, 0 , .89), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        
    def health3(self, entry):
        self.marsh.detachNode()
        if self.health[2] <= 0.3798: 
            self.health[2] += .422/10
        else:
            self.health[2] = .422
        print "Player3 recover hit, Health3: " + str(self.health[2])
        OnscreenImage(image = "images/GreenFox/GreenFox_HBred.png", pos = (-1, 0 , -.12), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        OnscreenImage(image= "images/Healthbar_green.png",pos = (-1-.1, 0 , -.12), scale = (self.health[2],.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        OnscreenImage(image = "images/GreenFox/GreenFox_HB.png", pos = (-1, 0 , -.12), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        OnscreenImage(image = "images/Healthbar_reflection.png",pos = (-1, 0 , -.12), scale = (.3,.3,.13)).setTransparency(TransparencyAttrib.MAlpha)
        
    def speed1(self, entry):
        print "speed for 1"
        self.speed.detachNode()
        self.foxes[0].run = True
    
    def speed2(self, entry):
        print "speed for 1"
        self.speed.detachNode()
        self.foxes[1].run = True
    
    def speed3(self, entry):
        print "speed for 1"
        self.speed.detachNode()
        self.foxes[2].run = True
        
    def shield1(self, entry):
        print "shield for 1"
    
    def shield2(self, entry):
        print "shield for 1"
   
    def shield3(self, entry):
        print "shield for 1"
    
    def loadMap(self):
		# fileslist = {"maps/map1.txt","maps/map2.txt","maps/map3.txt"}
		lines = []
		if os.path.exists("maps/map1.txt"):
			with open("maps/map1.txt", mode="r") as my_file:
				self.maploaded = True
				for line in my_file:
					lines.append(line)
			#print(line.rstrip("\n"))
			self.size = int(lines[0])+1
		else:
			self.size = 10
			self.maploaded = False

		self.Matrix = [[0 for x in range(self.size+1)] for y in range(self.size+1)]
		#self.Matrix1 = [[0 for x in range(self.size+1)] for y in range(self.size+1)]
		#
		if self.maploaded:
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
						elif c == "1":
							self.Matrix[m][n] = 10
						elif c == "2":
							self.Matrix[m][m] = 20
						elif c == "3":
							self.Matrix[m][n] = 30
						n = n + 1
					n = 1
					m = m + 1
				print l
		self.obs = loader.loadModel("models/crate.bam")
		self.tex = loader.loadTexture("Texture/woodencrate_front.png")
		self.ground = loader.loadModel("models/groundplane.bam")
		self.ground.setScale(.15/8)
		self.obs.setScale(0.5)
		self.obs.setTexture(self.tex)

		self.OBS = []

		#     **BUILD WALL**
		for i in range(0, self.size+1):
			j = 0
			n = render.attachNewNode("Obstacle")
			self.obs.instanceTo(n)
			n.reparentTo(render)
			n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 7.3/8)
			self.OBS.append(n)

		for i in range(0, self.size+1):
			j = self.size
			n = render.attachNewNode("Obstacle")
			self.obs.instanceTo(n)
			n.reparentTo(render)
			n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 7.3/8)
			self.OBS.append(n)

		for j in range(1, self.size):
			i = 0
			n = render.attachNewNode("Obstacle")
			self.obs.instanceTo(n)
			n.reparentTo(render)
			n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 7.3/8)
			self.OBS.append(n)

		for j in range(1, self.size):
			i = self.size
			n = render.attachNewNode("Obstacle")
			self.obs.instanceTo(n)
			n.reparentTo(render)
			n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 7.3/8)
			self.OBS.append(n)

		# map loaded:
		if self.maploaded:
			for i in range(1, self.size):
				for j in range(1, self.size):
					if self.Matrix[i][j] == 0:
						n = render.attachNewNode("Ground")
						self.ground.instanceTo(n)
						n.reparentTo(render)
						n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 0)
					elif self.Matrix[i][j] == 1:
						n = render.attachNewNode("Obstacle")
						self.obs.instanceTo(n)
						n.reparentTo(render)
						n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 7.3/8)
						self.OBS.append(n)
					elif self.Matrix[i][j] == 10:
						n = render.attachNewNode("Ground")
						self.ground.instanceTo(n)
						n.reparentTo(render)
						n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 0)
						self.player[0].setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 0)
					elif self.Matrix[i][j] == 20:
						n = render.attachNewNode("Ground")
						self.ground.instanceTo(n)
						n.reparentTo(render)
						n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 0)
						self.player[1].setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 0)
					elif self.Matrix[i][j] == 30:
						n = render.attachNewNode("Ground")
						self.ground.instanceTo(n)
						n.reparentTo(render)
						n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 0)
						self.player[2].setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 0)
		else: # if map was not loaded from file, then we load default
			for i in range(1, self.size):
				for j in range(1, self.size):
					n = render.attachNewNode("Ground")
					self.ground.instanceTo(n)
					n.reparentTo(render)
					n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 0)
					if i%2 == 0 and j%2 == 0:
						n = render.attachNewNode("Obstacle")
						self.obs.instanceTo(n)
						n.reparentTo(render)
						n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 7.3/8)
						self.OBS.append(n)
					elif random.randint(0, self.size) > self.size/2: # UNCOMMENT THIS SECTION to add random boxes to the map
					   for x in range(self.size):
						   if i > 1 or j > 1:
							   n = render.attachNewNode("Obstacle")
							   self.obs.instanceTo(n)
							   n.reparentTo(render)
							   n.setPos(-70/8 + i * 14.5/8, -80/8 + j * 14.5/8, 0)
							   self.OBS.append(n)      

		self.skybox = loader.loadModel("models/dome.bam")
		self.skytex = loader.loadTexture("Texture/spacebackground.png")
		self.skybox.setTexture(self.skytex)
		self.skybox.setScale(20)
		self.skybox.setBin('background', 1)
		self.skybox.setDepthWrite(0)
		self.skybox.setLightOff()
		self.skybox.reparentTo(render)

		self.setupModels()

    def setupControls(self):


        self.accept("escape", exit)
        self.accept("space", self.setfire, [0, 1])

        self.addKey("w", "forward")
        self.addKey("a", "left")
        self.addKey("s", "backward")
        self.addKey("d", "right")
        self.addKey("arrow_left", "turnLeft")
        self.addKey("arrow_right", "turnRight")
        self.addKey("arrow_down", "turnDown")
        self.addKey("arrow_up", "turnUp")

        self.setKey('zoom', 0)
        self.accept("wheel_up", self.setKey, ['zoom', 1])
        self.accept("wheel_down", self.setKey, ['zoom', -1])

        self.addKey("shift", "hyper")
        
        self.controllerKeys = [0 for x in range(pygame.joystick.get_count())]
        for i in range(0, pygame.joystick.get_count()):
            self.controllerKeys[i] = ControllerHandler(i)

        taskMgr.add(self.move, "moveTask")
        
    def setupCameras(self):
        self.cam.node().getDisplayRegion(0).setActive(0)

        self.cameras = [0 for x in range(self.numOfPlayers+1)]
        self.floaters = [0 for x in range(self.numOfPlayers+1)]
        
        for i in range(0, self.numOfPlayers+1):
            self.cameras[i] = self.makeCamera(self.win)
            self.floaters[i] = NodePath(PandaNode("floater"))        

        for i in range(0, self.numOfPlayers):
            self.floaters[i].reparentTo(self.player[i])
            self.floaters[i].setZ(1.0)
            self.floaters[i].setY(-1.0)

        for i in range(0, self.numOfPlayers):
            self.cameras[i].setH(180)
            self.cameras[i].reparentTo(self.player[i])
            #self.player[i].setScale(8)
        
        if self.numOfPlayers == 2:
            for i in range(0, self.numOfPlayers):
                self.makeRegion(self.cameras[i], Vec4(0, 1, 0.5-(i*0.5), 1-(i*0.5)))
        elif self.numOfPlayers == 3:
            self.makeRegion(self.cameras[0], Vec4(0, 0.5, 0.5, 1))
            self.makeRegion(self.cameras[1], Vec4(0.5, 1, 0.5, 1))
            self.makeRegion(self.cameras[2], Vec4(0, 0.5, 0, 0.5))
            self.cameras[3].setPos(0, 0, 50)
            self.cameras[3].setHpr(0, -90, 0)
            #self.makeRegion(self.cameras[3], Vec4(0.33, 0.66, 0.33, 0.66))
            self.makeRegion(self.cameras[3], Vec4(0.5, 1, 0, 0.5))
        else:
            self.makeRegion(self.cameras[0], Vec4(0, 0.5, 0.5, 1))
            #self.makeRegion(self.cameras[1], Vec4(0.5, 1, 0.5, 1))
            #self.makeRegion(self.cameras[2], Vec4(0, 0.5, 0, 0.5))
            #self.makeRegion(self.cameras[3], Vec4(0.5, 1, 0, 0.5))

    def setupCollision(self):
		cnodePath = [0 for x in range(self.numOfPlayers)]
		pusher = [0 for x in range(self.numOfPlayers)]
		self.cTrav = CollisionTraverser()

		# for i in range(0, self.numOfPlayers):
		#cs = CollisionBox((0, 0, 5), 3, 3, 4)
		cnodePath[0] = self.player[0].attachNewNode(CollisionNode('player1'))
		#cnodePath[0].node().addSolid(cs)
		cs = CollisionSphere(0, 0, 0.5, 0.5)
		cnodePath[0].node().addSolid(cs)
		cnodePath[0].show()

		#cs = CollisionBox((0, 0, 5), 3, 3, 4)
		cnodePath[1] = self.player[1].attachNewNode(CollisionNode('player2'))
		#cnodePath[1].node().addSolid(cs)
		#cs = CollisionSphere(0, 0, 9.5, 2)
		cnodePath[1].node().addSolid(cs)
		#cnodePath[1].show()

		#cs = CollisionBox((0, 0, 5), 3, 3, 4)
		cnodePath[2] = self.player[2].attachNewNode(CollisionNode('player3'))
		#cnodePath[2].node().addSolid(cs)
		#cs = CollisionSphere(0, 0, 9.5, 2)
		cnodePath[2].node().addSolid(cs)
		# cnodePath[2].show()

		for o in self.OBS:
			ct = CollisionBox((0, 0, 0), 1 , 1, 0.5)
			cn = o.attachNewNode(CollisionNode('box'))
			cn.node().addSolid(ct)
			cn.show()
		for i in range(0, self.numOfPlayers):
			pusher[i] = CollisionHandlerPusher()
			pusher[i].addCollider(cnodePath[i], self.player[i])
			self.cTrav.addCollider(cnodePath[i], pusher[i])
		# self.cTrav.showCollisions(render)

		cs =CollisionSphere(0, 0, 0.5, 0.5)
		healthNode = self.marsh.attachNewNode(CollisionNode('health'))
		healthNode.node().addSolid(cs)
		#healthNode.show()

		speedNode = self.speed.attachNewNode(CollisionNode('speed'))
		speedNode.node().addSolid(cs)
		#speedNode.show()

		base.cTrav.addCollider(healthNode, self.notifier)
		base.cTrav.addCollider(speedNode, self.notifier)
            
        

if __name__ == "__main__":
    gameApp = Application()
    gameApp.run()
