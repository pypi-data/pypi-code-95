from typing import List, Type
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
from swimlane_platform.upgrade_steps.upgrade_from_700_701 import UpgradeFrom700To701
from swimlane_platform.upgrade_steps.upgrade_from_701_800 import UpgradeFrom701To800
from swimlane_platform.upgrade_steps.upgrade_from_800_801 import UpgradeFrom800To801
from swimlane_platform.upgrade_steps.upgrade_from_801_900 import UpgradeFrom801To900
from swimlane_platform.upgrade_steps.upgrade_from_900_910 import UpgradeFrom900To910
from swimlane_platform.upgrade_steps.upgrade_from_910_911 import UpgradeFrom910To911
from swimlane_platform.upgrade_steps.upgrade_from_911_912 import UpgradeFrom911To912
from swimlane_platform.upgrade_steps.upgrade_from_912_1000 import UpgradeFrom912To1000
from swimlane_platform.upgrade_steps.upgrade_from_1000_1001 import UpgradeFrom1000To1001
from swimlane_platform.upgrade_steps.upgrade_from_1001_1002 import UpgradeFrom1001To1002
from swimlane_platform.upgrade_steps.upgrade_from_1002_1010 import UpgradeFrom1002To1010
from swimlane_platform.upgrade_steps.upgrade_from_1010_1011 import UpgradeFrom1010To1011
from swimlane_platform.upgrade_steps.upgrade_from_1011_1012 import UpgradeFrom1011To1012
from swimlane_platform.upgrade_steps.upgrade_from_1012_1013 import UpgradeFrom1012To1013
from swimlane_platform.upgrade_steps.upgrade_from_1013_1020 import UpgradeFrom1013To1020
from swimlane_platform.upgrade_steps.upgrade_from_1020_1022 import UpgradeFrom1020To1022
from swimlane_platform.upgrade_steps.upgrade_from_1022_1030 import UpgradeFrom1022To1030
from swimlane_platform.upgrade_steps.upgrade_from_1030_1040rc2 import UpgradeFrom1030To1040rc2
from swimlane_platform.upgrade_steps.upgrade_from_1040rc2_1040rc3 import UpgradeFrom1040rc2To1040rc3
from swimlane_platform.upgrade_steps.upgrade_from_1040rc3_1040 import UpgradeFrom1040rc3To1040
from swimlane_platform.upgrade_steps.upgrade_from_1040_1041 import UpgradeFrom1040To1041
from swimlane_platform.upgrade_steps.upgrade_from_1041_1042 import UpgradeFrom1041To1042

Upgrades = [
    UpgradeFrom700To701,
    UpgradeFrom701To800,
    UpgradeFrom800To801,
    UpgradeFrom801To900,
    UpgradeFrom900To910,
    UpgradeFrom910To911,
    UpgradeFrom911To912,
    UpgradeFrom912To1000,
    UpgradeFrom1000To1001,
    UpgradeFrom1001To1002,
    UpgradeFrom1002To1010,
    UpgradeFrom1010To1011,
    UpgradeFrom1011To1012,
    UpgradeFrom1012To1013,
    UpgradeFrom1013To1020,
    UpgradeFrom1020To1022,
    UpgradeFrom1022To1030,
    UpgradeFrom1030To1040rc2,
    UpgradeFrom1040rc2To1040rc3,
    UpgradeFrom1040rc3To1040,
    UpgradeFrom1040To1041,
    UpgradeFrom1041To1042
]  # type: List[Type[UpgradeStep]]
