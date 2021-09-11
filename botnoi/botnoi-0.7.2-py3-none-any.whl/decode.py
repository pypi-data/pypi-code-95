# This file is part of audioread.
import audioread
import sys
import os
import wave
import contextlib
import speech_recognition as sr

def decodeaudio(filename):
    with audioread.audio_open(filename) as f:
        with contextlib.closing(wave.open(filename.split('.')[0] + '.wav', 'w')) as of:
            of.setnchannels(f.channels)
            of.setframerate(f.samplerate)
            of.setsampwidth(2)
			for buf in f:
                of.writeframes(buf)

def transcribeaudio(aufile,lang='th-TH'):
	r = sr.Recognizer()
	decode.decodeaudio(aufile)
	with sr.AudioFile(aufile) as source:
    	audio = r.record(source)  # read the entire audio file
	try:
    	result = r.recognize_google(audio,language=lang)
	except sr.UnknownValueError:
    	result = "unknown error"
	except sr.RequestError as e:
    	result = "could not request service"
	return result

  def deletefile(aufile):
    try:
        os.remove(aufile)
    except:
        pass