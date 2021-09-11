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
    addNote(noteDuration)
    halfStepUp(4)
    addNote(noteDuration)
    halfStepUp(3)
    addNote(noteDuration)
    halfStepDown(3)
    addNote(noteDuration)
    halfStepDown(4)
    addNote(noteDuration)


# Tests using printTrack
import optimism as opt
opt.captureOutput()

arpeggio(C4, 0.5)
opt.testCase(printTrack())

opt.expectOutputContains("a 0.5s keyboard note at C4") # first
opt.expectOutputContains("and a 0.5s keyboard note at C4") # last
opt.expectOutputContains("note at E4") # 2 OR 4
opt.expectOutputContains("note at G4") # 3

eraseTrack()

arpeggio(B3, 0.3)
opt.testCase(printTrack())

opt.expectOutputContains("a 0.3s keyboard note at B3") # first
opt.expectOutputContains("and a 0.3s keyboard note at B3") # last
opt.expectOutputContains("note at Eb4") # 2 OR 4
opt.expectOutputContains("note at Gb4") # 3
