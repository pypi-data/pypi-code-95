"""Second seat card play."""

from typing import List, Union

from bridgeobjects import SUITS, Card
from bfgsupport import Board
from bfgcardplay.source import globals

from .cardplayer import Player

def second_seat_card(board: Board) -> Card:
    """Return the card if the second seat."""
    player = Player(board)
    trick = board.tricks[-1]
    cards = player.cards_for_trick_suit(trick)

    # cover honour with honour
    # TODO see this web site http://www.rpbridge.net/4l00.htm
    # if trick.cards[0].value >= 8: # nine or above
    #     for card in cards[::-1]:
    #         if card.value > trick.cards[0].value:
    #             return card

    if cards:
        return cards[-1]

    return _select_card_if_void(player)

def _select_card_if_void(player: Player) -> Card:
    """Return card if cannot follow suit."""
    # Trump if appropriate
    if player.trump_suit:
        pass


    # Signal suit preference."""
    suit = player.best_suit
    suit_cards = player.suit_cards[suit.name]
    for card in suit_cards:
        if not card.is_honour:
            return card

    other_suit = player.other_suit_for_signals(suit)
    other_suit_cards = player.suit_cards[other_suit]
    if other_suit_cards:
        return other_suit_cards[-1]

    for suit_name in SUITS:
        if suit_name != suit.name and suit_name != other_suit:
            final_suit_cards = player.suit_cards[suit_name]
            if final_suit_cards:
                return final_suit_cards[-1]

    return player.suit_cards[player.best_suit.name][0]

    raise ValueError('No card found for signalling')
