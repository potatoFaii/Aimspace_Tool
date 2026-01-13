# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
import math
try:
    import maya.cmds as cmds
    import maya.mel as mel
except ImportError:
    pass
import IndivPyAimSpace

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# -= Aimspace_UI.py =-
# __author__ = 'Lui Kit Fai'
# __license__ = ''
# __revision__ = 5
# __category__ = 'animation'
# __date__ = 2026-01-12
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class Aimspace_UI(object):
    rig_window = "WindowAimSpace"
    title_window = "KF_AimSpace"
    scriptPresetFolderPath  = cmds.internalVar(userAppDir=True)
    
    def __init__(self, *args):
        self.IndivPyAimSpace()

    def IndivPyAimSpace(self, *args):
        if (cmds.window("{}".format(self.rig_window),q=True,ex=True)):
            cmds.deleteUI("{}".format(self.rig_window),wnd=True)
        # Define window UI
        cmds.window(self.rig_window,t="{}".format(self.title_window),menuBar=True,sizeable=True,toolbox=False,
                    resizeToFitChildren=True,mnb=False,mxb=False,widthHeight=(250,300))
        cmds.menu(l="Help")
        cmds.menuItem(l=' Tutorial',i='SP_DirOpenIcon.png',c=lambda x:self.tutorials())
        cmds.menu(l='Reload')
        cmds.menuItem(l='Reload UI',c=lambda x:self.reloadAS())
        MainForm = cmds.formLayout(nd=100) # Main Layout
        maintabs = cmds.tabLayout()    
        cmds.formLayout(MainForm, edit=True,attachForm=[(maintabs,'top',5),(maintabs,'bottom',10),(maintabs,'left',5),(maintabs,'right',5)]) 

        # First Layout
        sFormL = cmds.formLayout()
        cmds.tabLayout(maintabs,edit = True,tabLabel=[sFormL,'- Function -'])
        #
        frameLay = cmds.frameLayout(l="AimSpace_Locator", labelAlign="center",collapsable=False,fn='boldLabelFont',bgc=(0.4,0.234,0.314),p=sFormL)
        cmds.formLayout(sFormL, e=True,attachForm=[(frameLay,'top',5),(frameLay,'left',5),(frameLay,'right',5)])
        cmds.setParent('..')
        cmdTxt1 = cmds.text('-Set GapDistance Value-',align="center",en=False)
        cmds.formLayout(sFormL, edit=True,attachControl=[(cmdTxt1,'top',0,frameLay)],
                                             attachForm=[(cmdTxt1,'left',5),(cmdTxt1,'right',5)])
        #
        distFormLOut = cmds.formLayout(bgc=(0.8,0.3,0.3))
        cmds.formLayout(sFormL,e=True,attachControl=[(distFormLOut,'top',5,cmdTxt1)],
                                         attachForm=[(distFormLOut,'left',5),(distFormLOut,'right',5)])
        distFormL = cmds.formLayout(bgc=(0.3,0.3,0.3))
        cmds.formLayout(distFormLOut,e=True,attachForm=[(distFormL,'top',1),(distFormL,'left',1),(distFormL,'right',1),(distFormL,'bottom',1)])
        aimText = cmds.text("Aim Space Distance :",align="left")
        self.intF = cmds.intSliderGrp(min=0,max=100,value=50,field=True,cw2=(80,20))
        self.breakLimitinF = cmds.checkBox(l="Limit",cc=lambda x:self.changeLimit())
        intFSep = cmds.separator(style="none")
        cmds.formLayout(distFormL,e=True,attachControl=[(self.intF,'top',5,aimText),
                                                        (intFSep,'top',7,self.intF)],
                                            attachForm=[(aimText,'top',5),(aimText,'left',10),(aimText,'right',5),
                                                        (self.breakLimitinF,'top',4),(self.breakLimitinF,'right',5),
                                                        (self.intF,'left',5),(self.intF,'right',5)])
        cmds.setParent('..')
        cmds.setParent('..')
        wsFormL = cmds.formLayout()
        cmds.formLayout(sFormL,e=True,attachControl=[(wsFormL,'top',5,distFormLOut)],
                                         attachForm=[(wsFormL,'left',5),(wsFormL,'right',5)])
        cbAIMTxt = cmds.checkBox(l='WorldSpaceTranslation',v=True)
        cbAIMTxt1 = cmds.text(l='-  ON  -  Worldspace ',align="center",en=1,fn='smallPlainLabelFont')
        cbAIMTxt2 = cmds.text(l=' -  OFF  - Objectspace  ',align="center",en=1,fn='smallPlainLabelFont')
        cbAIMTxt3 = cmds.text(l='______________',align="center",en=0,fn='smallPlainLabelFont')
        cmds.formLayout(wsFormL,e=True,attachControl=[(cbAIMTxt1,'top',0,cbAIMTxt),
                                                      (cbAIMTxt2,'top',0,cbAIMTxt1),
                                                      (cbAIMTxt3,'top',-8,cbAIMTxt2)],
                                          attachForm=[(cbAIMTxt,'left',5),
                                                      (cbAIMTxt1,'left',24),
                                                      (cbAIMTxt2,'left',20),
                                                      (cbAIMTxt3,'left',63)])
        cmds.setParent('..')
        btnMainFormL = cmds.formLayout()
        cmds.formLayout(sFormL,e=True,attachControl=[(btnMainFormL,'top',10,wsFormL)],
                                         attachForm=[(btnMainFormL,'left',5),(btnMainFormL,'right',5)])
        btnTitleFormL = cmds.formLayout(bgc=(0.2,0.2,0.2))
        cmds.formLayout(btnMainFormL,e=True,attachForm=[(btnTitleFormL,"top",0),(btnTitleFormL,"left",0),(btnTitleFormL,"right",0),(btnTitleFormL,"bottom",0)])
        self.posTxt = cmds.text(l='[ POSITIVE ]',align="center",en=1)
        self.posNegToggle = cmds.checkBox(l='',v=True,bgc=(0.8,0.5,0.5),cc=lambda x:self.posNegToggleFunc())
        self.btnX = cmds.button(l='+X',bgc=(0.3,0.3,0.3),h=20,c=lambda x:self.createXAim())
        self.btnY = cmds.button(l='+Y',bgc=(0.3,0.3,0.3),h=20,c=lambda x:self.createYAim())
        self.btnZ = cmds.button(l='+Z',bgc=(0.3,0.3,0.3),h=20,c=lambda x:self.createZAim())
        btnSep = cmds.separator(style='none')
        cmds.formLayout(btnTitleFormL,e=True,attachControl=[(self.btnX,'top',5,self.posTxt),
                                                            (self.btnY,'top',5,self.btnX),
                                                            (self.btnZ,'top',5,self.btnY),
                                                            (btnSep,'top',10,self.btnZ)],
                                                attachForm=[(self.posTxt,"top",5),(self.posTxt,"right",0),(self.posTxt,"left",0),
                                                            (self.posNegToggle,"top",5),(self.posNegToggle,"right",15),
                                                            (self.btnX,"left",15),(self.btnX,"right",15),
                                                            (self.btnY,"left",15),(self.btnY,"right",15),
                                                            (self.btnZ,"left",15),(self.btnZ,"right",15)])
        cmds.setParent('..')
        cmds.setParent('..')
        endSep = cmds.separator(style='none')
        cmds.formLayout(sFormL,e=True,attachControl=[(endSep,'top',5,btnMainFormL)])
        cmds.setParent('..')

        tFormL = cmds.formLayout()
        cmds.tabLayout(maintabs,edit = True,tabLabel=[tFormL,'- Manual -'])
        tframeLay = cmds.frameLayout(l="AimSpace_Locator", labelAlign="center",collapsable=False,fn='boldLabelFont',bgc=(0.4,0.234,0.314),p=tFormL)
        cmds.formLayout(tFormL, e=True,attachForm=[(tframeLay,'top',5),(tframeLay,'left',5),(tframeLay,'right',5)])
        cmds.setParent('..')
        txGuideMnl1 = cmds.text(l='1. SELECTION Controller',align="center",fn='boldLabelFont')
        txGuideMnl2 = cmds.text(l='- It will generate two locator ,adjust targetLoc -',align="center",fn='smallPlainLabelFont')
        cmds.formLayout(tFormL, e=True,attachControl=[(txGuideMnl1,'top',5,tframeLay),
                                                      (txGuideMnl2,'top',0,txGuideMnl1)],
                                          attachForm=[(txGuideMnl1,'left',5),(txGuideMnl1,'right',5),
                                                      (txGuideMnl2,'left',5),(txGuideMnl2,'right',5)])
        #
        genLocFormLOut = cmds.formLayout(bgc=(0.8,0.3,0.3))
        cmds.formLayout(tFormL,e=True,attachControl=[(genLocFormLOut,'top',6,txGuideMnl2)],
                                         attachForm=[(genLocFormLOut,'left',5),(genLocFormLOut,'right',5)])
        genLocFormL = cmds.formLayout(bgc=(0.3,0.3,0.3))
        cmds.formLayout(genLocFormLOut,e=True,attachForm=[(genLocFormL,'top',1),(genLocFormL,'left',1),(genLocFormL,'right',1),(genLocFormL,'bottom',1)])
        #
        MnlColl = cmds.radioCollection()
        self.txMnl = cmds.radioButton(l='tx',cl=MnlColl,sl=True)
        self.tyMnl = cmds.radioButton(l='ty',cl=MnlColl)
        self.tzMnl = cmds.radioButton(l='tz',cl=MnlColl)
        self.sliderMnl = cmds.intSliderGrp(min=-100,max=100,value=50,field=True,cw2=(80,20))
        MnlSep = cmds.separator(style='none')
        cmds.formLayout(genLocFormL,e=True,attachControl=[(self.sliderMnl,'top',0,self.tzMnl),
                                                          (MnlSep,'top',5,self.sliderMnl)],
                                              attachForm=[(self.txMnl,'left',15),
                                                          (self.tzMnl,'right',15),
                                                          (self.sliderMnl,'left',5),(self.sliderMnl,'right',5)],
                                          attachPosition=[(self.tyMnl,"left",0,40),(self.tyMnl,"right",0,55)])
        cmds.setParent('..')
        cmds.setParent('..')
        genMnlBtn = cmds.button(l='- < GenerateLocator > -',c=lambda x:self.generateLoc())
        genMnlBtnSep = cmds.separator(style='in')
        cmds.formLayout(tFormL,e=True,attachControl=[(genMnlBtn,'top',10,genLocFormLOut),
                                                     (genMnlBtnSep,'top',10,genMnlBtn)],
                                         attachForm=[(genMnlBtn,'left',5),(genMnlBtn,'right',5),
                                                     (genMnlBtnSep,'left',0),(genMnlBtnSep,'right',0)])
        
        txGuideMnl3 = cmds.text('- 2. SELECT "target" locator -',align="center",fn='boldLabelFont')
        txGuideMnl4 = cmds.text('*-Notice that above radioTick also ',align="center",en=1,fn='smallPlainLabelFont') 
        txGuideMnl5 = cmds.text('affect the result of the locator',align="center",en=1,fn='smallPlainLabelFont')
        txGuideMnl6 = cmds.text('Make sure to tick the exact result to Locator',align="center",en=1,fn='smallPlainLabelFont')
        cmds.formLayout(tFormL,e=True,attachControl=[(txGuideMnl3,'top',5,genMnlBtnSep),
                                                     (txGuideMnl4,'top',0,txGuideMnl3),
                                                     (txGuideMnl5,'top',0,txGuideMnl4),
                                                     (txGuideMnl6,'top',0,txGuideMnl5)],
                                         attachForm=[(txGuideMnl3,'left',5),(txGuideMnl3,'right',5),
                                                     (txGuideMnl4,'left',5),(txGuideMnl4,'right',5),
                                                     (txGuideMnl5,'left',5),(txGuideMnl5,'right',5),
                                                     (txGuideMnl6,'left',5),(txGuideMnl6,'right',5)])
        self.cbWorldMn1 = cmds.checkBox(l='WorldSpaceTranslation',v=True)
        MnlCreateBtn = cmds.button(l='< Create >',bgc=(0.5,0.7,0.5),c=lambda x:self.createLocFunction())
        cmds.formLayout(tFormL,e=True,attachControl=[(self.cbWorldMn1,'top',3,txGuideMnl6),
                                                     (MnlCreateBtn,'top',5,self.cbWorldMn1)],
                                         attachForm=[(self.cbWorldMn1,'left',5),
                                                     (MnlCreateBtn,'left',5),(MnlCreateBtn,'right',5)])
        cmds.showWindow(self.rig_window)

    def changeLimit(self):
        checkBoxTick = cmds.checkBox(self.breakLimitinF,q=True,v=True)
        value = 10000 if checkBoxTick else 100
        cmds.intSliderGrp(self.intF,e=True,max=value)

    def posNegToggleFunc(self):
        isPositive = cmds.checkBox(self.posNegToggle,q=True,v=True)
        stateText = '[ POSITIVE ]' if isPositive else '[ NEGATIVE ]'
        sign = '+' if isPositive else '-'
        cmds.text(self.posTxt,e=True,l=stateText)
        axes = ['X','Y','Z']
        buttons = [self.btnX,self.btnY,self.btnZ]
        for btn, axis in zip(buttons,axes):
            cmds.button(btn,e=True,l='{}{}'.format(sign,axis))
    def tutorials(self):
        script_dirP = os.path.dirname(os.path.abspath(__file__))
        script_dirP = script_dirP.replace("IndivPyAimSpace","tutorial")
        os.startfile(script_dirP)
    def reloadAS(self):
        self.IndivPyAimSpace()

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
    
    def createXAim(self, *args):
        self.createAimSpace('X')
    def createYAim(self, *args):
        self.createAimSpace('Y')
    def createZAim(self, *args):
        self.createAimSpace('Z')

if not __name__=='__main__':
    try:
        Aimspace_UI()
    except:
        pass


