# type: ignore

from .convert import ProtocolConverter, convert_protocol, dedent, dehyphen, pretokenize
from .entities import ParlaClarinSpeechTexts, Protocol, Speech, SpeechFactory
from .term_frequency import TermFrequencyCounter, compute_term_frequencies
