import logging

from typing import Text, List, Optional, Dict, Any

from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.training_data import TrainingData, Message
from rasa.nlu.components import Component
from custom_func.generator import generateur_Ar
from custom_func.translator_darijaFr_DarijaAr import trans 
from rasa.nlu.constants import (
    RESPONSE,
    TEXT,
    CLS_TOKEN,
    TOKENS_NAMES,
    MESSAGE_ATTRIBUTES,
    INTENT,
)

logger = logging.getLogger(__name__)


class Token(object):
    def __init__(
        self,
        text: Text,
        start: int,
        end: Optional[int] = None,
        data: Optional[Dict[Text, Any]] = None,
        lemma: Optional[Text] = None,
    ) -> None:
        self.text = text
        self.start = start
        self.end = end if end else start + len(text)

        self.data = data if data else {}
        self.lemma = lemma or text

    def set(self, prop: Text, info: Any) -> None:
        self.data[prop] = info

    def get(self, prop: Text, default: Optional[Any] = None) -> Any:
        return self.data.get(prop, default)

    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return (self.start, self.end, self.text, self.lemma) == (
            other.start,
            other.end,
            other.text,
            other.lemma,
        )

    def __lt__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return (self.start, self.end, self.text, self.lemma) < (
            other.start,
            other.end,
            other.text,
            other.lemma,
        )


class Tokenizer(Component):
    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework."""

        super().__init__(component_config)

        # flag to check whether to split intents
        self.intent_tokenization_flag = self.component_config.get(
            "intent_tokenization_flag", False
        )
        # split symbol for intents
        self.intent_split_symbol = self.component_config.get("intent_split_symbol", "_")

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        """Tokenizes the text of the provided attribute of the incoming message."""

        raise NotImplementedError

    
    

    def _split_intent(self, message: Message):
        text = message.get(INTENT)

        words = (
            text.split(self.intent_split_symbol)
            if self.intent_tokenization_flag
            else [text]
        )

        return self._convert_words_to_tokens(words, text)

    
    

    @staticmethod
    def _convert_words_to_tokens_corrected(words: List[Text], text: Text, words_corr: List[Text]) -> List[Token]:
        running_offset = 0
        list_off = []
        list_len = []
        tokens = []
        print(words_corr)
        print(words)
        for word in words:
            for word_corr in words_corr :
                print(word)
                print(word_corr)
                word_offset = text.index(word, running_offset)
                word_len = len(word)
                running_offset = word_offset + word_len
                tokens.append(Token(word_corr, word_offset))

        return tokens
    
    @staticmethod
    def _convert_words_to_tokens(words: List[Text], text: Text) -> List[Token]:
        running_offset = 0
        tokens = []
        
        for word in words:
                word_offset = text.index(word, running_offset)
                word_len = len(word)
                running_offset = word_offset + word_len
                tokens.append(Token(word, word_offset))

        return tokens

    @staticmethod
    def add_cls_token(tokens: List[Token], attribute: Text) -> List[Token]:
        if attribute in [RESPONSE, TEXT] and tokens:
            # +1 to have a space between the last token and the __cls__ token
            idx = tokens[-1].end + 1
            tokens.append(Token(CLS_TOKEN, idx))

        return tokens
