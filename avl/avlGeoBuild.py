import json
from math import radians, sqrt, tan
import avl.avlwrapper as avl
import time

def avlGeoBuild(stateVariables):

    def unpackSec(nameSurface):
        NUMBER_SECTIONS ={
            "wing": 3,
            "horizontal": 1,
            "vertical": 1
        }
        if nameSurface in NUMBER_SECTIONS:
            numberOfSecs = NUMBER_SECTIONS[nameSurface]
        else: raise NameError("Wrong parameter name in unpackSec(). Valid parameters are: 'wing', 'horizontal', 'vertical'.")

        secs =[{
                "chord": stateVariables[0],
                "b": 0,
                "sweep": 0,
                "aoa": stateVariables[1]
            }]
        for i in range(numberOfSecs):
            sec = {
                "chord": stateVariables[i+2],
                "b": stateVariables[i+3],
                "sweep": stateVariables[i+4],
                "aoa": stateVariables[i+5]
            }
            secs.append(sec)

        return secs


    def sectionBuild(secs):
