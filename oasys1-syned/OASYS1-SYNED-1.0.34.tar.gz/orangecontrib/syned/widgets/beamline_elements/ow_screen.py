
from orangecontrib.syned.widgets.gui.ow_optical_element import OWOpticalElement

from syned.beamline.optical_elements.ideal_elements.screen import Screen

class OWScreen(OWOpticalElement):

    name = "Screen"
    description = "Syned: Screen"
    icon = "icons/screen.png"
    priority = 4

    def __init__(self):
        super().__init__()

    def draw_specific_box(self):
        pass

    def get_optical_element(self):
        return Screen(name=self.oe_name)



