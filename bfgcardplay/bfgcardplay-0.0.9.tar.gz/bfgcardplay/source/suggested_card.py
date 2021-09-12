# suggested_card.py

"""Suggested card for Card Player."""
from typing import Union

from bridgeobjects import Card, SEATS
from bfgsupport import Board

from .player import Player
from .opening_lead_card import opening_lead_card
from .opening_lead_suit import opening_lead_suit
from .first_seat_defender import FirstSeatDefender
from .first_seat_declarer import FirstSeatDeclarer
from .second_seat_defender import SecondSeatDefender
from .second_seat_declarer import SecondSeatDeclarer
from .third_seat_defender import ThirdSeatDefender
from .third_seat_declarer import ThirdSeatDeclarer
from .fourth_seat_defender import FourthSeatDefender
from .fourth_seat_declarer import FourthSeatDeclarer

import bfgcardplay.source.global_variables as global_vars

def next_card(board: Board) -> Union[Card, None]:
    """Return the suggested card from the current status of the board."""
    unplayed_cards_in_board = _unplayed_cards(board)

    if unplayed_cards_in_board == 52:
        global_vars.initialize()
        return _opening_lead(board)
    if unplayed_cards_in_board == 0:
        return None

    trick_cards = len(board.tricks[-1].cards)
    player = Player(board)
    if trick_cards == 0:
        return first_seat_card(player)
    if trick_cards == 1:
        return second_seat_card(player)
    if trick_cards == 2:
        return third_seat_card(player)
    if trick_cards == 3:
        return fourth_seat_card(player)
    raise ValueError (f'No card to return for {board}')

def _opening_lead(board: Board) -> Card:
    """Return the proposed opening lead for the board."""
    if not board.contract.declarer:
        return None
    opening_suit = opening_lead_suit(board)
    leader = board.contract.leader
    leaders_cards = board.hands[leader].cards
    cards = [card for card in leaders_cards if card.suit == opening_suit]
    opening_card = opening_lead_card(cards, board.contract)
    return opening_card

def first_seat_card(player: Player) -> Card:
    """Return the card for the first seat."""
    if player.is_defender:
        selected_card = FirstSeatDefender(player).selected_card()
    else:
        selected_card = FirstSeatDeclarer(player).selected_card()
    return selected_card

def second_seat_card(player: Player) -> Card:
    """Return the card for the second seat."""
    if player.is_defender:
        selected_card = SecondSeatDefender(player).selected_card()
    else:
        selected_card = SecondSeatDeclarer(player).selected_card()
    return selected_card

def third_seat_card(player: Player) -> Card:
    """Return the card for the third seat."""
    if player.is_defender:
        selected_card = ThirdSeatDefender(player).selected_card()
    else:
        selected_card = ThirdSeatDeclarer(player).selected_card()
    return selected_card

def fourth_seat_card(player: Player) -> Card:
    """Return the card for the fourth seat."""
    if player.is_defender:
        selected_card = FourthSeatDefender(player).selected_card()
    else:
        selected_card = FourthSeatDeclarer(player).selected_card()
    return selected_card

def _unplayed_cards(board: Board):
    unplayed_cards = 0
    for seat in SEATS:
        unplayed_cards += len(board.hands[seat].unplayed_cards)
    return unplayed_cards
