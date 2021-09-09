import sys
sys.path.append('.')

from commind import core
from commind.core import *
from commind.v import *
from commind.ui import *
from commind.help import *

import commind.ui.mainwindow
import commind.help.info

def main():
    print(commind.help.info.help())
    commind.ui.mainwindow.run()

if __name__ == "__main__":
    main()