from panda3d.core import *
from pandac.PandaModules import *

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from math import sin, cos, pi

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
