try:
    import PySide6.QtCore as QtCore
    import PySide6.QtWidgets as QtWidgets
    import PySide6.QtGui as QtGui
    
except ImportError:
    import PySide2.QtCore as QtCore
    import PySide2.QtWidgets as QtWidgets
    import PySide2.QtGui as QtGui

from shiboken2 import wrapInstance
import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import sys,os
from maya.OpenMayaUI import MQtUtil
import maya.OpenMayaMPx as ompx
def maya_useNewAPI():
    pass
class PlayBlastCommand(om.MPxCommand):
    COMMAND = "myplayblast"
    def __init__(self):
        super(PlayBlastCommand, self).__init__()
    
    def doIt(self, args):
        # 如果不把 window 挂到 maya main window 下，那么窗口会闪退
        # 因为 doIt 执行完马上就退出了, 所以 window 会直接被关闭
        window = MyPlayBlast()
        window.show()
        
    @staticmethod
    def creator():
        return PlayBlastCommand()
def initializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.registerCommand(PlayBlastCommand.COMMAND, PlayBlastCommand.creator)
        print("注册 {0} 成功！".format(PlayBlastCommand.COMMAND))
    except Exception as e:
        om.MGlobal.displayError("注册 {0} 失败".format(PlayBlastCommand.COMMAND))

def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterCommand(PlayBlastCommand.COMMAND)
        print("注销 {0} 成功！".format(PlayBlastCommand.COMMAND))
    except Exception as e:
        om.MGlobal.displayError("注销 {0} 失败".format(PlayBlastCommand.COMMAND))

def maya_main_window():
    ptr = MQtUtil.mainWindow()
    if sys.version_info.major < 3:
        return wrapInstance(long(ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(int(ptr), QtWidgets.QWidget)

class PlayBlastHeader(QtWidgets.QWidget):
   
    def __init__(self, text, parent=None):
        super(PlayBlastHeader, self).__init__(parent)

        self.setAutoFillBackground(True)
        self.setBackGroundColor(None)

        self.text_label = QtWidgets.QLabel()
        self.text_label.setTextFormat(QtCore.Qt.TextFormat.MarkdownText)
        self.text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setText(text)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.addWidget(self.text_label)

    def setText(self, text):
       self.text_label.setText("<b>{0}</b>".format(text))
    
    def setBackGroundColor(self, color):
        if not color:
            color = QtWidgets.QPushButton().palette().color(QtGui.QPalette.Button)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, color)
        self.setPalette(palette)

class SavePart(QtWidgets.QWidget):
    
    SCENE_SAVED = "SceneSaved"
    dir_label_name = "目标文件夹"
    file_label_name = "文件名"
    DIR_PATH = ""
    FILE_NAME = ""
    PATH = ""
    ForceText = "强制覆盖"
    isForceChecked = False
    OPT_VAR_IS_OVERWRITE = "shot_mask_is_overwrite"
    def __init__(self, parent=None):
        super(SavePart, self).__init__(parent)
        self.initialize()
        self.createWidgets()
        self.retrieve_and_set_data()
        self.setLayout()
        self.createConnection()
    
    def retrieve_and_set_data(self):
        if cmds.optionVar(ex=self.OPT_VAR_IS_OVERWRITE):
            is_overwrite = cmds.optionVar(q=self.OPT_VAR_IS_OVERWRITE)
            if is_overwrite:
                self.force_overwrite_box.setChecked(True)
            else:
                self.force_overwrite_box.setChecked(False)
    def storeData(self):
        cmds.optionVar(iv=[self.OPT_VAR_IS_OVERWRITE, 1 if self.force_overwrite_box.isChecked() else 0])

    def setLayout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        dir_layout = QtWidgets.QHBoxLayout()
        
        dir_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        dir_layout.addWidget(self.directory_label)
        dir_layout.addWidget(self.directory_le)
        dir_layout.addWidget(self.file_browse_button)
        dir_layout.addWidget(self.open_curdir_button)
        

        file_layout = QtWidgets.QHBoxLayout()
        file_layout.addWidget(self.filename_label)
        file_layout.addWidget(self.filename_le)
        file_layout.addWidget(self.force_overwrite_box)
        file_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        main_layout.addLayout(dir_layout)
        main_layout.addLayout(file_layout)
        main_layout.addStretch()
    def createWidgets(self):
        
        self.directory_label = QtWidgets.QLabel()
        self.directory_label.setText("<b>{0}</b>".format(self.dir_label_name))
        self.directory_le = QtWidgets.QLineEdit()

        self.filename_label = QtWidgets.QLabel()
        self.filename_label.setText("<b>{0}</b>".format(self.file_label_name))
        self.filename_le = QtWidgets.QLineEdit()
        
        self.force_overwrite_box = QtWidgets.QCheckBox(self.ForceText)

        self.file_browse_button = QtWidgets.QPushButton()
        self.file_browse_button.setText("...")
        self.file_browse_button.setToolTip("浏览目录")
        self.file_browse_button.setFixedSize(24, 21)
        
        self.open_curdir_button = QtWidgets.QPushButton()
        self.open_curdir_button.setIcon(QtGui.QIcon(":/fileOpen.png"))
        self.open_curdir_button.setToolTip("打开当前文件夹")
        self.open_curdir_button.setFixedSize(24, 21)
       
        
        self.updateCurrentDirectory()
    def createConnection(self):
        self.filename_le.textChanged.connect(self.refreshText)
        self.directory_le.textChanged.connect(self.refreshText)
        self.force_overwrite_box.stateChanged.connect(self.refreshChecked)

        self.file_browse_button.clicked.connect(self.openFileBrower)
        self.open_curdir_button.clicked.connect(self.openFolder)
    
    def initialize(self):
        id1 = cmds.scriptJob(event=[self.SCENE_SAVED, self.updateCurrentDirectory], pro=True)
        MyPlayBlast.SCRIPT_JOB_IDs.append(id1)
    def openFileBrower(self):
        caption = "选择文件夹"
        #默认是Project路径
        dir = cmds.workspace(q=True, rd=True)
        if os.path.exists(self.DIR_PATH):
            #如果当前路径存在则选择当前路径
            dir = self.DIR_PATH 
        path = QtWidgets.QFileDialog.getExistingDirectory(self, caption=caption, dir=dir)
        if path:
            self.DIR_PATH = path
            self.directory_le.setText(self.DIR_PATH)
        else:
            return
    def openFolder(self):
        if os.path.exists(self.DIR_PATH):
            url = QtCore.QUrl.fromLocalFile(self.DIR_PATH)
        else:
            om.MGlobal.displayWarning("目标文件夹{0}不存在, 打开项目默认拍屏文件夹".format(self.DIR_PATH))
            url = cmds.workspace(q=True, rd=True)
            url = os.path.join(url, "movies")
            url = QtCore.QUrl.fromLocalFile(url)
            
        QtGui.QDesktopServices.openUrl(url)

    def refreshChecked(self):
        self.isForceChecked = self.force_overwrite_box.isChecked()
        
    def refreshText(self):
        self.DIR_PATH = self.directory_le.text()
        self.FILE_NAME = self.filename_le.text()

        self.PATH = os.path.join(self.DIR_PATH, self.FILE_NAME)
        self.PATH = self.PATH.replace(os.path.sep, "/")

        self.directory_le.setToolTip(self.DIR_PATH)
        self.filename_le.setToolTip(self.PATH)

    def updateCurrentDirectory(self):
        
        path = cmds.file(q=True, sceneName=True)
        self.FILE_NAME = os.path.basename(path)
        self.FILE_NAME = self.FILE_NAME.removesuffix(".ma").removesuffix(".mb")
        self.DIR_PATH = os.path.dirname(path)
        
        self.PATH = os.path.join(self.DIR_PATH, self.FILE_NAME)
        self.PATH = self.PATH.replace(os.path.sep, "/")
        
        self.directory_le.setText(self.DIR_PATH)
        self.directory_le.setToolTip(self.DIR_PATH)
        
        self.filename_le.setText(self.FILE_NAME)
        self.filename_le.setToolTip(self.PATH)
        print(self.PATH)
    def get_save_path(self):
        if self.isPathValid():
            return self.PATH
        else:
            raise Exception("Error: 目标路径不存在或未填写文件名")
    def isOverwrite(self):
        return self.force_overwrite_box.isChecked()
    
    def isPathValid(self):
        if not self.filename_le.text():
            return False
        if not self.directory_le.text():
            return False
        return os.path.exists(self.DIR_PATH)
class OptionPart(QtWidgets.QWidget):
    # RESOLUTION_LOOKUP = {
    #     "<当前分辨率>": ["",""],
    #     "HD 1080": (1920, 1080),
    #     "HD 720": (1280, 720),
    #     "HD 540": (960, 540),
    #     "<自定义>": ["",""]
    # }
    RESOLUTION_LOOKUP = {
        "<当前分辨率>": ["",""],
    }
    TIME_RANGE_SELECTION = ["时间轴", "自定义"]
    CUSTOM_TIME_RANGE = [1001,1100]
    OPEN_IN_VIEWER = True
    SHOW_ORNAMENT = False
    RES_LINE_EDIT_SIZE = (90, 32)
    OPT_VAR_RESOLUTION = "shot_mask_resolution"
    OPT_VAR_CUSTOM_RESOLUTION = "shot_mask_custom_resolution"
    OPT_VAR_CUSTOM_TIMERANGE = "shot_mask_custom_time_range"
    OPT_VAR_TIMERANGE_SELECT = "shot_mask_time_range_select"
    OPT_VAR_OPEN_IN_VIEWR = "shot_mask_open_in_viewer"
    OPT_VAR_PLAY_OFF_SCREEN = "shot_mask_play_off_screen"
    TIME_SLIDER_CHANGE_EVENT = "playbackRangeChanged"
    class CameraComboBox(QtWidgets.QComboBox):
        clicked = QtCore.Signal(str)
        def __init__(self, parent=None):
            super(OptionPart.CameraComboBox, self).__init__(parent)
        
        def mousePressEvent(self, event):
            self.clicked.emit("")
            super(OptionPart.CameraComboBox, self).mousePressEvent(event)

    def __init__(self, parent=None):
        super(OptionPart, self).__init__(parent)
        
        self.createWidgets()
        self.retrieve_options_and_set()
        self.setLayout()
        self.createConnections()
        self.initialize()

    
    def initialize(self):
        id1 = cmds.scriptJob(event=[self.TIME_SLIDER_CHANGE_EVENT, self.onPlayBackRangeChange])
        MyPlayBlast.SCRIPT_JOB_IDs.append(id1)
    def onPlayBackRangeChange(self):
        start_time = cmds.playbackOptions(query=True, minTime=True)
        end_time = cmds.playbackOptions(query=True, maxTime=True)
        if self.time_range_selection.currentText() == "时间轴":
            self.time_range_start.setText(str(int(start_time)))
            self.time_range_end.setText(str(int(end_time)))
        
    def storeData(self):
        # update time range selection
        cmds.optionVar(sv=[self.OPT_VAR_TIMERANGE_SELECT, self.time_range_selection.currentText()])
        # update custom time range
        start = int(self.time_range_start.text())
        end = int(self.time_range_end.text())
        cmds.optionVar(iv2=[self.OPT_VAR_CUSTOM_TIMERANGE, start, end])

        # update open in viewer option
        isChecked = self.openInViewCheckBox.isChecked()
        cmds.optionVar(iv=[self.OPT_VAR_OPEN_IN_VIEWR, 1 if isChecked else 0])
       
        # update playblast offscreen
        isOffScreen =  self.playBlastOffScreen.isChecked()
        cmds.optionVar(iv=[self.OPT_VAR_PLAY_OFF_SCREEN, 1 if isOffScreen else 0])
        
    def retrieve_options_and_set(self):
        # called after widgets created
        if cmds.optionVar(exists="shotmask_camera"):
            camera = cmds.optionVar(q="shotmask_camera")
            idx = self.camera_selection.findText(camera)
            
            if idx != -1:
                self.camera_selection.setCurrentIndex(idx)
        # 获取Hud勾选
        if cmds.optionVar(exists="shotmask_show_ornament"):
            state = cmds.optionVar(q="shotmask_show_ornament")
            self.ornament_checkbox.setCheckState(QtCore.Qt.CheckState(state))
            if state:
                self.SHOW_ORNAMENT = True
            else:
                self.SHOW_ORNAMENT = False
        # 获取自定义分辨率
        if cmds.optionVar(exists=self.OPT_VAR_RESOLUTION):
            resolution_tag = cmds.optionVar(q=self.OPT_VAR_RESOLUTION)
            idx = self.resolution_selection.findText(resolution_tag)
            self.resolution_selection.setCurrentIndex(idx)
            if resolution_tag == "<自定义>":
                if cmds.optionVar(ex=self.OPT_VAR_CUSTOM_RESOLUTION):
                    widthHeight = cmds.optionVar(q=self.OPT_VAR_CUSTOM_RESOLUTION)
                else:
                    widthHeight = ["", ""]
                self.RESOLUTION_LOOKUP[resolution_tag] = widthHeight
                self.resolution_width_le.setDisabled(False)
                self.resolution_height_le.setDisabled(False)
                
            elif resolution_tag == "<当前分辨率>":
                widthHeight = self.getCurrentResolution()
            else:
                widthHeight = self.RESOLUTION_LOOKUP[resolution_tag]

            if resolution_tag != "<自定义>":
                if cmds.optionVar(ex=self.OPT_VAR_CUSTOM_RESOLUTION):
                    self.RESOLUTION_LOOKUP["<自定义>"] = cmds.optionVar(q=self.OPT_VAR_CUSTOM_RESOLUTION)
                else:
                    self.RESOLUTION_LOOKUP["<自定义>"] = ["", ""]

            self.resolution_width_le.setText(str(widthHeight[0]))
            self.resolution_height_le.setText(str(widthHeight[1])) 

        else: 
            # 不存在数据, 采取当前分辨率
            widthHeight = self.getCurrentResolution()
            self.RESOLUTION_LOOKUP["<当前分辨率>"] = widthHeight
            self.resolution_width_le.setText(str(widthHeight[0]))
            self.resolution_height_le.setText(str(widthHeight[1])) 
        if cmds.optionVar(ex=self.OPT_VAR_CUSTOM_TIMERANGE):
            # [int, int]
            self.CUSTOM_TIME_RANGE = cmds.optionVar(q=self.OPT_VAR_CUSTOM_TIMERANGE)
        else:
            self.CUSTOM_TIME_RANGE = self.getTimeSliderRange()
        # 获取自定义拍屏范围
        if cmds.optionVar(ex=self.OPT_VAR_TIMERANGE_SELECT):
            tag = cmds.optionVar(q=self.OPT_VAR_TIMERANGE_SELECT)
            idx = self.time_range_selection.findText(tag)
            self.time_range_selection.setCurrentIndex(idx)
            if tag == "自定义":
                self.time_range_start.setText(str(self.CUSTOM_TIME_RANGE[0]))
                self.time_range_end.setText(str(self.CUSTOM_TIME_RANGE[1]))
                self.time_range_start.setDisabled(False)
                self.time_range_end.setDisabled(False)
            else:
                self.setToTimeSlider()
        else:
            self.setToTimeSlider()
        
        if cmds.optionVar(ex=self.OPT_VAR_OPEN_IN_VIEWR):
            if cmds.optionVar(q=self.OPT_VAR_OPEN_IN_VIEWR):
                self.openInViewCheckBox.setChecked(True)
            else:
                self.openInViewCheckBox.setChecked(False)

        if cmds.optionVar(ex=self.OPT_VAR_PLAY_OFF_SCREEN):
            if cmds.optionVar(q=self.OPT_VAR_PLAY_OFF_SCREEN):
                self.playBlastOffScreen.setChecked(True)
            else:
                self.playBlastOffScreen.setChecked(False)
        
    def setToTimeSlider(self):
        timeRange = self.getTimeSliderRange()
        self.time_range_start.setText(str(timeRange[0]))
        self.time_range_end.setText(str(timeRange[1]))

    def getTimeSliderRange(self):
        return [int(cmds.playbackOptions(q=True, min=True)), int(cmds.playbackOptions(q=True, max=True))]
        
    def getCurrentResolution(self):
            width = cmds.getAttr("defaultResolution.width") 
            height = cmds.getAttr("defaultResolution.height")
            return [width, height]
    def get_cameras(self):
        scene_cam_list = cmds.listCameras()
        scene_cam_list.insert(0, "<当前相机>")
        return scene_cam_list
    
    def createWidgets(self):
        self.camera_selection = OptionPart.CameraComboBox()
        self.camera_selection.addItems(self.get_cameras())
        self.ornament_checkbox = QtWidgets.QCheckBox("HUDs")

        self.resolution_selection = QtWidgets.QComboBox()
        self.resolution_selection.addItems(list(self.RESOLUTION_LOOKUP.keys()))
        
        self.resolution_width_le = QtWidgets.QLineEdit()
        self.resolution_height_le = QtWidgets.QLineEdit()
        self.resolution_height_le.setFixedSize(*self.RES_LINE_EDIT_SIZE)
        self.resolution_width_le.setFixedSize(*self.RES_LINE_EDIT_SIZE)
        validator = QtGui.QIntValidator(1, 9999)
        self.resolution_height_le.setValidator(validator)
        self.resolution_width_le.setValidator(validator)
        self.resolution_height_le.setDisabled(True)
        self.resolution_width_le.setDisabled(True)

        self.time_range_selection = QtWidgets.QComboBox()
        self.time_range_selection.addItems(self.TIME_RANGE_SELECTION)
        self.time_range_start = QtWidgets.QLineEdit()
        self.time_range_end = QtWidgets.QLineEdit()
        self.time_range_start.setFixedSize(*self.RES_LINE_EDIT_SIZE)
        self.time_range_end.setFixedSize(*self.RES_LINE_EDIT_SIZE)
        validator_ =  QtGui.QIntValidator()
        self.time_range_start.setValidator(validator_)
        self.time_range_end.setValidator(validator_)
        self.time_range_start.setDisabled(True)
        self.time_range_end.setDisabled(True)

        self.format_selection = QtWidgets.QComboBox()
        self.format_selection.addItem(cmds.optionVar(q="playblastFormat"))
        self.compression_selection =  QtWidgets.QComboBox()
        self.compression_selection.addItem(cmds.optionVar(q="playblastCompression"))

        self.openInViewCheckBox = QtWidgets.QCheckBox("在播放器中打开")
        self.openInViewCheckBox.setChecked(True)
        self.playBlastOffScreen = QtWidgets.QCheckBox("屏下拍屏")
        self.playBlastOffScreen.setChecked(False)
        self.createShotMaskCheckBox = QtWidgets.QCheckBox("遮罩预览")
        self.createShotMaskCheckBox.setChecked(False)
    def setLayout(self):
        main_layout = QtWidgets.QFormLayout(self)

        camera_layout = QtWidgets.QHBoxLayout()
        camera_layout.addWidget(self.camera_selection)
        camera_layout.addWidget(self.ornament_checkbox)

        resolution_layout = QtWidgets.QHBoxLayout()
        resolution_layout.addWidget(self.resolution_selection)
        resolution_layout.addWidget(self.resolution_width_le)
        resolution_layout.addWidget(QtWidgets.QLabel("<b>x</b>"))
        resolution_layout.addWidget(self.resolution_height_le)
        resolution_layout.addStretch()

        time_range_layout =  QtWidgets.QHBoxLayout()
        time_range_layout.addWidget(self.time_range_selection)
        time_range_layout.addWidget(self.time_range_start)
        time_range_layout.addWidget(QtWidgets.QLabel("<b>to</b>"))
        time_range_layout.addWidget(self.time_range_end)
        time_range_layout.addStretch()

        play_option_layout = QtWidgets.QHBoxLayout()
        play_option_layout.addWidget(self.openInViewCheckBox)
        play_option_layout.addWidget(self.playBlastOffScreen)
        play_option_layout.addWidget(self.createShotMaskCheckBox)
        play_option_layout.addStretch()

        main_layout.addRow("<b>相机</b>", camera_layout)
        main_layout.addRow("<b>分辨率</b>", resolution_layout)
        main_layout.addRow("<b>拍屏范围</b>", time_range_layout)
        main_layout.addRow("<b>Format</b>", self.format_selection)
        main_layout.addRow("<b>Encoding</b>", self.compression_selection)
        main_layout.addRow("", play_option_layout)
        
    def createConnections(self):
        # Camera Row
        self.camera_selection.currentIndexChanged.connect(self.onCameraChange)
        self.camera_selection.clicked.connect(self.onCameraClicked)
        self.ornament_checkbox.stateChanged.connect(self.onOrnamentChange)
        # Resolution Row
        self.resolution_selection.currentIndexChanged.connect(self.onResolutionChange)
        self.resolution_width_le.textChanged.connect(self.onWidthChange)
        self.resolution_height_le.textChanged.connect(self.onHeightChange)
        # Time Range Row
        self.time_range_start.textChanged.connect(self.onStartTimeChange)
        self.time_range_end.textChanged.connect(self.onEndTimeChange)

        self.time_range_selection.currentIndexChanged.connect(self.onTimeRangeSelectChange)
        self.createShotMaskCheckBox.stateChanged.connect(self.onCreateShotMask)
    
    def onCreateShotMask(self, state):
        if state:
            MyPlayBlast.createMask()
        else:
            MyPlayBlast.deleteMask()
    def onStartTimeChange(self, text):
        if text:
            self.CUSTOM_TIME_RANGE[0] = int(text)
        else:
            om.MGlobal.displayWarning("开始时间不能为空")

    def onEndTimeChange(self, text):
        if text:
            self.CUSTOM_TIME_RANGE[1] = int(text)
        else:
            om.MGlobal.displayWarning("结束时间不能为空")

    def onTimeRangeSelectChange(self, idx):
        tag = self.time_range_selection.currentText()
        if tag == "自定义":
            self.time_range_start.setDisabled(False)
            self.time_range_end.setDisabled(False)
            self.time_range_start.setText(str(self.CUSTOM_TIME_RANGE[0]))
            self.time_range_end.setText(str(self.CUSTOM_TIME_RANGE[1]))
        else:
            self.time_range_start.setDisabled(True)
            self.time_range_end.setDisabled(True)
            self.setToTimeSlider()

    def onWidthChange(self, text):
        if not self.resolution_width_le.isEnabled():
            return
        width = text
        height = self.resolution_height_le.text()
        widthHeight = [width, height]
        self.updateCustom(widthHeight)
        
    def onHeightChange(self, text):
        if not self.resolution_height_le.isEnabled():
            return
        width = self.resolution_width_le.text()
        height = text
        widthHeight = [width, height]
        self.updateCustom(widthHeight)

    def updateCustom(self, widthHeight):

        self.RESOLUTION_LOOKUP["<自定义>"] = widthHeight
        cmds.optionVar(sa=self.OPT_VAR_CUSTOM_RESOLUTION)
        cmds.optionVar(clearArray=self.OPT_VAR_CUSTOM_RESOLUTION)
        cmds.optionVar(sva=[self.OPT_VAR_CUSTOM_RESOLUTION, widthHeight[0]])
        cmds.optionVar(sva=[self.OPT_VAR_CUSTOM_RESOLUTION, widthHeight[1]])

    def onResolutionChange(self, idx):
        tag = self.resolution_selection.currentText()
        
        if tag == "<自定义>":
            self.resolution_width_le.setDisabled(False)
            self.resolution_height_le.setDisabled(False)
        else:
            self.resolution_width_le.setDisabled(True)
            self.resolution_height_le.setDisabled(True)
            if tag == "<当前分辨率>":
                self.RESOLUTION_LOOKUP[tag] = self.getCurrentResolution()

        widthHeight = self.RESOLUTION_LOOKUP[tag]
        print("tag: {0}, 分辨率是: {1}".format(tag, widthHeight))
        print("optionVar 为: {0}".format(cmds.optionVar(q=self.OPT_VAR_CUSTOM_RESOLUTION)))
        self.resolution_width_le.setText(str(widthHeight[0]))
        self.resolution_height_le.setText(str(widthHeight[1]))
        cmds.optionVar(sv=[self.OPT_VAR_RESOLUTION, tag])
            
    def onOrnamentChange(self, state):
        cmds.optionVar(iv=["shotmask_show_ornament", state])
        if state:
            self.SHOW_ORNAMENT = True
        else:
            self.SHOW_ORNAMENT = False
    def onCameraClicked(self, msg):
        cur_list = [self.camera_selection.itemText(i) for i in range(self.camera_selection.count())]
        update_list = cmds.listCameras()
        update_list.insert(0, '<当前相机>')
        if set(cur_list) != set(update_list):
            self.camera_selection.clear()
            self.camera_selection.addItems(update_list)

    def onCameraChange(self, index):
        cmds.optionVar(sv=["shotmask_camera", self.camera_selection.currentText()])
    def isWidthHeightValid(self):
        if self.resolution_width_le.text() and self.resolution_height_le.text():
            return True
        else:
            return False
    def getWidthHeight(self):
        return [int(self.resolution_width_le.text()), int(self.resolution_height_le.text())]
    def getCamera(self):
        
        return self.camera_selection.currentText()
    def isShowOrnament(self):
        return self.SHOW_ORNAMENT
    def getFormat(self):
        return self.format_selection.currentText()
    def isOpenInViewer(self):
        return self.openInViewCheckBox.isChecked()
    def isPlayBlastOffScreen(self):
        return self.playBlastOffScreen.isChecked()
    def getCompression(self):
        return self.compression_selection.currentText()
    def isTimeValid(self):
        start = self.time_range_start.text()
        end = self.time_range_end.text()
        if start and end:
            return int(end) > int(start)
        else:
            return False
    def getStartTime(self):
        if self.isTimeValid():
            if self.time_range_selection.currentText() == "自定义":
                return self.CUSTOM_TIME_RANGE[0]
            else:
                return int(self.time_range_start.text())
        else:
            raise Exception("请正确填写拍屏开始时间")
    def getEndTime(self):
        if self.isTimeValid():
            if self.time_range_selection.currentText() == "自定义":
                return self.CUSTOM_TIME_RANGE[1]
            else:
                
                return int(self.time_range_end.text())
        else:
            raise Exception("请正确填写拍屏结束时间")
    
class ShotMaskPart(QtWidgets.QWidget):

    OPT_VAR_BORDER_SCALE = "shotmask_border_scale"
    OPT_VAR_BORDER_COLOR = "shotmask_border_color"
    OPT_VAR_BORDER_ALPHA = "shotmask_border_alpha"
    OPT_VAR_TEXT_COLOR  = "shotmask_text_color"
    OPT_VAR_TEXT_ALPHA = "shotmask_text_alpha"
    LINE_EDIT_SIZE = (90, 32)
    def __init__(self, parent=None):
        super(ShotMaskPart, self).__init__(parent)
        self.createWidgets()
        self.retrieve_and_set()
        self.setLayout()
        self.createConnection()

    def retrieve_and_set(self):
        if cmds.optionVar(ex=self.OPT_VAR_BORDER_SCALE):
            val = cmds.optionVar(q=self.OPT_VAR_BORDER_SCALE)
            self.border_scale_slider.setValue(val)
        else:
            self.border_scale_slider.setValue(100)
        if cmds.optionVar(ex=self.OPT_VAR_BORDER_ALPHA):
            val = cmds.optionVar(q=self.OPT_VAR_BORDER_ALPHA)
            self.border_alpha_slider.setValue(val)
        else:
            self.border_alpha_slider.setValue(100)
        if cmds.optionVar(ex=self.OPT_VAR_TEXT_ALPHA):
            val = cmds.optionVar(q=self.OPT_VAR_TEXT_ALPHA)
            self.text_alpha_slider.setValue(val)
        else:
            self.text_alpha_slider.setValue(100)
    
    def setLayout(self):
        main_layout = QtWidgets.QFormLayout(self)
        border_scale_layout = QtWidgets.QHBoxLayout()
        border_scale_layout.addWidget(self.border_scale_slider)
        border_scale_layout.addStretch()

        border_alpha_layout = QtWidgets.QHBoxLayout()
        border_alpha_layout.addWidget(self.border_alpha_slider)
        border_alpha_layout.addStretch()

        text_alpha_layout = QtWidgets.QHBoxLayout()
        text_alpha_layout.addWidget(self.text_alpha_slider)
        text_alpha_layout.addStretch()

        main_layout.addRow("<b>遮罩缩放</b>", border_scale_layout)
        main_layout.addRow("<b>遮罩透明度</b>", border_alpha_layout)
        main_layout.addRow("<b>字体透明度</b>", text_alpha_layout)

    def createWidgets(self):
        self.border_scale_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.border_scale_slider.setMinimum(100)
        self.border_scale_slider.setMaximum(150)

        self.border_alpha_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.border_alpha_slider.setMinimum(0)
        self.border_alpha_slider.setMaximum(100)

        self.text_alpha_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.text_alpha_slider.setMinimum(0)
        self.text_alpha_slider.setMaximum(100)
        
        
    def createConnection(self):    
        self.border_scale_slider.valueChanged.connect(self.onBorderScaleChange)
        self.border_alpha_slider.valueChanged.connect(self.onBorderAlphaChange)
        self.text_alpha_slider.valueChanged.connect(self.onTextAlphaChange)

    def onTextAlphaChange(self, val):
        if MyPlayBlast.SHOT_MASK_NODE_NAME:
            cmds.setAttr("{0}.tAlpha".format(MyPlayBlast.SHOT_MASK_NODE_NAME), float(val/100))
        cmds.optionVar(iv=[self.OPT_VAR_TEXT_ALPHA, val])

    def onBorderAlphaChange(self, val):
        if MyPlayBlast.SHOT_MASK_NODE_NAME:
            cmds.setAttr("{0}.borderAlpha".format(MyPlayBlast.SHOT_MASK_NODE_NAME), float(val/100))
        cmds.optionVar(iv=[self.OPT_VAR_BORDER_ALPHA, val])

    def onBorderScaleChange(self, val):      
        if MyPlayBlast.SHOT_MASK_NODE_NAME:
            cmds.setAttr("{0}.borderScale".format(MyPlayBlast.SHOT_MASK_NODE_NAME), float(val/100))
        cmds.optionVar(iv=[self.OPT_VAR_BORDER_SCALE, val])
    
    @classmethod
    def setNodeAttribute(cls):
        if cmds.optionVar(ex=cls.OPT_VAR_BORDER_SCALE):
            scale = cmds.optionVar(q=cls.OPT_VAR_BORDER_SCALE)
            cmds.setAttr("{0}.bScale".format(MyPlayBlast.SHOT_MASK_NODE_NAME), float(scale/100))
        if cmds.optionVar(ex=cls.OPT_VAR_BORDER_ALPHA):
            alpha = cmds.optionVar(q=cls.OPT_VAR_BORDER_ALPHA)
            cmds.setAttr("{0}.bAlpha".format(MyPlayBlast.SHOT_MASK_NODE_NAME), float(alpha/100))
        if cmds.optionVar(ex=cls.OPT_VAR_TEXT_ALPHA):
            alpha = cmds.optionVar(q=cls.OPT_VAR_TEXT_ALPHA)
            cmds.setAttr("{0}.tAlpha".format(MyPlayBlast.SHOT_MASK_NODE_NAME), float(alpha/100))

class MyPlayBlast(QtWidgets.QDialog):

    SHOTMASK_PLUG_NAME = "ShotMask" # 也是插件名称
    SHOTMASK_SHAPE_NAME = "ShotMaskShape"
    SHOTMASK_TRANS_NAME = "ShotMask"
    SHOTMASK_NODE_TYPE = "ShotMask"

    SAVE_PART_NAME = "<b>文件保存</b>"
    OPTION_PART_NAME = "<b>拍屏选项</b>"
    PLAYBLAST_PART_NAME = "<b>PlayBlast</b>"
    OPERATION_PART_NAME = "<b>Operation</b>"
    SCRIPT_JOB_IDs = []

    SHOT_MASK_NODE_NAME = ""
    #获取 Maya MainWindow 对象并设置为parent
    def __init__(self, parent=maya_main_window()):
        super(MyPlayBlast, self).__init__(parent)
        self.initialize()
        self.create_widgets()
        self.createConnection()
        self.set_layout()
    
    def set_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.save_header)
        main_layout.addWidget(self.save_part)

        main_layout.addWidget(self.option_header)
        main_layout.addWidget(self.option_part)

        main_layout.addWidget(self.shotmask_header)
        main_layout.addWidget(self.shotmask_part)

        
        main_layout.addLayout(self.button_layout)

        main_layout.addStretch()
    def create_widgets(self):
        self.save_header = PlayBlastHeader(self.SAVE_PART_NAME)
        self.save_part = SavePart()
        
        self.option_header = PlayBlastHeader(self.OPTION_PART_NAME)
        self.option_part = OptionPart()

        self.shotmask_header = PlayBlastHeader(self.PLAYBLAST_PART_NAME)
        self.shotmask_part = ShotMaskPart()

        self.button_layout = QtWidgets.QHBoxLayout()  
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.playButton = QtWidgets.QPushButton()
        self.playButton.setText("开始拍屏")
        self.playButton.setFont(font)
        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setText("退出插件")   
        self.cancelButton.setFont(font)
        self.button_layout.addWidget(self.playButton)
        self.button_layout.addWidget(self.cancelButton)

    def createConnection(self):
        self.playButton.clicked.connect(self.onPlayBlast)
        self.cancelButton.clicked.connect(self.onCancelWinddow)

    def onCancelWinddow(self):
        self.close()
    def initialize(self):
        cmds.loadPlugin(MyPlayBlast.SHOTMASK_PLUG_NAME)
        self.setWindowTitle("PlayBlast")
        self.setMinimumSize(500, 600)
        
    def triggerWanring(self, msg):
        msg_dialog = QtWidgets.QDialog(parent=self)
        layout = QtWidgets.QHBoxLayout()
        msg_label = QtWidgets.QLabel(msg)
        layout.addWidget(msg_label)
        msg_dialog.setLayout(layout)
        msg_dialog.show()
    def onPlayBlast(self):
        
        options = {}
        try:
            options["filename"] = self.save_part.get_save_path()
            options["widthHeight"] = self.option_part.getWidthHeight()
            options["filename"] = self.save_part.get_save_path()
            options["forceOverwrite"] = self.save_part.isOverwrite()
            options["percent"] = 100 if options["widthHeight"][0] != 1920 else 94
            options["startTime"] = self.option_part.getStartTime()
            options["endTime"] = self.option_part.getEndTime()
            options["clearCache"] = True
            options["format"] = self.option_part.getFormat()
            options["compression"] = self.option_part.getCompression()
            options["showOrnaments"] = self.option_part.isShowOrnament()
            options["viewer"] = self.option_part.isOpenInViewer()
            options["offScreen"] = self.option_part.isPlayBlastOffScreen()
            self.lookThroughCamera(self.option_part.getCamera())
            
            MyPlayBlast.createMask()
            print("当前WidthHeight是 {0}".format(options["widthHeight"]))
            cmds.playblast(**options)
            MyPlayBlast.deleteMask()

        except Exception as e:
            self.triggerWanring(str(e))

    def lookThroughCamera(self, camera):
        panel = cmds.playblast(ae=True)
        panel = panel.split("|")[-1]
        if camera != "<当前相机>":
            mel.eval("lookThroughModelPanel {0} {1}".format(camera, panel))

    def getShotMaskNode(self):
        nodes = cmds.ls(type=MyPlayBlast.SHOTMASK_NODE_TYPE)
        if len(nodes) > 0:
            return nodes[0]
        else:
            return None
        
    @classmethod
    def isMaskLoaded(cls):
        return cmds.pluginInfo(MyPlayBlast.SHOTMASK_PLUG_NAME, q=True, loaded=True)
    
    @classmethod
    def deleteMask(cls):
        if cls.isMaskLoaded():
            nodes = cmds.ls(type="ShotMask")
            if nodes:
                cls.SHOT_MASK_NODE_NAME = ""
                for node in nodes:
                    parents = cmds.listRelatives(node, parent=True, fullPath=True)
                    if parents:
                        transform = parents[0]
                        cmds.delete(transform)
        else:
            om.MGlobal.displayWarning("ShotMask 插件并未加载")
    
    @classmethod
    def createMask(cls):
        if cls.isMaskLoaded():
            if not cmds.ls(type="ShotMask"):
                    cls.SHOT_MASK_NODE_NAME = cmds.createNode("ShotMask", ss=True)
                    parent_list = cmds.listRelatives(cls.SHOT_MASK_NODE_NAME, parent=True)
                    if parent_list:
                        cmds.rename(parent_list[0], "ShotMask")
                    ShotMaskPart.setNodeAttribute()
            else:
                om.MGlobal.displayWarning("ShotMask 结点已存在")
        else:
            om.MGlobal.displayWarning("ShotMask 插件并未加载")

    def closeEvent(self, event):
        for id in self.SCRIPT_JOB_IDs:
            cmds.scriptJob(k=id, force=True)
        self.deleteMask()
        self.save_part.storeData()
        self.option_part.storeData()
        
if __name__ == "__main__":
    plugin = "MyPlayBlast.py"
    # cmds.file(new=True, f=True)
    # 如果加载了, 先卸载, 已卸载就什么也不做
    cmds.evalDeferred("if cmds.pluginInfo(\"{0}\", query=True, loaded=True) : cmds.unloadPlugin(\"{0}\")".format(plugin))
    # 重新加载
    cmds.evalDeferred("if not cmds.pluginInfo(\"{0}\", query=True, loaded=True) : cmds.loadPlugin(\"{0}\")".format(plugin))
    cmds.myplayblast()