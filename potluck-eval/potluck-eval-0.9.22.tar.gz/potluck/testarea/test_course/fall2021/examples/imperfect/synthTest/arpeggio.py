"""
Names: Peter Mawhorter
Date: 2021-8-28
Purpose: Simple demonstration of wavesynth module.
"""

from wavesynth import *


def arpeggio(startPitch, noteDuration):
    """
    Adds 5 notes to the current track, starting at the given start pitch
    and moving up 4 and then 3 half-steps, and then back down again. Each
    note will have the given duration.
    """
    setPitch(startPitch)
    addNote(0.5)
    halfStepUp(4)
    addNote(0.5)
    halfStepUp(3)
    addNote(0.5)
    halfStepDown(6)
    addNote(0.5)


# Only one test
import optimism as opt
opt.captureOutput()

arpeggio(C4, 0.5)
opt.testCase(printTrack())

opt.expectOutputContains("a 0.5s keyboard note at C4") # first
opt.expectOutputContains("and a 0.5s keyboard note at C4") # last
opt.expectOutputContains("note at E4") # 2 OR 4
opt.expectOutputContains("note at G4") # 3
