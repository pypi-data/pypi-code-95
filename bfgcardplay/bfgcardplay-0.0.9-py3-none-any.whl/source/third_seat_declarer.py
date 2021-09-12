"""Third seat card play for declarer."""

import logging
log = logging.getLogger(__name__)

from typing import List, Union, Dict
from termcolor import colored

from bridgeobjects import SUITS, Card, Denomination
from bfgsupport import Board, Trick
from .player import Player
from .third_seat import ThirdSeat
import bfgcardplay.source.global_variables as global_vars


class ThirdSeatDeclarer(ThirdSeat):
    def __init__(self, player: Player):
        super().__init__(player)

    def selected_card(self) -> Card:
        """Return the card if the third seat."""
        player = self.player
        trick = player.board.tricks[-1]
        cards = player.cards_for_trick_suit(trick)
        if cards:
            # play singleton
            if len(cards) == 1:
                return cards[0]

            manager = global_vars.manager
            suit = cards[0].suit
            if suit == manager.winning_suit:
                if manager.long_player == player.seat:
                    if player.partners_suit_cards[suit.name]:
                        # While short hand has cards, long hand plays bottom card
                        return cards[-1]
                    else:
                        return cards[0]
                else:
                    # short hand always plays top card
                    return cards[0]

            # win trick if possible
            winning_card = self._winning_card(player, trick)
            if winning_card:
                return winning_card

            # If there is long suit make sure we lead toward higher card
            long_suits = player.partnership_long_suits()
            for suit in long_suits:
                if player.can_lead_toward_tenace(suit):
                    if winning_card:
                        return winning_card

            return cards[-1]
        return self._select_card_if_void(player, trick)

    def _winning_card(self, player: Player, trick: Trick) -> Union[Card, None]:
        """Return the card if can win trick."""
        cards = player.cards_for_trick_suit(trick)

        (value_0, value_1) = self._trick_card_values(trick, player.trump_suit)
        if cards:
            # print(f'{player.seat=}, {value_0=}, {value_1=}, {cards=}')
            if cards[-1].value > value_0 and cards[-1].value > value_1:
                return cards[-1]
            for index, card in enumerate(cards[:-1]):
                card_value = card.value

                # trick card values already adjusted for trumps
                if card.suit == player.trump_suit:
                    card_value += 13

                if (card_value > value_0 + 1 and
                        card_value > value_1 and
                        card.value != cards[index+1].value + 1):
                    if not self._ace_is_deprecated(trick, card):
                        return card

        # No cards in trick suit, look for trump winner
        elif player.trump_cards:
            print('third player trumps')
            for card in player.trump_cards[::-1]:
                if card.value + 13 > value_0 + 1 and card.value + 13 > value_1:
                    return card
        return None

    def _select_card_if_void(self, player: Player, trick: Trick) -> Card:
        """Return card if cannot follow suit."""
        # Trump if appropriate
        if player.trump_suit:
            if not self.partners_card_is_winner(trick):
                opponents_trumps = player.opponents_cards[player.trump_suit.name]
                if player.trump_cards and not opponents_trumps:
                    return player.trump_cards[-1]
                if player.trump_cards and opponents_trumps:
                    over_trump_partner = self._overtrump_partner(player, trick)
                    if over_trump_partner:
                        return player.trump_cards[-1]

        opponents_cards = player.opponents_cards[trick.suit.name]

        # Find card to discard
        suits ={suit_name: suit for suit_name, suit in SUITS.items() if suit_name != player.trump_suit.name}

        # Find a loser
        suit_length: Dict[str, int] = {}
        for suit_name, suit in suits.items():
            if player.suit_cards[suit_name]:
                suit_length[suit_name] = len(player.suit_cards[suit_name])
                our_cards = player.our_cards[suit_name]
                opponents_cards = player.opponents_cards[suit_name]
                if opponents_cards:
                    if our_cards[0].value < opponents_cards[0].value:  # TODO take into account length
                        return player.suit_cards[suit_name][-1]
                else:
                    return player.suit_cards[suit_name][-1]

        # Only trumps left
        if not suit_length:
            return player.trump_cards[-1]

        # Return smallest in longest suit
        # TODO we might not want to do this
        sorted_suit_length= {key: value for key, value in sorted(suit_length.items(), key=lambda item: item[1])}
        long_suit = list(sorted_suit_length)[0]
        return player.suit_cards[long_suit][-1]

    def partners_card_is_winner(self, trick: Trick) -> bool:
        """Return True if the card is the highest one out."""
        opponents_card = trick.cards[1]
        if opponents_card.suit == trick.suit:
            if opponents_card.value > trick.cards[0].value:
                return False

        player = self.player
        opponents_cards = player.opponents_cards[trick.suit.name]
        if not opponents_cards:
            return True

        if trick.cards[0].value > opponents_cards[0].value:
            return True
        return False
