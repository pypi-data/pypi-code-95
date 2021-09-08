from cxwidgets.aQt.QtDesigner import QPyDesignerCustomWidgetPlugin
from cxwidgets.aQt.QtGui import QIcon
from cxwidgets import PDoubleSpinBox, PCheckBox, PLCDNumber, PSpinBox, LedWidget


class PDoubleSpinBoxWidgetPlugin(QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        super().__init__(parent)

    def name(self):
        return 'PDoubleSpinBox'

    def group(self):
        return 'polymorph widgets'

    def icon(self):
        return QIcon()

    def isContainer(self):
        return False

    def includeFile(self):
        return 'cxwidgets'

    def toolTip(self):
        return 'a double spinbox from polymorphs'

    def whatsThis(self):
        return 'a double spinbox from polymorphs'

    def createWidget(self, parent):
        return PDoubleSpinBox(parent)


class PComboBoxWidgetPlugin(PDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'PCheckBox'

    def toolTip(self):
        return 'checkbox from polymorphs'

    def whatsThis(self):
        return 'checkbox from polymorphs'

    def createWidget(self, parent):
        return PCheckBox(parent)


class PLCDNumberWidgetPlugin(PDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'PLCDNumber'

    def toolTip(self):
        return 'LCDNumber from polymorphs'

    def whatsThis(self):
        return 'LCDNumber from polymorphs'

    def createWidget(self, parent):
        return PLCDNumber(parent)


class PSpinBoxWidgetPlugin(PDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'PSpinBox'

    def toolTip(self):
        return 'spinbox from polymorphs'

    def whatsThis(self):
        return 'spinbox from polymorphs'

    def createWidget(self, parent):
        return PSpinBox(parent)


class LedPlugin(PDoubleSpinBoxWidgetPlugin):
    def name(self):
        return "LedWidget"

    def toolTip(self):
        return "LED-like"

    def whatsThis(self):
        return "LED-like"

    def createWidget(self, parent):
        return LedWidget(parent)

