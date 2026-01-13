# -*- coding: utf-8 -*-
import os
import sys	
import json
import webbrowser
import math
import re
import maya.cmds as cmds
import maya.mel as mel


def get_safe_time_range(self):
    return (int(math.floor(cmds.playbackOptions(q=True, min=True))),
            int(math.ceil(cmds.playbackOptions(q=True, max=True))))

def generateLoc(self):
    valueSlider = cmds.intSliderGrp(self.sliderMnl ,query=True ,value=True)
    selection=cmds.ls(sl=True)
    if not selection:
        cmds.warning("You need select controller first")
        return

    for sel in selection:
        checkName = "{}_temp_aimspace_root".format(sel)
        if cmds.objExists(checkName) == True :
            cmds.warning("{} <EXIST>".format(checkName))
            return
        obj=str(sel)
        root = cmds.spaceLocator(n="{}_temp_aimspace_root".format(obj))
        rootOff = cmds.spaceLocator(n="{}_temp_aimspace_offset".format(obj))
        target = cmds.spaceLocator(n="{}_temp_aimspace_target".format(obj))
        cmds.parent(rootOff,root)
        axis = ['X','Y','Z']
        for ax in axis:
            cmds.setAttr("{}.localScale{}".format(target[0],ax), 5)
        rgb = ("R","G","B")
        cmds.setAttr("{}.overrideEnabled".format(target[0]), 1)
        cmds.setAttr("{}.overrideRGBColors ".format(target[0]),1)
        for channel,colorChange in zip(rgb, (0,0.6,0.6)): #lightBlue visual
            cmds.setAttr("{}.overrideColor{} ".format(target[0],channel),colorChange)
        cmds.parentConstraint(obj,root,mo=False)
        targetconst = cmds.parentConstraint(obj,target,mo=False)
        cmds.delete(targetconst)
        if cmds.radioButton("{}".format(self.txMnl),q=True ,sl=True):
            cmds.xform(target[0],t=(valueSlider, 0, 0), r=1, os=1)
        elif cmds.radioButton("{}".format(self.tyMnl), q=True ,sl=True):
            cmds.xform(target[0],t=(0, valueSlider, 0), r=1, os=1)        
        elif cmds.radioButton("{}".format(self.tzMnl), q=True ,sl=True):
            cmds.xform(target[0],t=(0, 0, valueSlider), r=1, os=1)
        cmds.select(target,root)
        mel.eval('print ("RESULT : {} locator generate <COMPLETE>\\n")'.format(obj))

def createLocFunction(self):
    minTime, maxTime = self.get_safe_time_range()
    selLoc = cmds.ls(sl=True)
    loc = selLoc[0]
    if "temp_aimspace" not in loc:
        cmds.warning("selection not '{}' ,please check".format("_temp_aimspace_")) 
        return
    
    base = loc.split("_temp_aimspace") # get back the name of the selection object 
    target = ("{}_temp_aimspace_target".format(base[0]))
    root = ("{}_temp_aimspace_root".format(base[0]))
    offset = ("{}_temp_aimspace_offset".format(base[0]))
    
    if cmds.listConnections(target,s=True,type="constraint"):
        cmds.warning("[{}] already constraint".format(target))
        return
    prt = cmds.parentConstraint(base[0], target, mo=True)
    cmds.select(target, root)
    cmds.undoInfo(openChunk=True)
    cmds.refresh(suspend=True)
    cmds.bakeResults(time=(minTime, maxTime),
                        simulation=True,
                        hierarchy='none',
                        oversamplingRate=1,
                        disableImplicitControl=False,
                        preserveOutsideKeys=True,
                        removeBakedAttributeFromLayer=False,
                        bakeOnOverrideLayer=False,
                        controlPoints=False,
                        shape=True)
    cmds.delete(staticChannels=True)
    cmds.filterCurve()
    cmds.delete(prt)
    cmds.refresh(suspend=False)
    cmds.undoInfo(closeChunk=True)

    cmds.setAttr("{}.rotate".format(offset), 0, 0, 0)
    
    def doAim(aimVec, upVec):
        cmds.aimConstraint(target, offset,
                            mo=True,
                            aimVector=aimVec,
                            upVector=upVec,
                            worldUpVector=upVec,
                            worldUpType='objectrotation',
                            worldUpObject=root)
    
    axisData = {
        self.txMnl: ("X", (1, 0, 0), (-1, 0, 0), (0, 0, 1)),
        self.tyMnl: ("Y", (0, 1, 0), (0, -1, 0), (0, 0, 1)),
        self.tzMnl: ("Z", (0, 0, 1), (0, 0, -1), (0, 1, 0))
    }
    
    for btn, (axis, posAim, negAim, upVec) in axisData.items():
        if not cmds.radioButton(btn, q=True, select=True):
            continue
        tgtVal = cmds.getAttr("{}.translate{}".format(target, axis))
        srcVal = cmds.getAttr("{}.translate{}".format(base[0], axis))
        if tgtVal >= srcVal:
            mel.eval('print ("RESULT : +{} created\\n")'.format(axis))
            doAim(posAim, upVec)
        else:
            mel.eval('print ("RESULT : -{} created\\n")'.format(axis))
            doAim(negAim, upVec)
        break
    
    world = cmds.checkBox(self.cbWorldMn1, q=True, value=True)
    if world:
        cmds.pointConstraint(root, base[0])
    else:
        cmds.pointConstraint(base[0], root)
    cmds.orientConstraint(offset, base[0])
    cmds.select(target)
    mel.eval('print ("RESULT : [{}] manual create <COMPLETE>\\n")'.format(target))

def createAimSpace(self, axis):
    AXIS_DATA = {
        'X': {'offset': (1,0,0), 'aim': (1,0,0), 'up': (0,0,1)},
        'Y': {'offset': (0,1,0), 'aim': (0,1,0), 'up': (0,0,1)},
        'Z': {'offset': (0,0,1), 'aim': (0,0,1), 'up': (0,1,0)}
    }
    isPositive = cmds.checkBox(self.posNegToggle, q=True, v=True)
    sign = 1 if isPositive else -1
    sliderVal = cmds.intSliderGrp(self.intF, q=True, v=True)
    minTime, maxTime = self.get_safe_time_range()
    sel = cmds.ls(sl=True)
    if not sel:
        cmds.warning("NO selection")
        return
    for obj in sel:
        root = "{}_temp_aimspace_root".format(obj)
        off  = "{}_temp_aimspace_offset".format(obj)
        tar  = "{}_temp_aimspace_target".format(obj)
        if cmds.objExists(root):
            cmds.warning("{} exists, remove it to recreate".format(root))
            continue

        root = cmds.spaceLocator(n=root)[0]
        off  = cmds.spaceLocator(n=off)[0]
        tar  = cmds.spaceLocator(n=tar)[0]
        cmds.parent(off, root)

        cmds.setAttr("{}.localScale".format(tar), 25,25,25)
        cmds.setAttr("{}.overrideEnabled".format(tar), 1)
        cmds.setAttr("{}.overrideRGBColors".format(tar), 1)
        cmds.setAttr("{}.overrideColorR".format(tar), 0)
        cmds.setAttr("{}.overrideColorG".format(tar), .6)
        cmds.setAttr("{}.overrideColorB".format(tar), .6)

        cmds.parentConstraint(obj, root, mo=False)
        cmds.parentConstraint(obj, tar, mo=False)
        cmds.delete(tar, constraints=True)
        offset = tuple(v * sliderVal * sign for v in AXIS_DATA[axis]['offset'])
        cmds.xform(tar, r=True, os=True, t=offset)

        prt = cmds.parentConstraint(obj, tar, mo=True)

        cmds.select(tar, root)
        cmds.refresh(suspend=True)
        cmds.bakeResults(time=(minTime, maxTime),
                            simulation=True,
                            sampleBy=1,
                            minimizeRotation=True,
                            preserveOutsideKeys=True)
        cmds.delete(staticChannels=True)
        cmds.filterCurve()
        cmds.delete(prt)
        cmds.refresh(suspend=False)

        # aim
        aimVec = tuple(v * sign for v in AXIS_DATA[axis]['aim'])
        upVec  = AXIS_DATA[axis]['up']

        cmds.aimConstraint(tar, off,mo=True,aimVector=aimVec,upVector=upVec,worldUpVector=upVec,worldUpType="objectrotation",worldUpObject=root)

        world = cmds.checkBox(self.cbWorldMn1, q=True, v=True)
        if world:
            cmds.pointConstraint(root, obj)
        else:
            cmds.pointConstraint(obj, root)
        cmds.orientConstraint(off, obj)
    mel.eval('print ("RESULT : aimspace created\\n")')