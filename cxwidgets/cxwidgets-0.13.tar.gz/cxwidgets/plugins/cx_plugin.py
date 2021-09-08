from cxwidgets.aQt.QtDesigner import QPyDesignerCustomWidgetPlugin
from cxwidgets.aQt.QtGui import QIcon
from cxwidgets import CXDoubleSpinBox, CXSpinBox, CXLCDNumber, CXCheckBox, CXTextComboBox
from cxwidgets import CXPushButton, CXLineEdit, CXProgressBar, CXSwitch, CXDevSwitch, CXIntLabel, CXDoubleLabel, CXStrLabel
from cxwidgets import CXEventLed, CXStateLed


class CXDoubleSpinBoxWidgetPlugin(QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        super().__init__(parent)

    def name(self):
        return 'CXDoubleSpinBox'

    def group(self):
        return 'CX custom widgets'

    def icon(self):
        return QIcon()

    def isContainer(self):
        return False

    def includeFile(self):
        return 'cxwidgets'

    def toolTip(self):
        return 'double spinbox adapted to CX control system'

    def whatsThis(self):
        return 'double spinbox adapted to CX control system'

    def createWidget(self, parent):
        return CXDoubleSpinBox(parent)


class CXSpinBoxWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXSpinBox'

    def toolTip(self):
        return 'CXSpinBox connected to CX'

    def whatsThis(self):
        return 'CXSpinBox connected to CX'

    def createWidget(self, parent):
        return CXSpinBox(parent)


class CXLCDNumberWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXLCDNumber'

    def toolTip(self):
        return 'a LCDNumber connected to CX'

    def whatsThis(self):
        return 'a LCDNumber connected to CX'

    def createWidget(self, parent):
        return CXLCDNumber(parent)


class CXLCheckBoxWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXCheckBox'

    def toolTip(self):
        return 'CheckBox connected to CX'

    def whatsThis(self):
        return 'CheckBox connected to CX'

    def createWidget(self, parent):
        return CXCheckBox(parent)


class CXTextComboBoxWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXTextComboBox'

    def toolTip(self):
        return 'CXTextComboBox connected to CX'

    def whatsThis(self):
        return 'CXTextComboBox connected to CX'

    def createWidget(self, parent):
        return CXTextComboBox(parent)


class CXPushButtonWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXPushButton'

    def toolTip(self):
        return 'CXPushButton connected to CX'

    def whatsThis(self):
        return 'CXPushButton connected to CX'

    def createWidget(self, parent):
        return CXPushButton(parent)


class CXLineEditWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXLineEdit'

    def toolTip(self):
        return 'CXLineEdit connected to CX'

    def whatsThis(self):
        return 'CXLineEdit connected to CX'

    def createWidget(self, parent):
        return CXLineEdit(parent)


class CXProgressBarWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXProgressBar'

    def toolTip(self):
        return 'CXProgressBar connected to CX'

    def whatsThis(self):
        return 'CXProgressBar connected to CX'

    def createWidget(self, parent):
        return CXProgressBar(parent)


class CXSwitchWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXSwitch'

    def toolTip(self):
        return 'CXSwitch connected to CX'

    def whatsThis(self):
        return 'CXSwitch connected to CX'

    def createWidget(self, parent):
        return CXSwitch(parent)


class CXDevSwitchWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXDevSwitch'

    def toolTip(self):
        return 'CXDevSwitch connected to CX'

    def whatsThis(self):
        return 'CXDevSwitch connected to CX'

    def createWidget(self, parent):
        return CXDevSwitch(parent)


class CXEventLedWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXEventLed'

    def toolTip(self):
        return 'EventLed connected to CX'

    def whatsThis(self):
        return 'EventLed connected to CX'

    def createWidget(self, parent):
        return CXEventLed(parent)


class CXStateLedWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXStateLed'

    def toolTip(self):
        return 'StateLed connected to CX'

    def whatsThis(self):
        return 'StateLed connected to CX'

    def createWidget(self, parent):
        return CXStateLed(parent)


class CXIntLabelWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXIntLabel'

    def toolTip(self):
        return 'Label connected to CX int channel'

    def whatsThis(self):
        return 'Label connected to CX int channel'

    def createWidget(self, parent):
        return CXIntLabel(parent)


class CXDoubleLabelWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXDoubleLabel'

    def toolTip(self):
        return 'Label connected to CX double channel'

    def whatsThis(self):
        return 'Label connected to CX double channel'

    def createWidget(self, parent):
        return CXDoubleLabel(parent)


class CXStrLabelWidgetPlugin(CXDoubleSpinBoxWidgetPlugin):
    def name(self):
        return 'CXStrLabel'

    def toolTip(self):
        return 'Label connected to CX str channel'

    def whatsThis(self):
        return 'Label connected to CX str channel'

    def createWidget(self, parent):
        return CXStrLabel(parent)

