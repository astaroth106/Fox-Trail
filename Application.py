from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from AppState import *
from SplitScreenwithController import *

class Application(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        state = AppState("Application")
        state.request("Menu")
