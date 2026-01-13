# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import json
try:
	import maya.cmds as cmds
	import maya.mel as mel
except ImportError:
	pass
import IndivPySpaceSwitch.spaceSwitch_Func as spaceSwitch_Func

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - spaceSwitch_UI.py -
# __author__ = 'Lui Kit Fai'
# __license__ = ''
# __revision__ = 6
# __category__ = 'Animation'
# __date__ = 2026-01-08
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class spaceSwitch_UI:
	rig_window = "WindowSpaceSwitch"
	title_window = "KF_SpaceSwitch"
	scriptPresetFolderPath  = cmds.internalVar(userAppDir=True)+'scripts/KF_PresetStore'
	scriptPresetPath = scriptPresetFolderPath + '/KF_SpaceSwitchPreset.json'
	COLLAPSE_STATE_OPTION_VAR = "SpaceSwitchOptionalCollapseState"
	# - Optional - Instance variables initialization
	optionExpanded = False
	TARGET_BAKE_KEY = "KFSpaceSwitch_TargetBakeTB"
	
	def __init__(self, *args):
		self.state_optionVar = "KFSpaceSwitch_OptionalTB"
		self.IndivPySpaceSwitch()	
	def save_button_state(self,button_name,state):
		states = self.get_all_button_states()
		states[button_name] = state
		cmds.optionVar(sv=(self.state_optionVar,json.dumps(states)))
	def get_button_state(self,button_name):
		states = self.get_all_button_states()
		return states.get(button_name,False)
	def get_all_button_states(self):
		if cmds.optionVar(exists = self.state_optionVar):
			return json.loads(cmds.optionVar(q=self.state_optionVar))
		return{}
	def restore_all_states(self):
		cmds.checkBox(self.targetBakeTickBtn, e=True,v=self.get_button_state("KFSpaceSwitch_TargetBakeTB"))
	
	def IndivPySpaceSwitch(self):
		self.optional_state = self.get_button_state("KFSpaceSwitch_OptionalTB")
		self.targetBake_state = self.get_button_state("KFSpaceSwitch_TargetBakeTB")
		TARGET_BAKE_KEY = "KFSpaceSwitch_TargetBakeTB"
		# Close old window if its open
		if (cmds.window("{}".format(self.rig_window) ,q=True, exists = True)):
			cmds.deleteUI("{}".format(self.rig_window),window=True)
		collapse_state = self.get_collapse_state()
		# Define window UI
		window = cmds.window(self.rig_window,t=self.title_window,menuBar=True,sizeable=True,toolbox=False, 
							 resizeToFitChildren=True,mnb=False,mxb=False,widthHeight=(240,240))
		cmds.menu(l='Help')
		cmds.menuItem(l='Instruction', divider=True)
		cmds.menuItem(l='Update Log',i='SP_FileIcon.png',c=lambda x:self.helps())
		cmds.menuItem(l='Tutorial',i='SP_DirOpenIcon.png',c=lambda x:self.tutorial())
		cmds.menu(l='Reload')
		cmds.menuItem(l='Reload UI',en=True,c=lambda x:self.reload_UI())
		# New TabLayout
		maintabs = cmds.tabLayout()
		# MainLayout
		fTab = cmds.formLayout(numberOfDivisions=100)
		cmds.tabLayout(maintabs,e=True,tabLabel=[fTab,'- Function -']) # Adding tab
		frameLay = cmds.frameLayout(l="SpaceSwitchk_Cheat", labelAlign="center",collapsable=False,fn='boldLabelFont',bgc=(0.399,0.234,0.314),p=fTab)
		cmds.formLayout(fTab, e=True,attachForm=[(frameLay,'top',5),(frameLay,'left',5),(frameLay,'right',5)])
		functionLayout = cmds.formLayout()
		switchInstTF = cmds.textField(text="Single",width=80,height=22,ed=False,bgc=(0.5,0.8,0.8))
		# Button
		switch_collection = cmds.radioCollection()
		self.switchSing = cmds.radioButton(l = 'Single',sl=True,collection=switch_collection,cc=lambda x :self.SwitchSCmd(switchInstTF))
		self.switchDoub = cmds.radioButton(l = 'D',collection=switch_collection,cc=lambda x :self.SwitchDCmd(switchInstTF))
		self.switchManual = cmds.radioButton(l = 'M',collection=switch_collection,cc=lambda x :self.SwitchMCmd(switchInstTF,self.switchManual,rotateOrderTxt))
		rotateOrderTxt = cmds.text(l=" Rotate Order ",align="center",en=False,fn='boldLabelFont')
		rotateOrderUnderlineTxt = cmds.text( l=" ____________________________ ",en=False,fn='smallPlainLabelFont')
		b1 = cmds.button(l="- XYZ -", ann = " RotateOrder : <0> XYZ ", c=lambda x:self.createLocatorFunction('XYZ'))
		b2 = cmds.button(l="- YZX -", ann = " RotateOrder : <1> YZX ", c=lambda x:self.createLocatorFunction('YZX'))
		b3 = cmds.button(l="- ZXY -", ann = " RotateOrder : <2> ZXY ", c=lambda x:self.createLocatorFunction('ZXY'))
		b4 = cmds.button(l="- XZY -", ann = " RotateOrder : <3> XZY ", c=lambda x:self.createLocatorFunction('XZY'))
		b5 = cmds.button(l="- YXZ -", ann = " RotateOrder : <4> YXZ ", c=lambda x:self.createLocatorFunction('YXZ'))
		b6 = cmds.button(l="- ZYX -", ann = " RotateOrder : <5> ZYX ", c=lambda x:self.createLocatorFunction('ZYX'))
		self.targetBakeTickBtn = cmds.checkBox(l="TargetBake",v=self.targetBake_state,cc=lambda x :self.bakeTickBoxCmd(self.targetBakeTickBtn,self.TargetBakeFrameL,x))
		fTabseperator = cmds.separator(style='none')
		cmds.formLayout(functionLayout, edit=True,attachControl=[(self.switchSing,'left',5,switchInstTF),(self.switchDoub,'left',5,self.switchSing),(self.switchManual,'left',5,self.switchDoub),
																  (b4,'left',5,b1),
																  (b5,'left',5,b2),
																  (b6,'left',5,b3),],
															attachForm=[(switchInstTF,'top',2),(switchInstTF,'left',5),
																		(self.switchSing,'top',4),(self.switchDoub,'top',4),(self.switchManual,'top',4),
																		(rotateOrderTxt,'top',26),(rotateOrderTxt,'left',0),(rotateOrderTxt,'right',0),
																		(rotateOrderUnderlineTxt,'top',28),(rotateOrderUnderlineTxt,'left',0),(rotateOrderUnderlineTxt,'right',0),
																		(b1,'top',45),(b1,'left',0),
																		(b4,'top',45),(b4,'right',0),
																		(b2,'top',75),(b2,'left',0),
																		(b5,'top',75),(b5,'right',0),
																		(b3,'top',105),(b3,'left',0),
																		(b6,'top',105),(b6,'right',0),
																		(self.targetBakeTickBtn,'top',135),
																		(fTabseperator,'top',150) ,(fTabseperator,'left',0),(fTabseperator,'right',0)],
													attachPosition=[(b1, "right", 0, 49),(b4, "left", 0, 51),
																	(b2, "right", 0, 49),(b5, "left", 0, 51),
																	(b3, "right", 0, 49),(b6, "left", 0, 51)])
		
		cmds.setParent('..')
		
		# Manual functionList
		self.ManualFrameL = cmds.frameLayout(l="< Manual >", labelAlign="center",collapsable=False,collapse=False,vis=False,
											collapseCommand=lambda *args: cmds.evalDeferred(lambda: self.on_collapse_changed()),
											expandCommand=lambda *args: cmds.evalDeferred(lambda: self.on_collapse_changed()),
											backgroundColor=[0.3,0.5,0.5])
		self.ManualFL = cmds.formLayout()
		instThird = cmds.text('-2.Select Target and Function -',align="center",en=0)
		instThirdUL = cmds.text( l=" __________________________________________ ",en=False,fn='smallPlainLabelFont')
		instThirdButton = cmds.button(l="Bake",c=lambda x:spaceSwitch_Func.LocManualBake())
		instSep = cmds.separator(style='in')
		cmds.formLayout(self.ManualFL, edit=True,attachControl = [(instSep,'top',10,instThirdButton)],
												    attachForm = [(instThird,'top',3),(instThird,'left',0),(instThird,'right',0),
																(instThirdUL,'top',6),(instThirdUL,'left',0),(instThirdUL,'right',0),
																(instThirdButton,'top',22),(instThirdButton,'right',5),(instThirdButton,'left',5),
																(instSep,'left',0),(instSep,'right',0)])

		cmds.setParent('..')
		cmds.setParent('..')

		# TargetBake functionList
		self.TargetBakeFrameL = cmds.frameLayout(l="< TargetBAKE >", labelAlign="center",collapsable=False,collapse=False,vis=self.targetBake_state,
											  collapseCommand=lambda *args: cmds.evalDeferred(lambda: self.on_collapse_changed()),
											  expandCommand=lambda *args: cmds.evalDeferred(lambda: self.on_collapse_changed()),
											  backgroundColor=[0.5,0.3,0.3])
		self.TargetBakeFL = cmds.formLayout()
		self.targetBakeProgress = cmds.progressBar(h=20,pr=0)
		self.targetBakeBtn = cmds.button(l="Bake Animation",ann = '''// Help reobtain source of the controller and bake Animation
Include remove animLayer''',c=lambda x:spaceSwitch_Func.bakeFunction(self.targetBakeProgress))
		targetBakeTxt = cmds.text(l='- Select target Controller and Function -',align="center",en=0,fn='smallPlainLabelFont')
		targetBakeSep = cmds.separator(style='none')
		cmds.formLayout(self.TargetBakeFL,edit=True,attachForm=[(self.targetBakeProgress,'top',5),(self.targetBakeProgress,'left',0),(self.targetBakeProgress,'right',0),
																(self.targetBakeBtn,'top',30),(self.targetBakeBtn,'left',1),(self.targetBakeBtn,'right',1),
																(targetBakeTxt,'top',60),(targetBakeTxt,'left',0),
																(targetBakeSep,'top',80),(targetBakeSep,'left',0),(targetBakeSep,'right',0)])
		
		cmds.setParent('..')
		cmds.setParent('..')
		spaceL = cmds.formLayout()
		betaText = cmds.text(l='[ KF_SpaceSwitch Locator 2.0  Beta ]',align="center",en=False,fn='smallPlainLabelFont')
		spaceSep = cmds.separator(style='none')
		cmds.formLayout(spaceL,e=True,attachForm=[(betaText,'top',5),(betaText,'left',0),(betaText,'right',0),
												  (spaceSep,'top',25),(spaceSep,'left',0),(spaceSep,'right',0)])
		
		# ----- Second tab ----- #
		sTab = cmds.formLayout(p=maintabs)
		cmds.tabLayout(maintabs,e=True,tabLabel=[sTab,'- Edit -'],cc=lambda *args:self.toggleOptionFrame()) # Adding tab
		# Optional
		self.OptionFrameL = cmds.frameLayout(l="Optional", labelAlign="center",collapsable=False,collapse=True,vis=False,
							collapseCommand=lambda *args: cmds.evalDeferred(lambda: self.on_collapse_changed()),
							expandCommand=lambda *args: cmds.evalDeferred(lambda: self.on_collapse_changed()),
							backgroundColor=[0.3,0.5,0.3])
		cmds.formLayout(sTab, edit=True, attachForm=[(self.OptionFrameL,'top',5),
													 (self.OptionFrameL,'left',5),(self.OptionFrameL,'right',5)])
		OptionTabpopupM = cmds.popupMenu()
		cmds.menuItem(l="Reset",i='rvViewingPipelineRefresh.png',p=OptionTabpopupM,c=lambda x:self.OptionResetMI())
		cmds.menuItem(divider=True,p=OptionTabpopupM)
		cmds.menuItem(l="File Location",i='SP_DirOpenIcon.png',p=OptionTabpopupM,c=lambda x:self.OptionFilePathMI())
		self.OptionTab = cmds.formLayout()
		
		savepresetBtn = cmds.button( l='Save Preset',ann='''// Save Preference To Document
{}'''.format(cmds.internalVar(userScriptDir=True)),width=100,c=lambda x:self.savepresetCmd())
		loadpresetBtn = cmds.button( l='Load Preset',ann='''// Load Preference To Document
{}'''.format(cmds.internalVar(userScriptDir=True)),width=100,c=lambda x:self.loadpresetCmd())
		paletteText = cmds.text( l = '1. Index Colour palette :-',align="center",en=True,fn='boldLabelFont')
		self.pale= cmds.palettePort(dim=(12,1), transparent=False, topDown=True, h=20, ced=0)
		cmds.palettePort(self.pale, e=1, rgb=(0, 1.000,1.000,1.000)) #1
		cmds.palettePort(self.pale, e=1, rgb=(1, 0.053,0.352,1.000)) #2
		cmds.palettePort(self.pale, e=1, rgb=(2, 0.078,0.533,0.815)) #3
		cmds.palettePort(self.pale, e=1, rgb=(3, 0.065,0.624,0.418)) #4
		cmds.palettePort(self.pale, e=1, rgb=(4, 0.238,1.000,0.061)) #5
		cmds.palettePort(self.pale, e=1, rgb=(5, 1.000,1.000,0.125)) #6
		cmds.palettePort(self.pale, e=1, rgb=(6, 1.000,0.617,0.089)) #7
		cmds.palettePort(self.pale, e=1, rgb=(7, 1.000,0.195,0.025)) #8
		cmds.palettePort(self.pale, e=1, rgb=(8, 1.000,0.060,0.060)) #9
		cmds.palettePort(self.pale, e=1, rgb=(9, 1.000,0.000,0.038)) #10
		cmds.palettePort(self.pale, e=1, rgb=(10, 1.000,0.165,0.456)) #11
		cmds.palettePort(self.pale, e=1, rgb=(11, 0.407,0.283,0.831)) #12
		self.indexShape = cmds.checkBox(l="Transform",v=True)
		self.indexOutliner = cmds.checkBox(l ="Outliner",v=False)
		indexSeperator = cmds.separator(style='in')
		ctrlText = cmds.text( l = '2. Controller :-',align="center",en=True,fn='boldLabelFont')
		ctrl_collection = cmds.radioCollection()
		self.ctrlLocator = cmds.radioButton( l = 'Locator',sl=True,collection=ctrl_collection)
		self.ctrlNull = cmds.radioButton( l = 'Null',collection=ctrl_collection,cc=lambda x:self.controllerNullCmd(self.indexShape,self.ctrlNull,self.ctrlSizeIntF))
		self.ctrlShape = cmds.radioButton( l = 'Shape',collection=ctrl_collection,cc=lambda x:self.controllerShapeCmd(self.ctrlShape,self.shapeMenu,self.ctrlSizeText,self.ctrlThickIntF))
		self.shapeMenu= cmds.optionMenuGrp(l="Shape :", cw2=(75,100),vis=False,cc=lambda x:self.controllerShapeCreateCmd(self.shapeMenu))
		cmds.menuItem(l="Locator  ")
		cmds.menuItem(l="Cube  ")
		cmds.menuItem(l="Sphere  ")
		cmds.menuItem(l="Pyramid  ")
		cmds.menuItem(l="Cylinder  ")
		ctrlHideSeperator = cmds.separator(style='none')
		ctrlSeperator = cmds.separator(style='in')

		cmds.formLayout(self.OptionTab, edit=True,attachControl=[(self.indexOutliner,'left',15,self.indexShape),
																 (self.ctrlNull,'left',15,self.ctrlLocator),(self.ctrlShape,'left',15,self.ctrlNull),
																 (self.shapeMenu,'bottom',5,ctrlHideSeperator)],
									attachForm=[(savepresetBtn,'left',0),(savepresetBtn,'top',5),
												(loadpresetBtn,'top',5),(loadpresetBtn,'right',0),
												(paletteText,'left',5),(paletteText,'top',37),
												(self.pale, "top", 55),
												(self.indexShape,'top',80),(self.indexShape,'left',2),
												(self.indexOutliner,'top',80),
												(indexSeperator,'top',105),(indexSeperator,'left',0),(indexSeperator,'right',0),
												#
												(ctrlText,'top',115),(ctrlText,'left',5),
												(self.ctrlLocator,'top',130),(self.ctrlLocator,'left',2),
												(self.ctrlNull,'top',130),(self.ctrlShape,'top',130),
												(self.shapeMenu,'top',150),
												(ctrlHideSeperator,'top',155),
												(ctrlSeperator,'left',0),(ctrlSeperator,'right',0)],
									attachPosition=[(savepresetBtn, "right", 0, 49),(loadpresetBtn, "left", 0, 51),
													(self.pale,"left",0,0),(self.pale,"right",0,100),
													(ctrlSeperator,"bottom",0,100)])
		
		cmds.setParent('..')
		
		self.OptionTab2 = cmds.formLayout()
		self.ctrlSizeText = cmds.text(l='3. Size :-',align="center",en=True,fn='boldLabelFont')
		self.ctrlSizeIntF = cmds.floatSliderGrp(min=0,max=100.00,value=10,h=50,ss=6,field=True,cw2=(50,110),precision=2)
		sizepopupM = cmds.popupMenu()
		cmds.menuItem(l="20.00",p=sizepopupM,c=lambda x:self.ctrlIntFValue(20.00,self.ctrlSizeIntF))
		cmds.menuItem(l="40.00",p=sizepopupM,c=lambda x:self.ctrlIntFValue(40.00,self.ctrlSizeIntF))
		cmds.menuItem(l="60.00",p=sizepopupM,c=lambda x:self.ctrlIntFValue(60.00,self.ctrlSizeIntF))
		cmds.menuItem(l="80.00",p=sizepopupM,c=lambda x:self.ctrlIntFValue(80.00,self.ctrlSizeIntF))
		self.ctrlThickIntF = cmds.floatSliderGrp(min=-1.00,max=10.00,value=-1.00,h=50,ss=6,field=True,vis=False,cw2=(50,110),precision=2)
		ctrlSizeSeperator = cmds.separator(style='in')
		#
		cmds.formLayout(self.OptionTab2, edit=True,attachForm=[(self.ctrlSizeText,'top',0),(self.ctrlSizeText,'left',5),
																		(self.ctrlSizeIntF,'top',5),(self.ctrlSizeIntF,'left',5),(self.ctrlSizeIntF,'right',5),
																		(self.ctrlThickIntF,'top',30),(self.ctrlThickIntF,'left',5),(self.ctrlThickIntF,'right',5),
																		(ctrlSizeSeperator,'left',0),(ctrlSizeSeperator,'right',0)],
											  attachPosition=[(ctrlSizeSeperator,"bottom",0,95)])
		
		cmds.setParent('..')
		
		self.OptionTab3 = cmds.formLayout()
		keySettingText = cmds.text(l='4. Key Setting :-',align="center",en=True,fn='boldLabelFont')
		key_collection = cmds.radioCollection()
		self.keyActive = cmds.radioButton(l='TimeSlider',sl=True,collection=key_collection)
		self.keyFrom = cmds.radioButton(l='From',collection=key_collection,cc=lambda x:self.keyFromCmd(self.keyFrom,self.fromtextF,self.totextF))
		self.fromtextF = cmds.textField(tx=0,width=50,en=False)
		toText = cmds.text(l='To' ,fn='boldLabelFont')
		self.totextF = cmds.textField(tx=200,width=50,en=False)
		self.BakeOntextField = cmds.textFieldGrp(l='Sample by:  ',tx=1.0,cw2=(65,150))
		keySetSeperator = cmds.separator(style='in')
		
		cmds.formLayout(self.OptionTab3, edit=True,attachControl=[(self.keyFrom,'left',15,self.keyActive),
																	   (self.fromtextF,'left',15,self.keyActive),(self.totextF,'left',10,toText),(toText,'left',5,self.fromtextF)],
												 attachForm=[(keySettingText,'top',0),(keySettingText,'left',5),
															 (self.keyActive,'top',15),(self.keyActive,'left',0),
															 (self.keyFrom,'top',15),
															 (self.fromtextF,'top',35),
															 (toText,'top',38),
															 (self.totextF,'top',35),
															 (self.BakeOntextField,'top',60),(self.BakeOntextField,'left',0),
															 (keySetSeperator,'top',95),(keySetSeperator,'left',0),(keySetSeperator,'right',0)])
		
		# Apply collapse states
		cmds.frameLayout(self.OptionFrameL, e=True, collapse=collapse_state[0])
		cmds.frameLayout(self.ManualFrameL, e=True, collapse=collapse_state[1])
		cmds.frameLayout(self.TargetBakeFrameL, e=True, collapse=collapse_state[2])
		self.on_collapse_changed()
		cmds.showWindow(self.rig_window)
#=========================================================================================================================================
	#    _________________
	# __/__Menu Window __/__
	def guideWindow(self,instructionNote):
		if (cmds.window("instructWinGL" ,q=True, exists = True)):
			cmds.deleteUI("instructWinGL",window=True)
		instructWGL = "instructWinGL"
		insWindowGL = cmds.window(instructWGL ,t="InstructionWindowGL",widthHeight=(520,550))
		FLayout = cmds.formLayout(numberOfDivisions = 100)
		FPanel = cmds.paneLayout( configuration='horizontal4')
		cmds.formLayout(FLayout,edit=True,attachForm =[(FPanel,"top",10),(FPanel,"bottom",10),(FPanel,"left",10),(FPanel,"right",10)])
		cmds.scrollField( editable=False, wordWrap=True, text=instructionNote)
		cmds.showWindow(insWindowGL)

	def helpsList(self,fileNameFormat):
		script_dir = os.path.dirname(os.path.abspath(__file__))
		script_dir = script_dir.replace("IndivPySpaceSwitch","List_SpaceSwitchk")
		file_name = fileNameFormat
		file_pathQ = os.path.join(script_dir, file_name)
		try:
			with open(file_pathQ, 'r') as file:
				QGuideText = file.read()
		except IOError:
			QGuideText = 'Error: Failed to load Q guide.'
		self.guideWindow(QGuideText)

	def helps(self):
		self.helpsList('list_GL.py')

	def tutorial(self):
		script_dirP = os.path.dirname(os.path.abspath(__file__))
		#print script_dirP
		script_dirP = script_dirP.replace("IndivPySpaceSwitch","tutorial")
		os.startfile(script_dirP)
	#    _____________________
	# __/__Menu Window END __/__
#=========================================================================================================================================
	def reload_UI(self):
		spaceSwitch_UI()
	# Assign Collapse here    
	def get_collapse_state(self):
		if cmds.optionVar(exists=self.COLLAPSE_STATE_OPTION_VAR):
			collapse_state = cmds.optionVar(q=self.COLLAPSE_STATE_OPTION_VAR)
			if collapse_state is not None and len(collapse_state) == 3:
				for value in collapse_state:
					if value < 0 or value > 1:
						return [0, 1, 1]
				return collapse_state
		return [0, 1, 1]
	
	def update_collapse_state(self):
		cmds.optionVar(clearArray=self.COLLAPSE_STATE_OPTION_VAR)
		layouts = [self.OptionFrameL, self.ManualFrameL, self.TargetBakeFrameL]
		for lay in layouts:
			if lay and cmds.frameLayout(lay, exists=True):
				collapse = cmds.frameLayout(lay, q=True, cl=True)
				cmds.optionVar(iva=[self.COLLAPSE_STATE_OPTION_VAR, collapse])

	def on_collapse_changed(self):
		total_height = 220
		layouts = [self.OptionTab,self.OptionTab2,self.OptionTab3,self.ManualFL,self.TargetBakeFL]
		
		for lay in layouts:
			if lay and cmds.frameLayout(lay, exists=True):
				total_height += cmds.formLayout(lay,q=True,h=True)
		if cmds.window(self.rig_window, exists=True):
			cmds.window(self.rig_window,e=True,h=total_height)
		self.update_collapse_state()
	
	def toggleOptionFrame(self):
		self.optionExpanded = not self.optionExpanded
		cmds.frameLayout(self.OptionFrameL,e=True,vis=self.optionExpanded,collapse=not self.optionExpanded)
		cmds.evalDeferred(self.on_collapse_changed)
	
	# UI Customize Adjustment
	def OptionResetMI(self):
		cmds.palettePort(self.pale,e=True,scc=0)
		cmds.checkBox(self.indexShape,e=True,v=True,en=True)
		cmds.checkBox(self.indexOutliner,e=True,v=False)
		
		cmds.radioButton(self.ctrlLocator,e=True,sl=True)
		cmds.optionMenuGrp(self.shapeMenu,e=True,sl=1,vis=False)
		
		cmds.floatSliderGrp(self.ctrlSizeIntF,e=True,v=10.00,en=True)
		cmds.floatSliderGrp(self.ctrlThickIntF,e=True,v=-1.00,vis=False)
		cmds.radioButton(self.keyActive,e=True,sl=True)
		
		cmds.textField(self.fromtextF,e=True,tx=0,en=False)
		cmds.textField(self.totextF,e=True,tx=200,en=False)
		cmds.textFieldGrp(self.BakeOntextField,e=True,tx=1.0)
	
	def OptionFilePathMI(self):
		os.startfile(self.scriptPresetFolderPath)
	
	def SwitchRBCmd(self,texts,textAssign,radioBtn,shortForm,color=()):
		radioSel = cmds.radioButton(radioBtn,q=True,sl=True)
		if radioSel:
			cmds.textField(texts,e=True,text=textAssign,bgc=color)
			cmds.radioButton(radioBtn,e=True,label=textAssign)
		else:
			cmds.radioButton(radioBtn,e=True,label=shortForm)
	
	def SwitchSCmd(self,textAssign):
		textF='Single'
		shortForm = 'S'
		self.SwitchRBCmd(textAssign,textF,self.switchSing,shortForm,color=(0.5,0.8,0.8)) #lightblue
	
	def SwitchDCmd(self,textAssign):
		textF='Double'
		shortForm= 'D'
		self.SwitchRBCmd(textAssign,textF,self.switchDoub,shortForm,color=(0.8,0.7,1.0)) #purple
	
	def SwitchMCmd(self,textAssign,radioBtn,rotateOrderTxt):
		textF='Manual'
		shortForm = 'M'
		is_on = cmds.radioButton(radioBtn,q=True,sl=True)
		self.SwitchRBCmd(textAssign,textF,self.switchManual,shortForm,color=(0.7,1.0,0.8)) #lightgreen
		cmds.frameLayout(self.ManualFrameL,e=True,en=is_on,collapse=not is_on,vis=is_on)
		cmds.text(rotateOrderTxt,e=True,label='-1. Create Controller-' if is_on else ' Rotate Order ')
		#cmds.formLayout(self.OptionTab3,e=True,vis=not is_on)
		if not is_on:
			cmds.evalDeferred(lambda: self.on_collapse_changed())

	# Optional UI Settings
	'''
	def optionTickBoxCmd(self,tickBox,optionF):
		tickV = cmds.checkBox(tickBox,q=True,v=True)
		cmds.frameLayout(optionF,e=True,vis=tickV,collapse=not tickV)
		cmds.evalDeferred(lambda: self.on_collapse_changed())
	'''
	
	def bakeTickBoxCmd(self,tickBox,optionF,state):
		self.save_button_state(self.TARGET_BAKE_KEY, state)
		tickV = cmds.checkBox(tickBox,q=True,v=True)
		cmds.frameLayout(optionF,e=True,vis=tickV,collapse=not tickV)
		cmds.evalDeferred(lambda: self.on_collapse_changed())
	
	def controllerNullCmd(self,shapeTickBtn,nullBtn,ctrlSizeIntF):
		nullSel = cmds.radioButton(nullBtn,q=True,sl=True)
		cmds.floatSliderGrp(ctrlSizeIntF,e=True,en=not nullSel)
		cmds.checkBox(shapeTickBtn,e=True,en=not nullSel)
		
	def controllerShapeCmd(self,radioBtn,optionVis,sizeText,IntFGrp):
		radioSel = cmds.radioButton(radioBtn,q=True,sl=True)
		cmds.optionMenuGrp(optionVis,e=True,vis=radioSel)
		cmds.floatSliderGrp(IntFGrp,e=True,vis=radioSel)
		cmds.text(sizeText,e=True,label='3. Size / Line Width :-' if radioSel else '3. Size :-')
	
	def ctrlIntFValue(self,value,ctrlIntF):
		cmds.floatSliderGrp(ctrlIntF,e=True,v=value)
	
	def keyFromCmd(self,keyFrom,fromText,toText):
		checkRB = cmds.radioButton(keyFrom,q=True,sl=True)
		cmds.textField(fromText,e=True,en=checkRB)
		cmds.textField(toText,e=True,en=checkRB)

	# Return Value for Creating 
	def controllerShapeCreateCmd(self,shapeMenu):
		checkMenu = cmds.optionMenuGrp(shapeMenu,q=True,v=True)
		mel.eval( 'print ("Shape : <{}> \\n")'.format(checkMenu))
		return checkMenu
	# -- Getting ReturnValue of Preset --
	def presetFolderCheck(self):
		try:
			if not os.path.exists(self.scriptPresetFolderPath):
				os.makedirs(self.scriptPresetFolderPath)
			if not os.path.exists(self.scriptPresetPath):
				open(self.scriptPresetPath, 'w').close()
		except OSError as e:
			print('Error: Unable to create folder due to {}'.format(e))
			cmds.warning("Failed to create KF_PresetStore. Check folder permissions.")

	# -- Getting ReturnValue of Preset --
	def savePresetData(self):
		radioList = []
		keySettingList = []
		fromToList = []

		paletteClr = cmds.palettePort(self.pale, q=True, scc=True)
		paletteIndex = paletteClr
		paletteColor = cmds.palettePort(self.pale, q=True, rgb=True) or [1.0, 1.0, 1.0]
		for rdBtn in [self.ctrlLocator,self.ctrlNull,self.ctrlShape]:
			rdSel = cmds.radioButton(rdBtn,q=True,sl=True)
			radioList.append(rdSel)
		for key in [self.keyActive,self.keyFrom]:
			keySel = cmds.radioButton(key,q=True,sl=True)
			keySettingList.append(keySel)
		for value in [self.fromtextF,self.totextF]:
			setValue = cmds.textField(value,q=True,tx=True)
			try:
				fromToList.append(int(setValue))
			except ValueError:
				fromToList.append(0)
		return {
			'palette': paletteIndex,
			'paletteColor': paletteColor,

			'shapeIndexEnabled': cmds.checkBox(self.indexShape,q=True,v=True),
			'outlinerIndexEnabled': cmds.checkBox(self.indexOutliner,q=True,v=True),
			
			'controller': radioList,
			'shapeType': cmds.optionMenuGrp(self.shapeMenu,q=True,sl=True),
			
			'ctrlSize': cmds.floatSliderGrp(self.ctrlSizeIntF,q=True,v=True),
			'ctrlLineWidth': cmds.floatSliderGrp(self.ctrlThickIntF,q=True,v=True),
			
			'keySetting': keySettingList,
			'fromToData': fromToList,
			'sampleBy': cmds.textFieldGrp(self.BakeOntextField,q=True,tx=True)
		}

	def savepresetCmd(self):
		data = self.savePresetData()
		try:
			self.presetFolderCheck()
			if os.path.exists(self.scriptPresetPath):
				with open(self.scriptPresetPath, "r") as f:
					if f.read().strip():
						confirm = cmds.confirmDialog(
							title="Confirm Overwrite",
							message="A preset already exists. Do you want to replace it?",
							button=["Yes", "No"],
							defaultButton="No",
							cancelButton="No",
							dismissString="No"
						)
						if confirm == "No":
							cmds.warning("File not overwritten")
							return
			with open(self.scriptPresetPath, "w") as f:
				json.dump(data, f, indent=4)
			mel.eval('print ("REMINDER : Save Preset <COMPLETE> \\n")')
		except OSError as e:
			print("Error:", e)
			cmds.warning("Failed to create KF_PresetStore.")
	
	def obtainpresetData(self):
		try:
			with open(self.scriptPresetPath, "r") as f:
				return json.load(f)
		except IOError:
			cmds.warning("Failed to load preset file.")
			return None
	
	def loadpresetCmd(self):
		data = self.obtainpresetData()
		if not data:
			return
		cmds.palettePort(self.pale, e=True, scc=int(data.get("palette", 0)))
		cmds.checkBox(self.indexShape, e=True, v=data.get("shapeIndexEnabled", False))
		cmds.checkBox(self.indexOutliner, e=True, v=data.get("outlinerIndexEnabled", False))
		controller_list = data.get("controller", [True, False, False])
		# Radio buttons
		for i, (rdBtn, state) in enumerate(zip([self.ctrlLocator, self.ctrlNull, self.ctrlShape],controller_list)):
			if state:
				cmds.radioButton(rdBtn, e=True, sl=True)
				is_null = (i == 1)
				is_shape = (i == 2)
				cmds.floatSliderGrp(self.ctrlSizeIntF, e=True, en=not is_null)
				cmds.checkBox(self.indexShape, e=True, en=not is_null)
				cmds.optionMenuGrp(self.shapeMenu, e=True, vis=is_shape)
				cmds.text(self.ctrlSizeText,e=True,label="3. Size / Line Width :-" if is_shape else "3. Size :-")
				cmds.floatSliderGrp(self.ctrlThickIntF, e=True, vis=is_shape)
		cmds.optionMenuGrp(self.shapeMenu, e=True, sl=int(data.get("shapeType", 1)))
		cmds.floatSliderGrp(self.ctrlSizeIntF, e=True, v=float(data.get("ctrlSize", 1.0)))
		cmds.floatSliderGrp(self.ctrlThickIntF, e=True, v=float(data.get("ctrlLineWidth", 1.0)))
		key_list = data.get("keySetting", [True, False])
		for i, (key, state) in enumerate(zip([self.keyActive, self.keyFrom],key_list)):
			if state:
				cmds.radioButton(key, e=True, sl=True, en=state)
				if i == 1:
					cmds.textField(self.fromtextF, e=True, en=True)
					cmds.textField(self.totextF, e=True, en=True)
		from_to = data.get("fromToData", [])
		if len(from_to) == 2:
			cmds.textField(self.fromtextF, e=True, tx=str(from_to[0]))
			cmds.textField(self.totextF, e=True, tx=str(from_to[1]))
		cmds.textFieldGrp(self.BakeOntextField, e=True, tx=str(data.get("sampleBy", "1.0")))
	
		mel.eval('print ("REMINDER : Load Preset <COMPLETE> \\n")')

# when i run function it will load all these data , if not then it will run default that stored in SpaceSwitch_Func.py
# self.savePresetData()
	def createLocatorFunction(self, rotOrder):
		radioList = [self.switchSing,self.switchDoub,self.switchManual]
		for radio in radioList:
			radioSel = cmds.radioButton(radio,q=True,sl=True)
			if radioSel:
				selectedRadio = cmds.radioButton(radio,q=True,label=True)
				break
		if selectedRadio == "Single":
			spaceSwitch_Func.createLocatorSingle(rotOrder)
		elif selectedRadio == "Double":
			spaceSwitch_Func.createLocatorDouble(rotOrder)
		elif selectedRadio == "Manual":
			spaceSwitch_Func.createLocatorManual(rotOrder)


if __name__ == '__main__':
    try:
        spaceSwitch_UI()
    except:
        pass