from cxwidgets.aQt.QtDesigner import QPyDesignerCustomWidgetPlugin, QPyDesignerTaskMenuExtension, QExtensionFactory
from cxwidgets.aQt.QtGui import QIcon
from cxwidgets.aQt.QtWidgets import QDialog, QDialogButtonBox
from pyqtgraph import GraphicsLayoutWidget


class GraphicsLayoutWidgetPlagin(QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initialized = False

    def name(self):
        return 'GraphicsLayoutWidget'

    def group(self):
        return 'pyqtgraph widgets'

    def icon(self):
        return QIcon()

    def isContainer(self):
        return False

    def includeFile(self):
        return 'pyqtgraph'

    def toolTip(self):
        return 'pyqtgraph GraphicsLayoutWidget'

    def whatsThis(self):
        return 'pyqtgraph GraphicsLayoutWidget'

    def createWidget(self, parent):
        return GraphicsLayoutWidget(parent)

    def initialize(self, formEditor):
        if self.initialized:
            return
        manager = formEditor.extensionManager()
        print(dir(manager))
        if manager:
            print('adding factory')
            self.factory = GraphicsLayoutTaskMenuFactory(manager)
            manager.registerExtensions(self.factory,"com.cx.pg.TaskMenu")
        self.initialized = True

    def isInitialized(self):
        return self.initialized


class GraphicsLayoutDialog(QDialog):
    def __init__(self, widget, parent=None):
        super().__init__(parent)
        print("GraphicsLayoutDialog")
        self.widget = widget

        buttonBox = QDialogButtonBox()
        okButton = buttonBox.addButton(buttonBox.Ok)
        okButton.clicked.connect(self.ok_ev)
        cancelButton = buttonBox.addButton(buttonBox.Cancel)
        cancelButton.clicked.connect()

        layout = QGridLayout()
        #layout.addWidget(self.previewWidget, 1, 0, 1, 2)
        layout.addWidget(buttonBox, 2, 0, 1, 2)
        self.setLayout(layout)

        self.setWindowTitle("Update Location")

    def ok_ev(self):
        print('ok')
        self.accept()

    def cancel_ev(self):
        print('cancel')
        self.reject()


class GraphicsLayoutMenuEntry(QPyDesignerTaskMenuExtension):
    def __init__(self, widget, parent):
        QPyDesignerTaskMenuExtension.__init__(parent)
        print("menu entry")
        self.widget = widget
        self.editStateAction = QAction("Update Location...", self)
        self.editStateAction.triggered.connect(self.updateValues)

    def preferredEditAction(self):
        return self.editStateAction

    def taskActions(self):
        return [self.editStateAction]

    def updateValues(self):
        dialog = GraphicsLayoutDialog(self.widget)
        dialog.exec_()


class GraphicsLayoutTaskMenuFactory(QExtensionFactory):
    def __init__(self, parent = None):
        super().__init__(parent)
        print("GraphicsLayoutTaskMenuFactory")

    def createExtension(self, obj, iid, parent):
        print("create extancion call", iid)
        if iid != "com.cx.pg.TaskMenu":
            print('other iid')
            return None
        if isinstance(obj, GraphicsLayoutWidget):
            return GraphicsLayoutMenuEntry(obj, parent)
        print('do nothing')
        return None


