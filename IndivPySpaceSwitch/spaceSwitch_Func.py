# -*- coding: utf-8 -*-
import os
import sys	
import json
import webbrowser
import math
import re
import maya.cmds as cmds
import maya.mel as mel

# ---- Save & Load Preset Data Here ---- #
DEFAULT_PRESET = {
	'palette': 0,
	'paletteColor': [1.000,1.000,1.000],
	'shapeIndexEnabled': False,
	'outlinerIndexEnabled': False,
	'controller': [False, False, True],
	'shapeType': 1,
	'ctrlSize': 2,
	'ctrlLineWidth': -1.0,
	'keySetting': [True, False],
	'fromToData': [0, 200],
	'sampleBy': '2.0'
}
scriptPresetFolderPath  = cmds.internalVar(userAppDir=True)+'scripts/KF_PresetStore'
scriptPresetPath = scriptPresetFolderPath + '/KF_SpaceSwitchPreset.json'

def obtainpresetData():
	if not os.path.exists(scriptPresetPath):
		cmds.warning("Preset file does not exist.")
		return DEFAULT_PRESET.copy()
	try:
		with open(scriptPresetPath, "r") as f:
			data = json.load(f)
	except Exception as e:
		cmds.warning("Failed to load preset file.")
		return DEFAULT_PRESET.copy()
	preset = DEFAULT_PRESET.copy()
	preset.update(data)
	# ---------- VALIDATION ----------
	# ctrlLineWidth
	lw = preset.get('ctrlLineWidth')
	if not isinstance(lw, (int, float)) or lw < 0:
		preset['ctrlLineWidth'] = DEFAULT_PRESET['ctrlLineWidth']
	# ctrlSize
	size = preset.get('ctrlSize')
	if not isinstance(size, (int, float)) or size <= 0:
		preset['ctrlSize'] = DEFAULT_PRESET['ctrlSize']
	# paletteColor
	col = preset.get('paletteColor')
	if (not isinstance(col, (list, tuple))) or len(col) != 3:
		preset['paletteColor'] = DEFAULT_PRESET['paletteColor']
	return preset
def loadpresetCmd():
    global returnList
    returnList = obtainpresetData()

def get_safe_time_range():
    return (int(math.floor(cmds.playbackOptions(q=True, min=True))),
			int(math.ceil(cmds.playbackOptions(q=True, max=True)))
			)

def ctrlCustomEdit(newName,typeCtrl,shapeCtrl):
	# controllerCurve
	shapeType = {
	0 : lambda :cmds.curve(d=1, n=newName, p=[(-1,0,0),(1,0,0),(0,0,0),(0,0,1),(0,0,-1),(0,0,0),(0,1,0),(0,-1,0)]), #locator
	1 : lambda :cmds.curve(d=1, n=newName, p=[(-0.75,0.75,0.75),(-0.75,0.75,-0.75),(0.75,0.75,-0.75),(0.75,0.75,0.75),(-0.75,0.75,0.75),
											(-0.75,-0.75,0.75),(0.75,-0.75,0.75),(0.75,0.75,0.75),(0.75,-0.75,0.75),(0.75,-0.75,-0.75),
											(0.75,0.75,-0.75),(0.75,-0.75,-0.75),(-0.75,-0.75,-0.75),(-0.75,0.75,-0.75),(-0.75,-0.75,-0.75),
											(-0.75,-0.75,0.75)]), #cube
	2 : lambda :cmds.curve(d=1, n=newName, p=[(0,0,-0.9975),(0.1575,0,-0.9835),(0.308,0,-0.9485),(0.4515,0,-0.889),(0.5845,0,-0.805),
											(0.7035,0,-0.7035),(0.805,0,-0.5845),(0.889,0,-0.4515),(0.9485,0,-0.308),(0.9835,0,-0.1575),
											(0.9975,0,0),(0.9835,0,0.1575),(0.9485,0,0.308),(0.889,0,0.4515),(0.805,0,0.5845),(0.7035,0,0.7035),
											(0.5845,0,0.805),(0.4515,0,0.889),(0.308,0,0.9485),(0.1575,0,0.9835),(0,0,0.9975),(-0.1575,0,0.9835),
											(-0.308,0,0.9485),(-0.4515,0,0.889),(-0.5845,0,0.805),(-0.7035,0,0.7035),(-0.805,0,0.5845),(-0.889,0,0.4515),
											(-0.9485,0,0.308),(-0.9835,0,0.1575),(-0.9975,0,0),(-0.9835,0,-0.1575),(-0.9485,0,-0.308),(-0.889,0,-0.4515),
											(-0.805,0,-0.5845),(-0.7035,0,-0.7035),(-0.5845,0,-0.805),(-0.4515,0,-0.889),(-0.308,0,-0.9485),(-0.1575,0,-0.9835),
											(0,0,-0.9975),(0,0.1575,-0.9835),(0,0.308,-0.9485),(0,0.4515,-0.889),(0,0.5845,-0.805),(0,0.7035,-0.7035),(0,0.805,-0.5845),
											(0,0.889,-0.4515),(0,0.9485,-0.308),(0,0.9835,-0.1575),(0,0.9975,0),(0,0.9835,0.1575),(0,0.9485,0.308),(0,0.889,0.4515),
											(0,0.805,0.5845),(0,0.7035,0.7035),(0,0.5845,0.805),(0,0.4515,0.889),(0,0.308,0.9485),(0,0.1575,0.9835),(0,0,0.9975),
											(0,-0.1575,0.9835),(0,-0.308,0.9485),(0,-0.4515,0.889),(0,-0.5845,0.805),(0,-0.7035,0.7035),(0,-0.805,0.5845),(0,-0.889,0.4515),
											(0,-0.9485,0.308),(0,-0.9835,0.1575),(0,-0.9975,0),(0,-0.9835,-0.1575),(0,-0.9485,-0.308),(0,-0.889,-0.4515),(0,-0.805,-0.5845),
											(0,-0.7035,-0.7035),(0,-0.5845,-0.805),(0,-0.4515,-0.889),(0,-0.308,-0.9485),(0,-0.1575,-0.9835),(0,0,-0.9975),(0,0.1575,-0.9835),
											(0,0.308,-0.9485),(0,0.4515,-0.889),(0,0.5845,-0.805),(0,0.7035,-0.7035),(0,0.805,-0.5845),(0,0.889,-0.4515),(0,0.9485,-0.308),
											(0,0.9835,-0.1575),(0,0.9975,0),(0.1575,0.9835,0),(0.308,0.9485,0),(0.4515,0.889,0),(0.5845,0.805,0),(0.7035,0.7035,0),(0.805,0.5845,0),
											(0.889,0.4515,0),(0.9485,0.308,0),(0.9835,0.1575,0),(0.9975,0,0),(0.9835,-0.1575,0),(0.9485,-0.308,0),(0.889,-0.4515,0),(0.805,-0.5845,0),
											(0.7035,-0.7035,0),(0.5845,-0.805,0),(0.4515,-0.889,0),(0.308,-0.9485,0),(0.1575,-0.9835,0),(0,-0.9975,0),(-0.1575,-0.9835,0),(-0.308,-0.9485,0),
											(-0.4515,-0.889,0),(-0.5845,-0.805,0),(-0.7035,-0.7035,0),(-0.805,-0.5845,0),(-0.889,-0.4515,0),(-0.9485,-0.308,0),(-0.9835,-0.1575,0),
											(-0.9975,0,0),(-0.9835,0.1575,0),(-0.9485,0.308,0),(-0.889,0.4515,0),(-0.805,0.5845,0),(-0.7035,0.7035,0),(-0.5845,0.805,0),(-0.4515,0.889,0),
											(-0.308,0.9485,0),(-0.1575,0.9835,0),(0,0.9975,0)]), #sphere
	3 : lambda :cmds.curve(d=1, n=newName, p=[(0,1,0),(1,0,0),(0,0,1),(-1,0,0),(0,0,-1),(0,1,0),(0,0,1),(0,-1,0),(0,0,-1),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0),(1,0,0)]), #rhombus
	4 : lambda :cmds.curve(d=1, n=newName, p=[(0,0.75,-0.786),(0.123,0.75,-0.777),(0.243,0.75,-0.747),(0.357,0.75,-0.699),
											(0.462,0.75,-0.636),(0.555,0.75,-0.555),(0.636,0.75,-0.462),(0.699,0.75,-0.357),(0.747,0.75,-0.243),(0.777,0.75,-0.123),
											(0.786,0.75,0),(0.777,0.75,0.123),(0.747,0.75,0.243),(0.699,0.75,0.357),(0.636,0.75,0.462),(0.555,0.75,0.555),
											(0.462,0.75,0.636),(0.357,0.75,0.699),(0.243,0.75,0.747),(0.123,0.75,0.777),(0,0.75,0.786),(-0.123,0.75,0.777),
											(-0.243,0.75,0.747),(-0.357,0.75,0.699),(-0.462,0.75,0.636),(-0.555,0.75,0.555),(-0.636,0.75,0.462),(-0.699,0.75,0.357),
											(-0.747,0.75,0.243),(-0.777,0.75,0.123),(-0.786,0.75,0),(-0.777,0.75,-0.123),(-0.747,0.75,-0.243),(-0.699,0.75,-0.357),
											(-0.636,0.75,-0.462),(-0.555,0.75,-0.555),(-0.462,0.75,-0.636),(-0.357,0.75,-0.699),(-0.243,0.75,-0.747),(-0.123,0.75,-0.777),
											(0,0.75,-0.786),(0,-0.75,-0.786),(0.123,-0.75,-0.777),(0.243,-0.75,-0.747),(0.357,-0.75,-0.699),(0.462,-0.75,-0.636),
											(0.555,-0.75,-0.555),(0.555,0.75,-0.555),(0.555,-0.75,-0.555),(0.636,-0.75,-0.462),(0.699,-0.75,-0.357),(0.747,-0.75,-0.243),
											(0.777,-0.75,-0.123),(0.786,-0.75,0),(0.786,0.75,0),(0.786,-0.75,0),(0.777,-0.75,0.123),(0.747,-0.75,0.243),
											(0.699,-0.75,0.357),(0.636,-0.75,0.462),(0.555,-0.75,0.555),(0.555,0.75,0.555),(0.555,-0.75,0.555),(0.462,-0.75,0.636),
											(0.357,-0.75,0.699),(0.243,-0.75,0.747),(0.123,-0.75,0.777),(0,-0.75,0.786),(0,0.75,0.786),(0,-0.75,0.786),
											(-0.123,-0.75,0.777),(-0.243,-0.75,0.747),(-0.357,-0.75,0.699),(-0.462,-0.75,0.636),(-0.555,-0.75,0.555),
											(-0.555,0.75,0.555),(-0.555,-0.75,0.555),(-0.636,-0.75,0.462),(-0.699,-0.75,0.357),(-0.747,-0.75,0.243),
											(-0.777,-0.75,0.123),(-0.786,-0.75,0),(-0.786,0.75,0),(-0.786,-0.75,0),(-0.777,-0.75,-0.123),(-0.747,-0.75,-0.243),
											(-0.699,-0.75,-0.357),(-0.636,-0.75,-0.462),(-0.555,-0.75,-0.555),(-0.555,0.75,-0.555),(-0.555,-0.75,-0.555),
											(-0.462,-0.75,-0.636),(-0.357,-0.75,-0.699),(-0.243,-0.75,-0.747),(-0.123,-0.75,-0.777),(0,-0.75,-0.786)]) #cylinder
	}
	ctrlType = {
	0: lambda: cmds.spaceLocator(n=newName)[0],
	1: lambda: cmds.group(n=newName,em=True), #unicode
	2: shapeType[shapeCtrl] 
	}
	ctrlCreate = ctrlType[typeCtrl]()
	ctrlChild = cmds.listRelatives(ctrlCreate, children=True, type='shape')
	if ctrlChild:
		for child in ctrlChild:
			cmds.rename(child, "{}Shape".format(ctrlCreate))
	return ctrlCreate

def ctrlSettingFunc(sel,rotOrder):
	ctrlList = []
	shapeType = returnList["shapeType"]	# ShapeType
	shapeType = int(shapeType)-1
	ctrlType = returnList["controller"] # ControllerType
	indexclr = returnList["paletteColor"] # RGBColor
	# Ensure returnList[2] and returnList[3] are always lists
	# zip() requires iterables, so single booleans (True/False) cause errors.
	shape_list = returnList["shapeIndexEnabled"] # ShapeTick
	outliner_list = returnList["outlinerIndexEnabled"] # OutlinerTick
	for i,type in enumerate(ctrlType):
		if type: # Which is selection
			newCreatedName = ("{}_locBake_{}".format(sel,rotOrder))	
			if cmds.objExists(newCreatedName):
				confirmLog = cmds.confirmDialog(title="Object Already Exists",
												message="The object '{}' already exists in the scene.\nDo you still want to proceed?".format(newCreatedName),
												button=["Yes","No"],
												defaultButton="No",
												cancelButton="No",
												dismissString="No"
												)
				if confirmLog == "No" :
					cmds.warning("This step is cancel")
					cmds.select(newCreatedName)
					return
			newName = ctrlCustomEdit(newCreatedName,i,shapeType)
			ctrlList.append(newName)
			if shape_list:
				if i != 1: # Not Null
					selLR = cmds.listRelatives(newName, children=True, type='shape')[0]
					if selLR:
						cmds.setAttr("{}.overrideEnabled".format(selLR), 1)
						cmds.setAttr("{}.overrideRGBColors".format(selLR), 1)
						cmds.setAttr("{}.overrideColorRGB".format(selLR), indexclr[0], indexclr[1], indexclr[2])
			if outliner_list:
				cmds.setAttr("{}.useOutlinerColor".format(newName), 1)
				cmds.setAttr("{}.outlinerColor".format(newName), indexclr[0], indexclr[1], indexclr[2])
			if i == 0 or i == 2:
				for attr in ['.sx', '.sy', '.sz']:
					cmds.setAttr("{}{}".format(newName, attr), int(returnList["ctrlSize"])) # ScaleSize
				if i == 2:
					selLRC = cmds.listRelatives(newName, children=True, type='shape')[0]
					if selLRC:
						cmds.setAttr("{}.lineWidth".format(selLRC), int(returnList["ctrlLineWidth"]))
	return ctrlList
#    ____________________
# __/__FunctionColumn __/__
# Modify so every button will share the same function 
def createLocatorSingle(rotateOrder):
	loadpresetCmd()
	ROTATE_ORDER_MAP = {
    "XYZ": 0,
    "YZX": 1,
    "ZXY": 2,
    "XZY": 3,
    "YXZ": 4,
    "ZYX": 5
	}
	objectsel = cmds.ls(sl=True)
	if not objectsel:
		cmds.warning("SELECT A CONTROLLER TO FUNCTION")
		return []
	minTime, maxTime = get_safe_time_range()
	createdCtrls = []
	cmds.undoInfo(openChunk=True)
	cmds.refresh(suspend=True)
	cmds.progressWindow(title='Working...',progress=0,maxValue=len(objectsel),status='Progress : 0%',isInterruptable=True)
	try:
		for i,obj in enumerate(objectsel,start=1):
			if cmds.progressWindow(q=True,isCancelled=True):
				break
			ctrlList = ctrlSettingFunc(obj,rotateOrder)
			if not ctrlList:
				return
			ctrl = ctrlList[0]
			createdCtrls.append(ctrl)
			prtCnt = cmds.parentConstraint(obj, ctrl, mo=False)[0]
			cmds.setAttr("{}.rotateOrder".format(ctrl), ROTATE_ORDER_MAP[rotateOrder])
			cmds.bakeResults(ctrl,
							 time=(minTime,maxTime),
							 simulation=True,
							 hierarchy='none',
							 oversamplingRate=1,
							 disableImplicitControl=False,
							 preserveOutsideKeys =True,
							 removeBakedAttributeFromLayer=False,
							 bakeOnOverrideLayer=False,
							 controlPoints=False,
							 shape=True,
							 )
			cmds.delete(prtCnt)
			cmds.parentConstraint(ctrl,obj,mo=True)
			animCurves = cmds.listConnections(ctrl, d=False, type='animCurve')
			if animCurves:
				cmds.filterCurve(animCurves)
			cmds.progressWindow(e=True,progress=i,status='Progress : {}%'.format(int((float(i)/len(objectsel))*100)))
	finally:
		cmds.progressWindow(endProgress=True)
		cmds.refresh(suspend=False)
		cmds.undoInfo(closeChunk=True)
	if createdCtrls:
		mel.eval('print("RESULT: <{}> locator CREATED\\n")'.format(len(createdCtrls)))	
	return createdCtrls

def createLocatorDouble(rotateOrder):
	loadpresetCmd()
	ROTATE_ORDER_XFORM = {
    "XYZ": "xyz",
    "YZX": "yzx",
    "ZXY": "zxy",
    "XZY": "xzy",
    "YXZ": "yxz",
    "ZYX": "zyx",
	}
	objectsel = cmds.ls(sl=True)
	if not objectsel:
		cmds.warning("SELECT A CONTROLLER TO FUNCTION")
		return []
	minTime, maxTime = get_safe_time_range()

	createdCtrls = []
	cmds.undoInfo(openChunk=True)
	cmds.refresh(suspend=True)
	cmds.progressWindow(title='Working...',progress=0,maxValue=len(objectsel),status='Progress : 0%',isInterruptable=True)
	try:
		for i,obj in enumerate(objectsel,start=1):
			if cmds.progressWindow(q=True,isCancelled=True):
				break
			ctrlList = ctrlSettingFunc(obj,rotateOrder)
			if not ctrlList:
				return
			ctrl = ctrlList[0]
			createdCtrls.append(ctrl)
			prtCnt = cmds.parentConstraint(obj, ctrl, mo=False)[0]
			cmds.delete(prtCnt)
			cmds.xform(ctrl,p=True,rotateOrder=ROTATE_ORDER_XFORM[rotateOrder])
			ctrlChild = cmds.duplicate(ctrl,n="{}_child".format(ctrl))[0]
			cmds.parent(ctrlChild,ctrl)
			prtChildCnt = cmds.parentConstraint(obj, ctrlChild, mo=False)[0]
			cmds.bakeResults(ctrlChild,
							 time=(minTime,maxTime),
							 simulation=True,
							 hierarchy='none',
							 oversamplingRate=1,
							 disableImplicitControl=False,
							 preserveOutsideKeys =True,
							 removeBakedAttributeFromLayer=False,
							 bakeOnOverrideLayer=False,
							 controlPoints=False,
							 shape=True,
							 )
			cmds.delete(prtChildCnt)
			cmds.orientConstraint(ctrlChild,obj,mo=True)
			animCurves = cmds.listConnections(ctrlChild, d=False, type='animCurve')
			if animCurves:
				cmds.filterCurve(animCurves)
			cmds.progressWindow(e=True,progress=i,status='Progress : {}%'.format(int((float(i)/len(objectsel))*100)))
	finally:
		cmds.progressWindow(endProgress=True)
		cmds.refresh(suspend=False)
		cmds.undoInfo(closeChunk=True)
	if createdCtrls:
		mel.eval('print("RESULT: <{}> locator CREATED\\n")'.format(len(createdCtrls)))	
	return createdCtrls
#=========================================================================================================================================
#    _________________________
# __/__ManualLocator SETUP __/__
def pivRot(obj):
	if cmds.objectType(obj)=="transform" or cmds.objectType(obj)=="joint": #locator also consider as transform                                
		piv= cmds.xform(obj, q=1, rp=1, ws=1)
		rot = cmds.getAttr("{}.rotate".format(obj))[0]
		rotOr= cmds.getAttr("{}.rotateOrder".format(obj))
	elif cmds.objectType(obj)=="mesh" or cmds.objectType(obj)=="nurbsCurve" or cmds.objectType(obj)=="nurbsSurface":   
		tempPiv= cmds.exactWorldBoundingBox(obj)
		piv= [round((tempPiv[0]+tempPiv[3])/2, 3), round((tempPiv[1]+tempPiv[4])/2, 3), round((tempPiv[2]+tempPiv[5])/2, 3)]
		rot= [0,0,0]
		rotOr= 0 # xyz
	return piv, rot, rotOr
def pivCent(obj):
    px, py, pz = [], [], []
    for obj in obj:
        piv, _, _ = pivRot(obj)
        px.append(piv[0])
        py.append(piv[1])
        pz.append(piv[2])
    piv = [
        round((min(px) + max(px)) / 2, 3),
        round((min(py) + max(py)) / 2, 3),
        round((min(pz) + max(pz)) / 2, 3),
    ]
    return piv

def clean_name(name):
    return re.sub("_+", "_", name).strip("_")
def clean_name_keep_namespace(obj_name):
    if ":" in obj_name:
        ns, base = obj_name.rsplit(":", 1)
        return "{}:{}".format(ns, clean_name(base))
    return clean_name(obj_name)

def createLocatorManual(rotOrder):
	loadpresetCmd()
	ROTATE_ORDER_MAP = {
    "XYZ": 0,
    "YZX": 1,
    "ZXY": 2,
    "XZY": 3,
    "YXZ": 4,
    "ZYX": 5
	}
	sel_objs  = cmds.ls(sl=True) # mesh ,joint ,locator ,nurbs
	if not sel_objs :
		cmds.warning("SELECT SOMETHING TO FUNCTION")
		return []
	cmds.undoInfo(openChunk=True)
	createdCtrls = []
	try:
		center_piv = pivCent(sel_objs)
		ctrlList = ctrlSettingFunc(sel_objs[0], rotOrder)  # just pass first selection
		if not ctrlList:
			return
		ctrl = ctrlList[0]
		createdCtrls.append(ctrl)
		cmds.xform(ctrl, ws=True, t=center_piv)
		cmds.matchTransform(ctrl, sel_objs[0], rot=True)
		cmds.setAttr("{}.rotateOrder".format(ctrl), ROTATE_ORDER_MAP[rotOrder])
		ctrl = cmds.rename(ctrl,"{}_Manual".format(clean_name_keep_namespace(ctrl)))
		mel.eval('print("RESULT: <{}> locator CREATED\\n")'.format(ctrl))
	finally:
		cmds.undoInfo(closeChunk=True)
	return createdCtrls
'''
def LocRename():
	selection = cmds.ls(sl=True)
	if len(selection) != 2 :
		cmds.warning("SELECT ONE SOURCE AND ONE TARGET")
	else:
		newLocName = ("{}_align_locBake_XYZ".format(selection[0]))
		if cmds.objExists(newLocName):
			cmds.select(newLocName)
			cmds.warning("{} already <EXIST> , please Check".format(newLocName))
		else:
			cmds.rename(selection[-1],newLocName)
'''
def LocManualBake():
    loadpresetCmd()
    minTime, maxTime = get_safe_time_range()
    locBakeAXYZ = cmds.ls(sl=True)
    if not locBakeAXYZ:
        cmds.warning("Please select locator(s) to bake")
        return []
    cmds.undoInfo(openChunk=True)
    cmds.refresh(suspend=True)
    cmds.progressWindow(title='Baking Manual Locators',
                        progress=0,
                        maxValue=len(locBakeAXYZ),
                        status='Progress : 0%',
                        isInterruptable=True)
    try:
        for i, each in enumerate(locBakeAXYZ, start=1):
            if cmds.progressWindow(q=True, isCancelled=True):
                break
            parts = each.split(":")
            ns = parts[0] if len(parts) > 1 else ""
            base_name = parts[-1]
            # check suffix pattern
            pattern = r".*_locBake_.*_Manual$"
            if not re.match(pattern, base_name):
                cmds.warning("Selection locator suffix different, please check the naming: {}".format(each))
                continue
            # rebuild source object (with namespace if exists)
            source_base = base_name.split("_locBake_")[0]
            source = "{}:{}".format(ns, source_base) if ns else source_base
            prtCnt = cmds.parentConstraint(source, each, mo=True)
            cmds.bakeResults(each,
                             time=(minTime, maxTime),
                             simulation=True,
                             hierarchy='none',
                             oversamplingRate=1,
                             disableImplicitControl=False,
                             preserveOutsideKeys=True,
                             removeBakedAttributeFromLayer=False,
                             bakeOnOverrideLayer=False,
                             controlPoints=False,
                             shape=True)
            cmds.delete(prtCnt)
            cmds.parentConstraint(each, source, mo=True)
            animCurves = cmds.listConnections(each, d=False, type='animCurve')
            if animCurves:
                cmds.filterCurve(animCurves)
            for obj_sel in [each]:
                for attr in ['.sx', '.sy', '.sz', '.v']:
                    cmds.setAttr(obj_sel + attr, l=True, k=False, cb=False)
            cmds.progressWindow(e=True,
                                progress=i,
                                status='Progress : {}%'.format(int((float(i)/len(locBakeAXYZ))*100)))
            mel.eval('print("RESULT: <{}> locator bake complete\\n")'.format(each))

    finally:
        cmds.progressWindow(endProgress=True)
        cmds.refresh(suspend=False)
        cmds.undoInfo(closeChunk=True)

#    _____________________________
# __/__ManualLocator SETUP END __/__
#=========================================================================================================================================

#=========================================================================================================================================
#    _______________________________
# __/__AnimationLayer SETUP START__/__
# Select object from layers
def selectObjectsFromLayers(anim_layers):
	objects = set()
	for anim_layer in anim_layers:
		attrs = cmds.animLayer(anim_layer, q=True, attribute=True) or []
		for attr in attrs:
			objects.add(attr.split('.', 1)[0])
	objects = list(objects)
	if objects:
		cmds.select(objects)
	return objects
def getAllLayers(depth=0):
	root = cmds.animLayer(q=True,r=True)
	if not root:
		return []
	result = []
	def walk(layer):
		children = cmds.animLayer(layer,q=True,children=True)
		for child in children:
			result.append(child)
			walk(child)
	walk(root)
	return result
def checkEmptyAnimLayerAllTheWay(layer):
    if cmds.animLayer(layer, q=True, attribute=True):
        return False
    children = cmds.animLayer(layer, q=True, children=True) or []
    return all(checkEmptyAnimLayerAllTheWay(c) for c in children)
def deleteEmptyLayers():
    allLayers = getAllLayers()
    if not allLayers:
        return
    toDelete = [l for l in allLayers if checkEmptyAnimLayerAllTheWay(l)]
    if toDelete:
        cmds.delete(toDelete)
def removeFromAnimLayer(node):
    cmds.select(node)
    affected = cmds.animLayer(q=True, affectedLayers=True) or []
    if not affected:
        mel.eval('print ("REMINDER : {} does not belong to any animation layer\\n")'.format(node))
        return
    root = cmds.animLayer(q=True, root=True)
    if root in affected:
        affected.remove(root)
    attrs = cmds.listAttr(node, keyable=True) or []
    attrs = ["{}.{}".format(node, a) for a in attrs]
    locked = cmds.listAttr(node, locked=True, keyable=True) or []
    locked = {"{}.{}".format(node, a) for a in locked}
    attrs = [a for a in attrs if a not in locked]
    for layer in affected:
        cmds.animLayer(layer, e=True, removeAttribute=attrs)
    if cmds.animLayer(q=True, affectedLayers=True):
        cmds.warning("got error")
    else:
        mel.eval('print ("REMINDER : {} Animation Layers merged\\n")'.format(node))

# Get back target constraint list
def getTargetConstraint(sel):
    cons = cmds.listConnections(sel, type='constraint', plugs=True) or []
    return list({c.split('.', 1)[0] for c in cons if '.targetParentMatrix' in c})
def getActualTarget(sel):
    """
    Returns transforms directly driven by constraints on sel, skipping the sel itself.
    """
    if not cmds.objExists(sel):
        return []

    driven = set()
    constraints = cmds.listConnections(sel, type='constraint') or []
    for con in constraints:
        # get all downstream connections from the constraint
        outputs = cmds.listConnections(con, s=False, d=True) or []
        for out in outputs:
            if cmds.objExists(out) and cmds.nodeType(out) == 'transform':
                if out != sel:  # skip the constrained object itself
                    driven.add(out)
    return list(driven)
def filterTransforms(nodes):
    return [n for n in nodes if cmds.objExists(n) and cmds.nodeType(n) == 'transform']
def getPairDrivenTarget(sel):
    """
    Returns the final transform nodes driving the selected object,
    skipping intermediate nodes like pairBlend but following them to the real target.
    """
    if not cmds.objExists(sel):
        return []
    final_drivers = set()
    constraints = cmds.listConnections(sel, type='constraint') or []
    for con in constraints:
        downstream = cmds.listConnections(con, s=False, d=True) or []
        for node in downstream:
            if not cmds.objExists(node):
                continue
            node_type = cmds.nodeType(node)
            if node_type == 'pairBlend':
                # follow pairBlend output to find the actual transform
                pairblend_outputs = cmds.listConnections(node, s=False, d=True) or []
                for out in pairblend_outputs:
                    if cmds.objExists(out) and cmds.nodeType(out) == 'transform':
                        final_drivers.add(out)
    return list(final_drivers)
#    _____________________________
# __/__AnimationLayer SETUP END__/__
#=========================================================================================================================================
def bakeFunction(progressBar=None):
	sels = cmds.ls(sl=True)
	if not sels:
		return cmds.warning("SELECT OBJECT TO BAKE ANIMATION")
	selectionReplacesNew = []
	timeSlider = returnList["keySetting"]
	timeData = returnList["fromToData"]
	sampleData = returnList["sampleBy"]

	if timeSlider[0] == True: # TimeSlider
		minTime, maxTime = get_safe_time_range()
	else:
		minTime,maxTime = timeData[0],timeData[-1]	
	for obj in sels:
		targets = getActualTarget(obj)
		if not targets:
			targets = getPairDrivenTarget(obj)
		selectionReplacesNew.extend(targets)
	if not selectionReplacesNew:
		return cmds.warning("NO CONSTRAINT SOURCES FOUND TO BAKE ANIMATION")
	selectionReplacesNew = filterTransforms(selectionReplacesNew)
	total = len(selectionReplacesNew)
	if not total:
		return cmds.warning("No valid transforms to bake.")
	if progressBar and cmds.progressBar(progressBar, exists=True):
		cmds.progressBar(progressBar, e=True, progress=0)
	cmds.undoInfo(openChunk=True)
	cmds.refresh(suspend=True)
	try:
		total = len(selectionReplacesNew)
		for i, (source, target) in enumerate(zip(selectionReplacesNew, sels), 1):
			progress = (float(i) / total) * 100.0
			cmds.refresh(suspend=True)
			cmds.bakeResults(source,
						time=(minTime,maxTime),
						simulation=True,
						hierarchy='none',
						oversamplingRate=1,
						disableImplicitControl=False,
						preserveOutsideKeys =True,
						removeBakedAttributeFromLayer=False,
						bakeOnOverrideLayer=False,
						controlPoints=False,
						shape=True,
						sampleBy=sampleData
						)
			cmds.delete(target)
			removeFromAnimLayer(source)
			cmds.refresh(suspend=False)

			if progressBar and cmds.progressBar(progressBar, exists=True):
				percent = int((float(i) / total) * 100)
				cmds.progressBar(progressBar, e=True, progress=percent)
	finally:
		if progressBar and cmds.progressBar(progressBar, exists=True):
			cmds.progressBar(progressBar, e=True, progress=100)
		cmds.refresh(suspend=False)
		cmds.undoInfo(closeChunk=True)

	deleteEmptyLayers()
	cmds.select(selectionReplacesNew)
	showBakeCompleteWindow(selectionReplacesNew)

def showBakeCompleteWindow(objects):
	if not objects:
		return
	num = len(objects)
	win = "ControllerBake_List"
	if cmds.window(win, exists=True):
		cmds.deleteUI(win)
	window = cmds.window(win, title="Bake Complete", widthHeight=(400, 200))
	form = cmds.formLayout()
	frame = cmds.frameLayout(label="[{}] Objects baked successfully".format(num),marginWidth=10,marginHeight=10, bgc=(0.2, 0.35, 0.2))
	scroll = cmds.textScrollList(allowMultiSelection=True,append=objects,dcc=lambda *_: cmds.select(cmds.textScrollList(scroll, q=True, selectItem=True)))
	cmds.formLayout(form, e=True,attachForm=[(frame, 'top', 5),(frame, 'bottom', 5),(frame, 'left', 5),(frame, 'right', 5)])
	cmds.showWindow(window)
	mel.eval('print ("REMINDER : Selection COMPLETE BAKE :D\\n")')

def setupFunction():
	cmds.refresh(suspend=True) # Off
	try:
		list = bakeFunction("XYZ",0)
		if list:
			cmds.select(list)
			mel.eval( 'print ("\\nREMINDER : SpaceSwitch <CREATED> \\n")')
	except:
		cmds.refresh(suspend=False)
		cmds.error('Error during the Bake')
	cmds.refresh(suspend=False)