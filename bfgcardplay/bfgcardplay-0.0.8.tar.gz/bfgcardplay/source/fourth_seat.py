"""Fourth seat card play."""

from typing import List, Union, Tuple

from bridgeobjects import SUITS, Card, Denomination
from bfgsupport import Board, Trick
from .cardplayer import Player


def fourth_seat_card(board: Board) -> Card:
    """Return the card if the fourth seat."""
    player = Player(board)
    trick = board.tricks[-1]
    cards = player.cards_for_trick_suit(trick)

    if cards:
        # play singleton
        if len(cards) == 1:
            return cards[0]

        # play low if partner is winning trick
        if _second_player_winning_trick(cards, trick, player.trump_suit):
            return cards[-1]

        # win trick if possible
        winning_card = _winning_card(player, trick)
        if winning_card:
            return winning_card

        # play smallest card
        if cards:
            return cards[-1]

    return _select_card_if_void(player)

def _winning_card(player: Player, trick: Trick) -> Union[Card, None]:
    """Return the card if can win trick."""
    cards = player.cards_for_trick_suit(trick)

    (value_0, value_1, value_2) = _trick_card_values(trick, player.trump_suit)
    if cards:
        for card in cards[::-1]:
            card_value = card.value
            if card.suit == player.trump_suit:
                card_value += 13
            if card_value > value_0 and card_value > value_2:
                return card

    # No cards in trick suit, look for trump winner
    elif player.trump_cards:
        for card in player.trump_cards[::-1]:
            if card.value + 13 > value_2:
                return card
    return None

def _second_player_winning_trick(cards: List[Card], trick: Trick, trumps: Denomination) -> bool:
    """Return True if the second player is winning the trick."""
    (value_0, value_1, value_2) = _trick_card_values(trick, trumps)
    if value_1 > value_0 and value_1 > value_2:
        return True
    return False

def _trick_card_values(trick: Trick, trumps: Denomination) -> Tuple[int, int, int]:
    """Return a tuple of card values."""
    value_0 = trick.cards[0].value
    value_1 = trick.cards[1].value
    value_2 = trick.cards[2].value
    if trumps:
        if trick.cards[0].suit == trumps:
            value_0 += 13
        if trick.cards[1].suit == trumps:
            value_1 += 13
        if trick.cards[2].suit == trumps:
            value_2 += 13
    return (value_0, value_1, value_2)

def _select_card_if_void(player: Player) -> Card:
    """Return card if cannot follow suit."""
    # Trump if appropriate
    if player.trump_suit:
        pass

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
