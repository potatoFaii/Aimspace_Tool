# -*- coding: utf-8 -*-
import math
import maya.cmds as cmds
import maya.mel as mel

def _bake_nodes(nodes, min_time, max_time):
    if not nodes:
        return
    cmds.bakeResults(
        nodes,
        time=(min_time, max_time),
        simulation=True,
        hierarchy="none",
        oversamplingRate=1,
        disableImplicitControl=False,
        preserveOutsideKeys=True,
        removeBakedAttributeFromLayer=False,
        bakeOnOverrideLayer=False,
        controlPoints=False,
        shape=True
    )

def get_safe_time_range():
    return (int(math.floor(cmds.playbackOptions(q=True, min=True))),
            int(math.ceil(cmds.playbackOptions(q=True, max=True))))

def spawnAimLocators(obj, axis, distance, sign=1):
    """
    Create root / offset / target temp aimspace locators for one object.
    Returns: (root, off, tar)
    """
    axis_vectors = {
        "X": (1, 0, 0),
        "Y": (0, 1, 0),
        "Z": (0, 0, 1)
    }

    if axis not in axis_vectors:
        cmds.warning("Invalid axis: {}".format(axis))
        return None

    root_name = "{}_temp_aimspace_root".format(obj)
    off_name  = "{}_temp_aimspace_offset".format(obj)
    tar_name  = "{}_temp_aimspace_target".format(obj)

    existing = [n for n in (root_name, off_name, tar_name) if cmds.objExists(n)]
    if existing:
        cmds.warning("Temp aimspace nodes already exist: {}".format(", ".join(existing)))
        return None

    root = createDisplayLocator(root_name)
    off  = createDisplayLocator(off_name, parent=root)
    tar  = createDisplayLocator(tar_name, scale=(25, 25, 25), color=(0, 0.6, 0.6))

    # snap root and target to source object first
    tmp_root = cmds.parentConstraint(obj, root, mo=False)
    tmp_tar  = cmds.parentConstraint(obj, tar, mo=False)
    cmds.delete(tmp_root, tmp_tar)

    # push target along selected axis
    axis_vec = axis_vectors[axis]
    offset = tuple(v * distance * sign for v in axis_vec)
    cmds.xform(tar, r=True, os=True, t=offset)

    return root, off, tar

def generateLoc(axis, sliderCtrl=None, posNegToggle=None):
    """
    Only generate temp locators + reference curve for selected objects.
    No bake, no aimConstraint, no final setup.
    """
    sel = cmds.ls(sl=True, type="transform") or []
    if not sel:
        cmds.warning("You need to select controller first")
        return []

    if sliderCtrl:
        distance = cmds.intSliderGrp(sliderCtrl, q=True, v=True)
    else:
        distance = 50

    sign = 1
    if posNegToggle:
        is_positive = cmds.checkBox(posNegToggle, q=True, v=True)
        sign = 1 if is_positive else -1

    # collect all existing first
    existing_nodes = []
    for obj in sel:
        for name in (
            "{}_temp_aimspace_root".format(obj),
            "{}_temp_aimspace_offset".format(obj),
            "{}_temp_aimspace_target".format(obj)
        ):
            if cmds.objExists(name):
                existing_nodes.append(name)

    if existing_nodes:
        existing_nodes = sorted(set(existing_nodes))
        cmds.select(existing_nodes, r=True)
        cmds.warning(
            "Temp aimspace nodes already exist. Remove them first:\n{}".format(
                ", ".join(existing_nodes)
            )
        )
        return []

    created_tars = []

    cmds.undoInfo(openChunk=True)
    try:
        cmds.refresh(suspend=True)
        try:
            for obj in sel:
                result = spawnAimLocators(obj, axis, distance, sign)
                if not result:
                    continue

                root, off, tar = result
                buildAimReference(off, tar)
                created_tars.append(tar)

                mel.eval('print ("RESULT : {} locator generate <COMPLETE>\\n")'.format(obj))
        finally:
            cmds.refresh(suspend=False)
    finally:
        cmds.undoInfo(closeChunk=True)

    if created_tars:
        cmds.select(created_tars, r=True)

    return created_tars

def createLocFunction(txMnl=None, tyMnl=None, tzMnl=None, cbWorldMn1=None):
    minTime, maxTime = get_safe_time_range()
    selLoc = cmds.ls(sl=True) or []
    if not selLoc:
        cmds.warning("Please select temp aimspace locator(s) to create aimConstraint")
        return

    bases = []
    for loc in selLoc:
        if "_temp_aimspace_" not in loc:
            continue
        base = loc.split("_temp_aimspace", 1)[0]
        if base not in bases:
            bases.append(base)

    if not bases:
        cmds.warning("Selection not '{}' ,please check".format("_temp_aimspace_"))
        return
    
    def doAim(target_node, offset_node, root_node, aimVec, upVec):
        cmds.aimConstraint(target_node, offset_node,
                            mo=True,
                            aimVector=aimVec,
                            upVector=upVec,
                            worldUpVector=upVec,
                            worldUpType='objectrotation',
                            worldUpObject=root_node)
    
    axisData = [
        (txMnl, "X", (1, 0, 0), (-1, 0, 0), (0, 0, 1)),
        (tyMnl, "Y", (0, 1, 0), (0, -1, 0), (0, 0, 1)),
        (tzMnl, "Z", (0, 0, 1), (0, 0, -1), (0, 1, 0)),
    ]

    selected_axis_data = None
    for btn, axis, posAim, negAim, upVec in axisData:
        if not btn:
            continue
        if cmds.radioButton(btn, q=True, select=True):
            selected_axis_data = (axis, posAim, negAim, upVec)
            break

    if selected_axis_data is None:
        selected_axis_data = ("X", (1, 0, 0), (-1, 0, 0), (0, 0, 1))

    if cbWorldMn1:
        world = cmds.checkBox(cbWorldMn1, q=True, value=True)
    else:
        world = False

    prepared_items = []
    bake_nodes = []
    temp_constraints = []

    for base in bases:
        target = "{}_temp_aimspace_target".format(base)
        root = "{}_temp_aimspace_root".format(base)
        offset = "{}_temp_aimspace_offset".format(base)

        missing_nodes = [node for node in (target, root, offset) if not cmds.objExists(node)]
        if missing_nodes:
            cmds.warning("Missing temp nodes for [{}]: {}".format(base, ", ".join(missing_nodes)))
            continue

        existing_target_constraints = cmds.listConnections(target, s=True, type="constraint") or []
        if existing_target_constraints:
            try:
                cmds.delete(list(set(existing_target_constraints)))
            except Exception as e:
                cmds.warning("Failed to clear existing constraints on [{}]: {}".format(target, e))
                continue

        try:
            prt_target = cmds.parentConstraint(base, target, mo=True)[0]
            prt_root = cmds.parentConstraint(base, root, mo=True)[0]
        except Exception as e:
            cmds.warning("Failed to create bake parentConstraint for [{}]: {}".format(base, e))
            continue

        temp_constraints.extend([prt_target, prt_root])
        bake_nodes.extend([target, root])
        prepared_items.append((base, target, root, offset))

    if not prepared_items:
        cmds.warning("No valid temp aimspace setup found in selection")
        return

    unique_bake_nodes = list(dict.fromkeys(bake_nodes))

    cmds.undoInfo(openChunk=True)
    try:
        cmds.refresh(suspend=True)
        try:
            print(unique_bake_nodes)
            _bake_nodes(unique_bake_nodes, minTime, maxTime)
            cmds.filterCurve(*unique_bake_nodes)
            if temp_constraints:
                cmds.delete(temp_constraints)

            axis, posAim, negAim, upVec = selected_axis_data
            final_targets = []
            for base, target, root, offset in prepared_items:
                cmds.setAttr("{}.rotate".format(offset), 0, 0, 0)

                tgtVal = cmds.getAttr("{}.translate{}".format(target, axis))
                srcVal = cmds.getAttr("{}.translate{}".format(base, axis))
                if tgtVal >= srcVal:
                    mel.eval('print ("RESULT : +{} created\\n")'.format(axis))
                    doAim(target, offset, root, posAim, upVec)
                else:
                    mel.eval('print ("RESULT : -{} created\\n")'.format(axis))
                    doAim(target, offset, root, negAim, upVec)

                if world:
                    cmds.pointConstraint(root, base)
                else:
                    cmds.pointConstraint(base, root)
                cmds.orientConstraint(offset, base)
                final_targets.append(target)
                mel.eval('print ("RESULT : [{}] manual create <COMPLETE>\\n")'.format(target))

            cmds.select(deselect=True)
            if final_targets:
                cmds.select(final_targets)
        finally:
            cmds.refresh(suspend=False)
    finally:
        cmds.undoInfo(closeChunk=True)

def createDisplayLocator(name,parent=None,scale=1,color=None):
    loc = cmds.spaceLocator(n=name)[0]
    # localScale (support scalar or 3-tuple)
    if isinstance(scale, (list, tuple)) and len(scale) == 3:
        x_scale, y_scale, z_scale = scale
    else:
        x_scale = y_scale = z_scale = float(scale)

    cmds.setAttr("{}.localScaleX".format(loc), x_scale)
    cmds.setAttr("{}.localScaleY".format(loc), y_scale)
    cmds.setAttr("{}.localScaleZ".format(loc), z_scale)
    cmds.setAttr("{}.v".format(loc), l=True,k=False,cb=False)
    if color is not None:
        cmds.setAttr("{}.overrideEnabled".format(loc), 1)
        cmds.setAttr("{}.overrideRGBColors".format(loc), 1)
        cmds.setAttr("{}.overrideColorR".format(loc), color[0])
        cmds.setAttr("{}.overrideColorG".format(loc), color[1])
        cmds.setAttr("{}.overrideColorB".format(loc), color[2])
    # parent
    if parent and cmds.objExists(parent):
        cmds.parent(loc, parent)
    return loc

def _node_name(node):
    return node.rsplit("|", 1)[-1]
    
def crvSpawn(off,tar):
    if not cmds.objExists(off):
        cmds.warning("{} does not exist".format(off))
        return None
    if not cmds.objExists(tar):
        cmds.warning("{} does not exist".format(tar))
        return None
    tarBase = _node_name(tar)
    curveName = "{}_CRV".format(tarBase)
    if cmds.objExists(curveName):
        cmds.warning("{} <EXIST>".format(curveName))
        return curveName
    offPos = cmds.xform(off, q=True, ws=True, t=True)
    tarPos = cmds.xform(tar, q=True, ws=True, t=True)
    if offPos == tarPos:
        cmds.warning("Skipping {}: off and tar are at same position".format(curveName))
        return None
    newCurve = cmds.curve(n=curveName, d=1, p=[offPos, tarPos])
    shape = cmds.listRelatives(newCurve, c=True, s=True, type='nurbsCurve')
    if shape:
        shape = shape[0]
        cmds.setAttr("{}.lineWidth".format(shape), 3)
        cmds.setAttr("{}.overrideEnabled".format(shape), 1)
        cmds.setAttr("{}.overrideDisplayType".format(shape), 2)
        cmds.setAttr("{}.useOutlinerColor".format(newCurve), 1)
        cmds.setAttr("{}.outlinerColor".format(newCurve), 0.5, 0.5, 0.5)
        desiredShapeName = "{}Shape".format(curveName)
        if shape != desiredShapeName:
            try:
                cmds.rename(shape, desiredShapeName)
            except:
                pass
    cmds.select(clear=True)
    return newCurve

def clusterCrvSpawn(crv,off,tar):
    if not crv or not cmds.objExists(crv):
        cmds.warning("Curve not valid")
        return []
    created = []
    offBase = _node_name(off)
    tarBase = _node_name(tar)
    offNode = "{}_cluster".format(offBase) 
    if cmds.objExists(offNode):
        cmds.warning("{} cluster exists -> skip .".format(offNode))
    else:
        _ , offNode = cmds.cluster("{}.cv[0]".format(crv))
        offNode = cmds.rename(offNode, "{}_cluster".format(off))
        cmds.parent(offNode,off)
        cmds.setAttr("{}.v".format(offNode),0)
        created.append(offNode)
    tarNode = "{}_cluster".format(tarBase)
    if cmds.objExists(tarNode):
        cmds.warning("{} cluster exists -> skip .".format(tarNode))
    else:
        _, tarNode = cmds.cluster("{}.cv[1]".format(crv))
        tarNode = cmds.rename(tarNode, "{}_cluster".format(tar))
        cmds.parent(tarNode,tar)
        cmds.setAttr("{}.v".format(tarNode),0)
        created.append(tarNode)
    return created

def buildAimReference(off, tar):
    cmds.undoInfo(openChunk=True)
    try:
        sCurve = crvSpawn(off, tar)
        if not sCurve:
            return None, []
        clusters = clusterCrvSpawn(sCurve, off, tar) or []
        return sCurve, clusters
    finally:
        cmds.undoInfo(closeChunk=True)

def createAimSpace(axis, posNegToggle, intF=None, cbWorldMn1=None):
    # backward compatibility:  old UI call had swapped args (posNegToggle, axis)
    if axis and isinstance(axis, str) and 'checkBox' in axis and posNegToggle in ('X', 'Y', 'Z'):
        axis, posNegToggle = posNegToggle, axis

    AXIS_DATA = {
        'X': {'offset': (1,0,0), 'aim': (1,0,0), 'up': (0,0,1)},
        'Y': {'offset': (0,1,0), 'aim': (0,1,0), 'up': (0,0,1)},
        'Z': {'offset': (0,0,1), 'aim': (0,0,1), 'up': (0,1,0)}
    }

    if axis not in AXIS_DATA:
        cmds.warning("Invalid axis: {}".format(axis))
        return

    isPositive = cmds.checkBox(posNegToggle, q=True, v=True)
    sign = 1 if isPositive else -1
    if intF:
        sliderVal = cmds.intSliderGrp(intF, q=True, v=True)
    else:
        sliderVal = 50
    minTime, maxTime = get_safe_time_range()
    
    sel = cmds.ls(sl=True, type="transform") or []
    if not sel:
        cmds.warning("NO selection")
        return
    
    existingNodes = []
    objNodeMap = {}

    for obj in sel:
        rootName = "{}_temp_aimspace_root".format(obj)
        offName  = "{}_temp_aimspace_offset".format(obj)
        tarName  = "{}_temp_aimspace_target".format(obj)

        objNodeMap[obj] = (rootName, offName, tarName)
        for node in (rootName,offName,tarName):
            if cmds.objExists(node):
                existingNodes.append(node)

    if existingNodes:
        existingNodes = list(set(existingNodes))
        cmds.select(existingNodes,r=True)
        cmds.warning("Temp aimspace nodes already exist. Remove them first:\n{}".format(", ".join(existingNodes)))
        return

    createdTar = []
    if cbWorldMn1:
        world = cmds.checkBox(cbWorldMn1, q=True, v=True)
    else:
        world = False
    
    cmds.undoInfo(openChunk=True)
    try:
        cmds.refresh(suspend=True)
        try:
            temp_constraints = []
            bake_targets = []
            created_data = []

            for obj in sel:
                rootName, offName, tarName = objNodeMap[obj]

                try:
                    root = createDisplayLocator(rootName)
                    off  = createDisplayLocator(offName, parent=root)
                    tar  = createDisplayLocator(tarName, scale=(25,25,25), color=(0,0.6,0.6))
                except Exception as e:
                    cmds.warning("Failed to create display locators for [{}]: {}".format(obj, e))
                    continue

                createdTar.append(tar)

                tmpConst1 = cmds.parentConstraint(obj, root, mo=False)
                tmpConst2 = cmds.parentConstraint(obj, tar, mo=False)
                cmds.delete(tmpConst1)
                cmds.delete(tmpConst2)

                offset = tuple(v * sliderVal * sign for v in AXIS_DATA[axis]['offset'])
                cmds.xform(tar, r=True, os=True, t=offset)
                buildAimReference(off,tar)

                tempConst_tar = cmds.parentConstraint(obj, tar, mo=True)[0]
                tempConst_root = cmds.parentConstraint(obj, root, mo=True)[0]
                temp_constraints.extend([tempConst_tar, tempConst_root])
                bake_targets.extend([tar, root])
                created_data.append((obj, root, off, tar))

            if not created_data:
                cmds.warning("No valid objects were prepared for aimspace creation")
                return

            unique_bake_targets = list(dict.fromkeys(bake_targets))
            _bake_nodes(unique_bake_targets, minTime, maxTime)
            cmds.filterCurve(*unique_bake_targets)
            if temp_constraints:
                cmds.delete(temp_constraints)

            aimVec = tuple(v * sign for v in AXIS_DATA[axis]['aim'])
            upVec  = AXIS_DATA[axis]['up']

            for obj, root, off, tar in created_data:
                cmds.aimConstraint(
                    tar, off,
                    mo=True,
                    aimVector=aimVec,
                    upVector=upVec,
                    worldUpVector=upVec,
                    worldUpType="objectrotation",
                    worldUpObject=root
                )

                if world:
                    cmds.pointConstraint(root,obj,mo=True)
                else:
                    cmds.pointConstraint(obj,root,mo=True)
                cmds.orientConstraint(off,obj,mo=True)
        finally:
            cmds.refresh(suspend=False)
    except Exception as e:
        cmds.warning("createAimSpace failed: {}".format(e))
        raise
    finally:
        cmds.undoInfo(closeChunk=True)
    if createdTar:
        cmds.select(createdTar, r=True)
    mel.eval('print ("RESULT : aimspace created\\n")')
