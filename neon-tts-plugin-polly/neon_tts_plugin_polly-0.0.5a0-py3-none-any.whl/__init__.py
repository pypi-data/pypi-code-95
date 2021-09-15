# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending

import boto3

from neon_utils.configuration_utils import get_neon_tts_config
from neon_utils.logger import LOG
from neon_utils.parse_utils import format_speak_tags

try:
    from neon_audio.tts import TTS, TTSValidator
except ImportError:
    from mycroft.tts import TTS, TTSValidator
from mycroft.metrics import Stopwatch
from unidecode import unidecode

from neon_tts_plugin_polly.util import get_credentials_from_file

LOG.name = "PollyTTS"


class PollyTTS(TTS):

    def __init__(self, lang="en-us", config=None):
        config = config or get_neon_tts_config().get("polly", {})
        super(PollyTTS, self).__init__(lang, config, PollyTTSValidator(self),
                                       audio_ext="mp3",
                                       ssml_tags=["speak", "say-as", "voice",
                                                  "prosody", "break",
                                                  "emphasis", "sub", "lang",
                                                  "phoneme", "w", "whisper",
                                                  "amazon:auto-breaths",
                                                  "p", "s", "amazon:effect",
                                                  "mark"])

        if config.get("aws_access_key_id"):
            self.key_id = self.config.get("aws_access_key_id", '')
            self.key = self.config.get("aws_secret_access_key", '')
            self.region = self.config.get("region", 'us-west-2')
        elif hasattr(self, "keys") and self.keys.get("polly"):
            self.key_id = self.keys["polly"].get("key_id") or self.key_id
            self.key = self.keys["polly"].get("secret_key") or self.key
            self.region = self.keys["polly"].get("region") or self.region
        # these checks are separate in case we want to use different keys for the translate api for example
        elif hasattr(self, "keys") and self.keys.get("amazon"):
            self.key_id = self.keys["amazon"].get("key_id") or self.key_id
            self.key = self.keys["amazon"].get("secret_key") or self.key
            self.region = self.keys["amazon"].get("region") or self.region
        else:
            creds = get_credentials_from_file()
            self.key = creds.get("aws_secret_access_key", '')
            self.key_id = creds.get("aws_access_key_id", '')
            self.region = "us-west-2"

        self._voice_cache = dict()
        self.polly = boto3.Session(aws_access_key_id=self.key_id,
                                   aws_secret_access_key=self.key,
                                   region_name=self.region).client('polly')

    def get_tts(self, sentence, wav_file, speaker=None):
        stopwatch = Stopwatch()
        speaker = speaker or dict()
        # Read utterance data from passed configuration
        request_lang = speaker.get("language",  self.lang)
        # Catch Chinese alt code
        if request_lang.lower() == "zh-zh":
            request_lang = "cmn-cn"

        request_gender = speaker.get("gender", "female")
        request_voice = speaker.get("voice") or  self._get_voice(request_lang, request_gender)

        to_speak = format_speak_tags(sentence)
        LOG.debug(to_speak)
        if to_speak:
            with stopwatch:
                tts = boto3.client(service_name='polly', region_name=self.region, aws_access_key_id=self.key_id,
                                   aws_secret_access_key=self.key).synthesize_speech(OutputFormat='mp3',
                                                                                     Text=to_speak,
                                                                                     TextType='ssml',
                                                                                     VoiceId=request_voice)
            LOG.debug(f"Polly time={stopwatch.time}")

            with stopwatch:
                with open(str(wav_file), 'wb') as speak_file:
                    sound_bytes = tts['AudioStream'].read()
                    speak_file.write(sound_bytes)
                    # speak_file.close()
            LOG.debug(f"File access time={stopwatch.time}")
        return wav_file, None

    def _get_voice(self, language, gender) -> str:
        stopwatch = Stopwatch()
        with stopwatch:
            lang, reg = language.split("-")
            lang_code = f"{lang}-{reg.upper()}"

            cache_key = f"{lang_code}_{gender}"
            if cache_key in self._voice_cache:
                LOG.debug(f"get cached voice={stopwatch.time}")
                sel_voice = self._voice_cache[cache_key]
            else:
                data = self.polly.describe_voices(LanguageCode=lang_code)
                voices = [voice.get('Name') for voice in data.get("Voices") if voice.get("Gender") == gender.title()]
                if len(voices) == 0:
                    LOG.warning("No voices available for the requested language and gender")
                    LOG.debug(voices)
                    voices = [voice.get('Name') for voice in data.get("Voices")]
                if "Joanna" in voices:
                    sel_voice = "Joanna"
                elif "Joey" in voices:
                    sel_voice = "Joey"
                else:
                    sel_voice = unidecode(voices[0])
            self._voice_cache[cache_key] = sel_voice
        LOG.debug(f"Get Voice time={stopwatch.time}")
        return sel_voice


class PollyTTSValidator(TTSValidator):
    def __init__(self, tts):
        super(PollyTTSValidator, self).__init__(tts)

    def validate_lang(self):
        # TODO
        pass

    def validate_dependencies(self):
        try:
            from boto3 import Session
        except ImportError:
            raise Exception(
                'PollyTTS dependencies not installed, please run pip install '
                'boto3 ')

    def validate_connection(self):
        pass
        # try:
        #     # if not self.tts.voice:
        #     #     raise Exception("Polly TTS Voice not configured")
        #     self.tts.describe_voices()
        # except TypeError:
        #     raise Exception(
        #         'PollyTTS server could not be verified. Please check your '
        #         'internet connection and credentials.')

    def get_tts_class(self):
        return PollyTTS


if __name__ == "__main__":
    e = PollyTTS()
    ssml = """<speak>
     This is my original voice, without any modifications. <amazon:effect vocal-tract-length="+15%"> 
     Now, imagine that I am much bigger. </amazon:effect> <amazon:effect vocal-tract-length="-15%"> 
     Or, perhaps you prefer my voice when I'm very small. </amazon:effect> You can also control the 
     timbre of my voice by making minor adjustments. <amazon:effect vocal-tract-length="+10%"> 
     For example, by making me sound just a little bigger. </amazon:effect><amazon:effect 
     vocal-tract-length="-10%"> Or, making me sound only somewhat smaller. </amazon:effect> 
</speak>"""
    e.get_tts(ssml, "polly.mp3")
