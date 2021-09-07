import pytest
from digitalguide.uhrzeit_filter import FilterUhrzeit
from telegram import Message
from telegram import Chat
from datetime import datetime

@pytest.fixture
def uhrzeit_filter():
    '''Filter for the identification of datetimes'''
    return FilterUhrzeit()

@pytest.mark.parametrize("message_text", [
    (Message(121123, date=datetime.now, chat=Chat(id=1212, type ="private"), text ="0 Uhr")),
    (Message(121123, date=datetime.now, chat=Chat(id=1212, type ="private"), text ="00:00")),
    (Message(121123, date=datetime.now, chat=Chat(id=1212, type ="private"), text ="12"))
])
def test_uhrzeit_filter_on_messages(uhrzeit_filter, message_text):
    assert uhrzeit_filter.filter(message_text) == True

@pytest.mark.parametrize("message_text", [
    (Message(121123, date=datetime.now, chat=Chat(id=1212, type ="private"), text ="weiß nicht")),
    (Message(121123, date=datetime.now, chat=Chat(id=1212, type ="private"), text ="ohne")),
    (Message(121123, date=datetime.now, chat=Chat(id=1212, type ="private"), text ="leer"))
])
def test_uhrzeit_filter_on_false_messages(uhrzeit_filter, message_text):
    assert uhrzeit_filter.filter(message_text) == False