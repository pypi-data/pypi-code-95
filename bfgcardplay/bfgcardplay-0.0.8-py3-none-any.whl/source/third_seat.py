""" Third seat card play."""

import logging
log = logging.getLogger(__name__)

from typing import List, Union, Tuple

from bridgeobjects import SUITS, Card, Denomination
from bfgsupport import Board, Trick

from .cardplayer import Player
from .third_seat_defender import ThirdSeatDefender
from .third_seat_declarer import ThirdSeatDeclarer

def third_seat_card(board) -> Card:
    """Return the card for the third seat."""
    player = Player(board)
    if player.is_defender:
        selected_card = ThirdSeatDefender(player).selected_card()
    else:
        selected_card = ThirdSeatDeclarer(player).selected_card()
    return selected_card