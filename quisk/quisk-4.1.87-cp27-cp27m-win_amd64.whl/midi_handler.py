# This module implements Midi processing in Quisk. The OnReadMIDI() method is called for any Midi bytes
# received. Do not change this file. If you want to replace it with your own Midi handler, create a
# configuration file, copy this file into it and make any changes there. Quisk will use your configuration
# file MidiHandler instead of this one.

# Midi messages are generally three bytes long. The first byte is the status and has the most significant bit set.
# Subsequent bytes have the most significant bit zero. The status byte of a channel message is a 1 bit, three bits of message
# type and 4 bits of channel number. This is followed by two bytes of data.

# For Note On (status 0x9?) and Note Off (status 0x8?) the data bytes are the note number and velocity. Velocity
# indicates how hard the key was pressed. If the velocity of a Note On message is zero it is treated the same as Note Off.

# For a control change (status = 0xB?) the data bytes are the controller number and the controller value. For some controllers
# it only matters if the value is less than 64 (down) or 64 or greater (up). For other controllers the value 0 to 127
# is the actual control setting.

# To access the Quisk radio volume control, use self.app.sliderVol.GetDecValue(). The value is 0.0 to 1.0. To set
# the value use self.app.sliderVol.SetDecValue(value). The value will be changed to 0.0 to 1.0 if out of range.


class MidiHandler:	# Quisk calls this to make the Midi handler instance.
  def __init__(self, app, conf):
    self.app = app		# The application object
    self.conf = conf		# The configuration settings
    self.midi_message = []	# Save Midi bytes until a whole message is received.
  def OnReadMIDI(self, byts):	# Quisk calls this for any Midi bytes received.
    for byt in byts:
      if byt & 0x80:		# this is a status byte and the start of a new message
        self.midi_message = [byt]
      else:
        self.midi_message.append(byt)
      if len(self.midi_message) == 3:
        status   = self.midi_message[0]
        status = status & 0xF0	# Ignore channel
        if status == 0x90:	# Note On
          note     = self.midi_message[1]
          velocity = self.midi_message[2]
          if velocity == 0:	# Note On with zero velocity is the same as note Off
            pass
          else:
            try:
              name = self.app.local_conf.MidiNoteDict[str(note)]
              btn = self.app.idName2Button[name]
            except:
              pass #traceback.print_exc()
            else:
              btn.Shortcut(None, name)
        elif status == 0x80:	# Note Off
          pass
        elif status == 0xB0:	# Control Change
          controller = self.midi_message[1]
          value      = self.midi_message[2]
          if controller == 88:
            oldfreq = self.app.txFreq + self.app.VFO
            if value < 64:
              pass
            else:
              pass
