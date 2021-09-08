""" Opening leads for Card Player."""
from typing import Union

from bridgeobjects import Card, SEATS
from bfgsupport import Board

from .opening_lead_card import opening_lead_card
from .opening_lead_suit import opening_lead_suit
from .first_seat import first_seat_card
from .second_seat import second_seat_card
from .third_seat import third_seat_card
from .fourth_seat import fourth_seat_card
# from .globals import  initialize_manager


def next_card(board: Board) -> Union[Card, None]:
    """Return the suggested card from the current status of the board."""
    unplayed_cards_in_board = 0
    for seat in SEATS:
        unplayed_cards_in_board += len(board.hands[seat].unplayed_cards)

    # if unplayed_cards_in_board == 52:
    #     manager = initialize_manager()
    #     manager.board = board
    #     manager.set_declarer_strategy()

    if unplayed_cards_in_board == 0:
        return None
    if len(board.tricks[-1].cards) == 0:
        return _trick_lead(board)
    elif len(board.tricks[-1].cards) == 1:
        return second_seat_card(board)
    elif len(board.tricks[-1].cards) == 2:
        return third_seat_card(board)
    elif len(board.tricks[-1].cards) == 3:
        return fourth_seat_card(board)

def _trick_lead(board: Board) -> Card:
    """Return the card if the first card of a trick."""
    if len(board.tricks) == 1:
        (opening_suit, opening_card) = _opening_lead(board)
        return opening_card
    else:
        return first_seat_card(board)

def _opening_lead(board: Board) -> Card:
    """Return the proposed opening lead for the board."""
    if not board.contract.declarer:
        return None
    opening_suit = opening_lead_suit(board)
    cards = [card for card in board.hands[board.contract.leader].cards if card.suit == opening_suit]
    opening_card = opening_lead_card(cards, board.contract)
    return (opening_suit, opening_card)
