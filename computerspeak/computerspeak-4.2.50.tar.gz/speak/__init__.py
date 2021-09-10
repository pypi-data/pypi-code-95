import pyttsx3

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')


def speaker(audio):
    engine.say(audio)
    engine.runAndWait()


def change(number):
    engine.setProperty('voice', voices[number].id)


  