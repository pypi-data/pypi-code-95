""" First seat card play."""

import logging
log = logging.getLogger(__name__)

from typing import List, Dict, Union
import random

from bridgeobjects import SUITS, Card, Suit, SEATS, CARD_NAMES
from bfgsupport import Board

from .cardplayer import Player
from .first_seat_defender import FirstSeatDefender
from .first_seat_declarer import FirstSeatDeclarer

def first_seat_card(board: Board) -> Card:
    """Return the card if the first seat."""
    player = Player(board)
    suit = _select_lead_suit(player)
    selected_card = _select_card_from_suit(player, suit)
    # print(player.seat, selected_card)
    return selected_card

def _select_card_from_suit(player, suit):
    """Return the card to lead from the given suit."""
    if player.is_declarer or player.is_dummy:
        return FirstSeatDeclarer().select_lead_card(player, suit)
    else:
        cards = player.suit_cards[suit.name]

        # Top of touching honours
        for index, card in enumerate(cards[:-1]):
            if card.is_honour and card.value == cards[index+1].value + 1:
                return card

        # Top of doubleton
        if len(cards) == 2:
            return cards[0]

        # Return bottom card
        return cards[-1]

def _select_lead_suit(player: Player) -> Suit:
    """Return the suit for the lead."""
    if player.is_defender:
        return _select_lead_suit_for_defender(player)
    else:
        return _select_lead_suit_for_declarer(player)

def _select_lead_suit_for_declarer(player: Player) -> Suit:
    """Return the trick lead suit for the declarer."""
    if player.board.contract.is_nt:
        return FirstSeatDeclarer().select_lead_suit_for_suit_contract(player)  # TODO needs changing
    else:
        return FirstSeatDeclarer().select_lead_suit_for_suit_contract(player)  # TODO needs changing

def _select_lead_suit_for_defender(player: Player) -> Suit:
    """Return the trick lead suit for the defender."""
    if player.board.contract.is_nt:
        return FirstSeatDefender().select_lead_suit_for_suit_contract(player)
    else:
        return FirstSeatDefender().select_lead_suit_for_suit_contract(player)
