import maya.cmds as cmds, re

def pin(sel):
    objShape  = cmds.listRelatives(sel[0], p=1)[0]
    objTran   = cmds.listRelatives(objShape, p=1)[0]
    typeCheck = cmds.nodeType(objShape)
    
    if typeCheck == "mesh" or typeCheck == "nurbsSurface" or typeCheck == "nurbsCurve":
        loc = cmds.spaceLocator(n=objTran+"RP_loc")[0]
        
        node_aim = cmds.createNode("aimConstraint", n=objTran+"RP_aimConstraint")
        cmds.setAttr(node_aim+".tg[0].tw",1)
        cmds.setAttr(node_aim+".a", 0,1,0)
        cmds.setAttr(node_aim+".u", 0,0,1)
        
        node_mut = cmds.createNode("multiplyDivide", n=objTran+"RP_mut")
        cmds.setAttr(node_mut+".input2X", .1)
        cmds.setAttr(node_mut+".input2Z", .1)
        
        parAttrs = ["parameterU", "parameterV"]
        inputTyp = ".inputSurface"
        
        if typeCheck == "mesh":
            tenAttr  = ".tv"
            numSel   = len(sel)
            if numSel < 2:
                cmds.error("No two edges selected.")
                
                return
                
            else:
                node_lof = cmds.createNode("loft", n=objTran+"RP_lof")
                cmds.setAttr(node_lof+".u", 1)
                cmds.setAttr(node_lof+".rsn", 1)
                cmds.setAttr(node_lof+".ic", s=len(sel))
                
                count = 0
                for edge in sel:
                    node_cme = cmds.createNode("curveFromMeshEdge", n=objTran+"RP_cme")
                    edgeNum  = re.findall(r"[-+]?\d*\.\d+|\d+", edge)
                    cmds.setAttr(node_cme+".ihi", 1)
                    cmds.setAttr(node_cme+".edgeIndex[0]", int(edgeNum[-1]))
                    
                    cmds.connectAttr(objShape+".worldMesh", node_cme+".inputMesh")
                    cmds.connectAttr(node_cme+".outputCurve", node_lof+".inputCurve["+str(count)+"]")
                    count += 1
                    
                node_pos = cmds.createNode("pointOnSurfaceInfo", n=objTran+"RP_pos")
                cmds.setAttr(node_pos+".turnOnPercentage", 1)
                
                for parAttr, axis in zip(parAttrs, ["X", "Z"]):
                    cmds.addAttr(loc, ln=parAttr, k=1, min=0, max=10.0)
                    cmds.setAttr(loc+"."+parAttr, 5)
                    cmds.connectAttr(loc+"."+parAttr, node_mut+".input1"+axis)
                    cmds.connectAttr(node_mut+".output"+axis, node_pos+"."+parAttr)
                
        if typeCheck == "nurbsSurface":
            sel      = sel[0]
            tenAttr  = ".tv"
            
            uvVal    = re.findall(r"[-+]?\d*\.\d+|\d+", sel)
            node_pos = cmds.createNode("pointOnSurfaceInfo", n=objTran+"RP_pos")
            cmds.setAttr(node_pos+".turnOnPercentage", 1)
            
            minMaxU = cmds.getAttr(objShape+".minMaxRangeU")
            minMaxV = cmds.getAttr(objShape+".minMaxRangeV")
            
            val = [float(uvVal[-2])/minMaxU[0][1], float(uvVal[-1])/minMaxV[0][1]]
            
            for parAttr, val, axis in zip(parAttrs, val, ["X", "Z"]):
                cmds.addAttr(loc, ln=parAttr, k=1, min=0, max=10.0)
                cmds.setAttr(loc+"."+parAttr, val*10)
                cmds.connectAttr(loc+"."+parAttr, node_mut+".input1"+axis)
                cmds.connectAttr(node_mut+".output"+axis, node_pos+"."+parAttr)
            
        elif typeCheck == "nurbsCurve":
            sel      = sel[0]
            tenAttr  = ".t"
            inputTyp = ".inputCurve"
            
            uVal     = re.findall(r"[-+]?\d*\.\d+|\d+", sel)
            node_pos = cmds.createNode("pointOnCurveInfo", n=objTran+"RP_poc")
            cmds.setAttr(node_pos+".turnOnPercentage", 1)
            
            minMax = cmds.getAttr(objShape+".minMaxValue")
            uVal   = float(uVal[-1])/minMax[0][1]
            
            cmds.addAttr(loc, ln=parAttrs[0], k=1, min=.0001, max=9.9999)
            cmds.setAttr(loc+"."+parAttrs[0], uVal*10)
            
            cmds.connectAttr(loc+"."+parAttrs[0], node_mut+".input1X")
            cmds.connectAttr(node_mut+".outputX", node_pos+".parameter")
        
        if typeCheck == "mesh":
            cmds.connectAttr(node_lof+".outputSurface", node_pos+inputTyp)
        else:
            cmds.connectAttr(objShape+".worldSpace", node_pos+inputTyp)
            
        cmds.connectAttr(node_pos+tenAttr, node_aim+".wu")
        cmds.connectAttr(node_pos+".n", node_aim+".tg[0].tt")
        cmds.connectAttr(node_pos+".result.position", loc+".t")
        cmds.connectAttr(node_aim+".cr", loc+".r")
        
        cmds.parent(node_aim, loc)
        cmds.select(loc)
        
        return loc
    
    else:
        cmds.error("Tool does not support %s.") %sel
        
        return


def slide(sel):
    sel       = sel[0]
    objShape  = cmds.listRelatives(sel, p=1)[0]
    objTran   = cmds.listRelatives(objShape, p=1)[0]
    typeCheck = cmds.nodeType(objShape)
    
    if typeCheck == "nurbsSurface" or typeCheck == "nurbsCurve":
        node_aim = cmds.createNode("aimConstraint", n=objTran+"RS_aimConstraint")
        cmds.setAttr(node_aim+".tg[0].tw",1)
        cmds.setAttr(node_aim+".a", 0,1,0)
        cmds.setAttr(node_aim+".u", 0,0,1)
        
        surfaceloc = cmds.spaceLocator(n=objTran+"Surface_loc")[0]
        cmds.setAttr(surfaceloc+".overrideEnabled", 1)
        cmds.setAttr(surfaceloc+".overrideColor", 4)
        
        spaceloc   = cmds.spaceLocator(n=objTran+"Space_loc")[0]
        cmds.setAttr(spaceloc+".overrideEnabled", 1)
        cmds.setAttr(spaceloc+".overrideColor", 15)
        
        if typeCheck == "nurbsSurface":
            node_cps = cmds.createNode("closestPointOnSurface", n=objTran+"RS_cps")
            node_pos = cmds.createNode("pointOnSurfaceInfo", n=objTran+"RS_pos")
            
            nodeTmp_pos = cmds.createNode("pointOnSurfaceInfo", n=objTran+"TmpRS_pos")
            uvVal       = re.findall(r"[-+]?\d*\.\d+|\d+", sel)
            
            parAttrs = ["parameterU", "parameterV"]
            count    = -2
            for parAttr in parAttrs:
                cmds.setAttr(nodeTmp_pos+"."+parAttr, float(uvVal[int(count)]))
                cmds.connectAttr(node_cps+"."+parAttr, node_pos+"."+parAttr)
                count+=1
            
            cmds.connectAttr(objShape+".worldSpace", nodeTmp_pos+".inputSurface")
            cmds.connectAttr(nodeTmp_pos+".position", spaceloc+".translate")
            
            cmds.connectAttr(objShape+".worldSpace", node_cps+".inputSurface")
            cmds.connectAttr(objShape+".worldSpace", node_pos+".inputSurface")
            cmds.connectAttr(spaceloc+".translate", node_cps+".inPosition")
            
            cmds.connectAttr(node_cps+".position", surfaceloc+".translate")
            cmds.connectAttr(node_pos+".result.normal", node_aim+".tg[0].tt")
            cmds.connectAttr(node_pos+".tv", node_aim+".wu")
            
            cmds.getAttr(nodeTmp_pos+".position")
            
            cmds.delete(nodeTmp_pos)
            
        elif typeCheck == "nurbsCurve":
            node_npc = cmds.createNode("nearestPointOnCurve", n=objTran+"RS_npc")
            node_poc = cmds.createNode("pointOnCurveInfo", n=objTran+"RS_poc")
            
            nodeTmp_poc = cmds.createNode("pointOnCurveInfo", n=objTran+"TmpRS_poc")
            uVal        = re.findall(r"[-+]?\d*\.\d+|\d+", sel)
            cmds.setAttr(nodeTmp_poc+".parameter", float(uVal[-1]))
            
            cmds.connectAttr(objShape+".worldSpace", nodeTmp_poc+".inputCurve")
            cmds.connectAttr(nodeTmp_poc+".position", spaceloc+".translate")
            
            spacelocSpace = cmds.getAttr(spaceloc+".t")[0]
            cmds.delete(nodeTmp_poc)
            cmds.setAttr(spaceloc+".t", spacelocSpace[0], spacelocSpace[1], spacelocSpace[2])
            
            cmds.connectAttr(objShape+".worldSpace", node_poc+".inputCurve")
            cmds.connectAttr(objShape+".worldSpace", node_npc+".inputCurve")
            cmds.connectAttr(node_npc+".result.parameter", node_poc+".parameter")
            cmds.connectAttr(node_npc+".result.position", surfaceloc+".translate")
            cmds.connectAttr(spaceloc+".translate", node_npc+".inPosition")
            cmds.connectAttr(node_poc+".result.normal", node_aim+".tg[0].tt")
            cmds.connectAttr(node_poc+".result.tangent", node_aim+".wu")
            
        cmds.connectAttr(node_aim+".cr", surfaceloc+".r")
        cmds.parent(node_aim, surfaceloc)
        cmds.select(spaceloc)
    
        return spaceloc
    
    else:
        cmds.error("Tool does not support %s.") %sel
        
        return



#sel = cmds.ls(sl=1)[0]
#rivet.slide(sel)
#rivet.pin(sel)

