import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaAnim as oma
import maya.OpenMayaMPx as ompx
import maya.mel as mel
import math
import os
def maya_useNewAPI(): pass

def initializePlugin(obj):
    plug = om2.MFnPlugin(obj, vendor="StanDou", version="1.0.0")
    try:
        plug.registerCommand(ShotMask.COMMAND, ShotMask.creater)
        print(f"{ShotMask.COMMAND} 指令注册成功")
    except:
        om2.MGlobal.displayError("{0} 指令注册失败".format(ShotMask.COMMAND))
    try:
        plug.registerNode(ShotMaskLocatorNode.NODE_NAME,
                          ShotMaskLocatorNode.NODE_ID, 
                          ShotMaskLocatorNode.creator,
                          ShotMaskLocatorNode.initialize,
                          om2.MPxNode.kLocatorNode,
                          ShotMaskLocatorNode.DRAW_DB_CLASSIFICATION)
        
        print(f"{ShotMaskLocatorNode.NODE_NAME} 结点注册成功")
    except Exception as e:
        om2.MGlobal.displayError(f"{ShotMaskLocatorNode.NODE_NAME} 结点注册失败, 异常类型: {type(e)}")
    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(ShotMaskLocatorNode.DRAW_DB_CLASSIFICATION,
                                                      ShotMaskLocatorNode.DRAW_REGISTRANT_ID,
                                                      ShotMaskDrawOverride.creator)
        print("ShotMask DrawOverride 注册成功")
    except Exception as e:
        om2.MGlobal.displayError(f"ShotMask DrawOverride 注册失败, 异常类型: {type(e)}")

def uninitializePlugin(obj):
    plug = om2.MFnPlugin(obj)
    
    try:
        plug.deregisterCommand(ShotMask.COMMAND)
        print(f"{ShotMask.COMMAND} 命令注销成功")
    except Exception as e:
        om2.MGlobal.displayError(f"{ShotMask.COMMAND} 命令注销失败, 异常类型: {type(e)}")
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(
            ShotMaskLocatorNode.DRAW_DB_CLASSIFICATION, 
            ShotMaskLocatorNode.DRAW_REGISTRANT_ID)
        print("ShotMaskOverride 注销成功")
    except Exception as e:
        om2.MGlobal.displayError(f"ShotMaskOverride 注销失败, 异常类型: {type(e)}")

    try:
        plug.deregisterNode(ShotMaskLocatorNode.NODE_ID)
        print(f"{ShotMaskLocatorNode.NODE_NAME} 结点注销成功")
    except Exception as e:
        om2.MGlobal.displayError(f"{ShotMaskLocatorNode.NODE_NAME} 结点注销失败, 异常类型: {type(e)}")

def getShotMask():
    node = cmds.ls(type = ShotMaskLocatorNode.NODE_NAME)
    if len(node) > 0:
        return node
    else:
        return None
    
class ShotMask(om2.MPxCommand):
    COMMAND = "shotmask"
                     
    def __init__(self):
        super(ShotMask, self).__init__()

    def doIt(self, args):
        print("shotMask run!")

    @classmethod
    def creater(cls):
        return ShotMask()

class ShotMaskLocatorNode(omui.MPxLocatorNode):
    NODE_NAME = "ShotMask"
    NODE_ID = om2.MTypeId(0x40000)
    DRAW_DB_CLASSIFICATION = "drawdb/geometry/shotmask"
    DRAW_REGISTRANT_ID = "ShotMaskLocator"
    COLOR_YELLOW = om2.MColor([1.0, 1.0, 0.0])
    COLOR_WHITE = om2.MColor([1.0, 1.0, 1.0])
    COLOR_BLACK = om2.MColor([0.0, 0.0, 0.0])
    SHOTMASK_TEXT = [("bottomLeft", "blt"), 
                     ("bottomRight", "brt"),
                     ("bottomMid", "bmid"),
                     ("topLeft", "tlt"),
                     ("topMid", "tmid"),
                     ("topRight", "trt")]
    OPT_VAR_BORDER_SCALE = "shotmask_border_scale"
    OPT_VAR_BORDER_COLOR = "shotmask_border_color"
    OPT_VAR_BORDER_ALPHA = "shotmask_border_alpha"
    OPT_VAR_TEXT_COLOR  = "shotmask_text_color"
    OPT_VAR_TEXT_ALPHA = "shotmask_text_alpha"
    def __init__(self):
        super(ShotMaskLocatorNode, self).__init__()
    
    def compute(self, plug, dataBlock):
        pass
    
    @classmethod
    def creator(cls):
        return ShotMaskLocatorNode()
    
    @classmethod
    def initialize(cls):
        
        typed_attr = om2.MFnTypedAttribute()
        numeric_attr = om2.MFnNumericAttribute()
        # 创建默认值 同为 MObject 类型
        default_attr = om2.MFnStringData()
        default_val = default_attr.create("")
        cam_attr = typed_attr.create("camera", "cam", om2.MFnData.kString, default_val)
        cls.update_attr(typed_attr)
        cls.addAttribute(cam_attr)
        # 添加 ShotMask 文本属性
        for tuple in cls.SHOTMASK_TEXT:
            obj = typed_attr.create(*tuple, om2.MFnData.kString, default_val)
            cls.update_attr(typed_attr)
            cls.addAttribute(obj)
        
        # 添加边界缩放和边界颜色
        obj = numeric_attr.create("borderScale", "bScale", om2.MFnNumericData.kFloat, 1.0)
        numeric_attr.setMin(1.0)
        numeric_attr.setMax(1.5)
        numeric_attr.default = 1.1
        cls.addAttribute(obj)
        

        obj = numeric_attr.createColor("borderColor", "bColor")
        cls.update_attr(numeric_attr)
        cls.addAttribute(obj)

        obj = numeric_attr.create("borderAlpha", "bAlpha", om2.MFnNumericData.kFloat, 1.0)
        cls.update_attr(numeric_attr)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        cls.addAttribute(obj)
        # 添加文本和文本颜色
        obj = numeric_attr.createColor("textColor", "tColor")
        cls.update_attr(numeric_attr)
        numeric_attr.default = (1.0, 1.0, 0.0) # yellow
        cls.addAttribute(obj)

        obj = numeric_attr.create("textAlpha", "tAlpha", om2.MFnNumericData.kFloat, 1.0)
        cls.update_attr(numeric_attr)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        cls.addAttribute(obj)
        # 添加 帧数 和 日期时间
        cFrame = default_attr.create(str(cmds.currentTime(q=True)))
        obj = default_attr.create("currentFrame", "cFrame", om2.MFnData.kString, cFrame)
        cls.addAttribute(obj)

        date = "{0} {1}".format(cmds.about(currentDate = True), cmds.about(currentTime = True))
        obj = numeric_attr.create("currentTime", "cTime", om2.MFnNumericData.kInt, date)
        cls.addAttribute(obj)
    # 返回 True 会被视为正常 Locator 处理
    @classmethod
    def update_attr(cls, attr):
        if not attr:
            return
        attr.writable = True
        attr.readable = True
        if attr.type() == om2.MFn.kNumericAttribute:
           attr.keyable = True
    def postConstructor(self):
        mfn_node = om2.MFnDependencyNode(self.thisMObject())
        mfn_node.findPlug("castsShadows", False).setBool(False)
        mfn_node.findPlug("receiveShadows", False).setBool(False)
        mfn_node.findPlug("motionBlur", False).setBool(False)

    def excludeAsLocator(self):
        return False
    
class ShotMaskMUserData(om2.MUserData):
    def __init__(self):
        super(ShotMaskMUserData, self).__init__()
        self.SHOTMASK_TEXT = {
                              "bottomLeft" : "",
                              "bottomRight" : "",
                              "bottomMid": "",
                              "topLeft" : "",
                              "topMid" : "",
                              "topRight" : ""
                              }
        self.borderColor = om2.MColor([0.0, 0.0, 0.0]) # Black
        self.borderAlpha = 1.0

        self.textColor = om2.MColor([1.0, 1.0, 1.0, 1.0]) # White
        self.textAlpha = 1.0

        self.maskWidth = 0
        self.maskHeight = 0

        self.vp_width = 0
        self.vp_height = 0
        
        self.bottomBorder = True
        self.topBorder = True

        self.currentTime = str(cmds.currentTime(q=True))
        self.currentCamera = "None"

        self.borderScale = 1.0

    def __str__(self):
        print_str = ""
        print_str += "Mask Width: {0}\n".format(str(self.maskWidth)) 
        print_str += "Mask Height: {0}\n".format(str(self.maskHeight)) 
        print_str += "ViewPort Widght: {0}\n".format(str(self.vp_width))
        print_str += "ViewPort Height: {0}\n".format(str(self.vp_height))
        print_str += "是否显示上边界: {0}\n".format(self.topBorder)
        print_str += "是否显示下边界: {0}\n".format(self.bottomBorder)
        print_str += "当前帧为: {0}\n".format(self.currentTime)
        print_str += "当前相机为: {0}\n".format(self.currentCamera)
        return print_str
class ShotMaskDrawOverride(omr.MPxDrawOverride):

    NAME = "shotmask_draw_override"
    def __init__(self, obj):
        super(ShotMaskDrawOverride, self).__init__(obj, None)

    def supportedDrawAPIs(self):
        return (omr.MRenderer.kAllDevices)
    
    def prepareForDraw(self, objPath, cameraPath, frameContext, oldData):
        data = oldData
        if not isinstance(data, ShotMaskMUserData):
            data = ShotMaskMUserData()
        dag_node = om2.MFnDagNode(objPath)
        # 检查 Camera 是否存在且是否为目标 Camera
        cam_plug = dag_node.findPlug("camera", False)
        if cameraPath and self.camera_exist(cam_plug) and not self.nameMatch(cam_plug.asString(), cameraPath):
            return None
        # 获取更新数据
        origin_x, origin_y, data.vp_width, data.vp_height = frameContext.getViewportDimensions()
        data.maskWidth, data.maskHeight = self.getResolutionWidthAndHeight(cameraPath, data.vp_width, data.vp_height)
        data.currentTime = int(cmds.currentTime(q=True))
        data.currentCamera = self.getTransformName(cameraPath)
        ## 更新 ShotMask 文本、以及边界缩放
        for key in data.SHOTMASK_TEXT.keys():
            data_plug = dag_node.findPlug(key, False)
            if key == "bottomMid":
                data.SHOTMASK_TEXT[key] = data.currentCamera
            elif key == "bottomRight": 
                data.SHOTMASK_TEXT[key] = str(data.currentTime)
            elif key == "bottomLeft":
                data.SHOTMASK_TEXT[key] = mel.eval("getenv USERNAME")
            elif key == "topRight":
                text = "{0} {1}".format(cmds.about(currentDate = True), cmds.about(currentTime = True))
                data.SHOTMASK_TEXT[key] = text
            elif key == "topMid":     
                path = cmds.file(q=True, sceneName=True)
                if not path: # 获取当前文件名
                    data.SHOTMASK_TEXT[key] = "untitled"
                else: # 未命名文件
                    data.SHOTMASK_TEXT[key] = os.path.basename(path)
            else:
                data.SHOTMASK_TEXT[key] = data_plug.asString()
            
        data.borderScale = dag_node.findPlug("bScale", False).asFloat()
        ## 更新文本颜色、边界颜色
        data.borderAlpha = dag_node.findPlug("bAlpha", False).asFloat()
        borderR = dag_node.findPlug("bColorr", False).asFloat()
        borderG = dag_node.findPlug("bColorg", False).asFloat()
        borderB = dag_node.findPlug("bColorb", False).asFloat()
        data.borderColor = om2.MColor([borderR, borderB, borderG, data.borderAlpha])
        
        data.textAlpha = dag_node.findPlug("tAlpha", False).asFloat()
        textR = dag_node.findPlug("tColorr", False).asFloat()
        textG = dag_node.findPlug("tColorg", False).asFloat()
        textB = dag_node.findPlug("tColorb", False).asFloat()
        data.textColor = om2.MColor([textR, textG, textB, data.textAlpha])

        print(data)
        return data
    
    def getResolutionWidthAndHeight(self, cameraPath, vp_width, vp_height):
        camera = om2.MFnCamera(cameraPath)
        overscan = camera.overscan
        device_aspect_ratio = cmds.getAttr("defaultResolution.deviceAspectRatio")
        pixel_aspect_ratio = cmds.getAttr("defaultResolution.pixelAspect")
        device_aspect_ratio = device_aspect_ratio / pixel_aspect_ratio
        camera_aspect_ratio = camera.aspectRatio()
        
        vp_aspect_ratio = vp_width / vp_height

        if camera.filmFit == om2.MFnCamera.kHorizontalFilmFit:
            mask_width = vp_width / overscan
            mask_height = mask_width / device_aspect_ratio
        elif camera.filmFit == om2.MFnCamera.kVerticalFilmFit:
            mask_height =  vp_height / overscan
            mask_width = mask_height * device_aspect_ratio
        else:
            om2.MGlobal.displayError("not supported film fit type")
            return None, None

        return mask_width, mask_height
    
    def hasUIDrawables(self):
        return True
    
    def addUIDrawables(self, objPath, drawManager, frameContext, data):
        if not (data and isinstance(data, ShotMaskMUserData)):
            return
        border_index_x = (data.vp_width - data.maskWidth) / 2.0
        border_index_y = (data.vp_height - data.maskHeight) / 2.0
        borderHeight = data.maskHeight * 0.05 * data.borderScale
        backgroundSize = (math.ceil(data.maskWidth), math.ceil(borderHeight))

        drawManager.beginDrawable()
        # 绘制 ShotMask 上下边界
        if data.bottomBorder:
            border_index_x = (data.vp_width - data.maskWidth) / 2.0
            border_index_y = (data.vp_height - data.maskHeight) / 2.0
            self.drawBorder(drawManager, 
                            om2.MPoint(border_index_x, border_index_y), 
                            backgroundSize,
                            data.borderColor)
            print("border 左下角: ({0}, {1})".format(border_index_x, border_index_y))
        if data.topBorder:
            border_index_x = (data.vp_width - data.maskWidth) / 2.0
            border_index_y = (data.vp_height + data.maskHeight) / 2.0 - borderHeight 
            self.drawBorder(drawManager, 
                            om2.MPoint(border_index_x, border_index_y), 
                            backgroundSize,
                            data.borderColor)
            print("border 左上角: ({0}, {1})".format(border_index_x, border_index_y))
        
        font_size = int(0.68 * borderHeight)
        drawManager.setFontName("Consolas")
        drawManager.setFontSize(font_size)
        drawManager.setColor(data.textColor)

        for key in data.SHOTMASK_TEXT.keys():
            self.drawText(drawManager, data, key, borderHeight, backgroundSize)

        drawManager.endDrawable()
    
    def drawText(self, drawManager, data, key, borderHeight, backgroundSize):
        left_index_x = (data.vp_width - data.maskWidth) / 2.0
        right_index_x = (data.vp_width + data.maskWidth) / 2.0
        top_index_y = (data.vp_height + data.maskHeight) / 2.0 - borderHeight
        bottom_index_y = (data.vp_height - data.maskHeight) / 2.0
        # print("text 左下角: ({0}, {1})".format(left_index_x, bottom_index_y))
        # print("text 左上角: ({0}, {1})".format(left_index_x, top_index_y))
        text = data.SHOTMASK_TEXT[key]

        if key == "bottomLeft":
            position = om2.MPoint(left_index_x, bottom_index_y)
            alignment = omr.MUIDrawManager.kLeft
        elif key == "bottomMid":
            position = om2.MPoint(data.vp_width / 2, bottom_index_y)
            alignment = omr.MUIDrawManager.kCenter
        elif key == "bottomRight":
            position = om2.MPoint(right_index_x, bottom_index_y)
            alignment = omr.MUIDrawManager.kRight
        elif key == "topLeft":
            position = om2.MPoint(left_index_x, top_index_y)
            alignment = omr.MUIDrawManager.kLeft
        elif key == "topMid":
            position = om2.MPoint(data.vp_width / 2, top_index_y)
            alignment = omr.MUIDrawManager.kCenter
        elif key == "topRight":
            position = om2.MPoint(right_index_x, top_index_y)
            alignment = omr.MUIDrawManager.kRight
        else:
            return
        if key == "bottomRight" or key == "topRight":
            # 帧数会经常变化，设置成 dynamic 节省性能
            drawManager.text2d(position, text, alignment=alignment, dynamic = False, backgroundSize =backgroundSize)
        else:
            drawManager.text2d(position, text, alignment=alignment, dynamic = False, backgroundSize = backgroundSize)

    def drawBorder(self, drawManager, position, backgroundSize, color):
        drawManager.text2d(position, " ", 
                           alignment = omr.MUIDrawManager.kLeft,
                           backgroundSize = backgroundSize,
                           backgroundColor = color
                           )
        
    def camera_exist(self, cam_plug):
        dag_itr = om2.MItDependencyNodes(om2.MFn.kCamera)
        cam_name = cam_plug.asString()
        while not dag_itr.isDone():
            dag_path = om2.MDagPath.getAPathTo(dag_itr.thisNode())
            if self.nameMatch(cam_name, dag_path):
                return True
            dag_itr.next()
        return False
    
    def nameMatch(self, name, dag_path):
        return name == self.getShapeName(dag_path) or name == self.getTransformName(dag_path)

    def getShapeName(self, dagPath):
        shape_node = dagPath.node()
        if shape_node:
            dag_shape = om2.MFnDagNode(shape_node)
            return dag_shape.name()
        return ""
    
    def getTransformName(self, dagPath):
        transform_node = dagPath.transform()
        if transform_node:
            dag_trans = om2.MFnDagNode(transform_node)
            return dag_trans.name()
        return ""
    @staticmethod
    def creator(obj):
        return ShotMaskDrawOverride(obj)
    
    
def main_dev():

    cmds.file(f=True, new=True)
    
    plugin_name = "ShotMask.py"
   
    cmds.evalDeferred("if cmds.pluginInfo(\"{0}\", loaded=True, query=True): cmds.unloadPlugin(\"{0}\")".format(plugin_name))
    cmds.evalDeferred("if not cmds.pluginInfo(\"{0}\", loaded=True, query=True): cmds.loadPlugin(\"{0}\")".format(plugin_name))
    cmds.evalDeferred('cmds.createNode("ShotMask")')

if __name__ == "__main__":
    # Development Only, Used for fast Update of code like auto reloading when execute
    main_dev()
    pass