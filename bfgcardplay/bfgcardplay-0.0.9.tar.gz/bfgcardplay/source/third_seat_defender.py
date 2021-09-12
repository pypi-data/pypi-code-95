"""Third seat card play for defender."""

import logging
log = logging.getLogger(__name__)

from typing import List, Union, Tuple

from bridgeobjects import SUITS, Card, Denomination
from bfgsupport import Board, Trick
from .player import Player
from .third_seat import ThirdSeat

class ThirdSeatDefender(ThirdSeat):
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

            # win trick if possible
            winning_card = self._winning_card(player, trick)
            if winning_card:
                return winning_card

            # signal attitude
            if cards[0].is_honour:
                for card in cards[1:]:
                    if not card.is_honour:
                        return card
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
                    if (not self._seat_dominates_left_hand_dummy_tenace(player, card) and
                            not self._ace_is_deprecated(trick, card)):
                        return card

        # No cards in trick suit, look for trump winner
        elif player.trump_cards:
            print('third player trumps')
            for card in player.trump_cards[::-1]:
                if card.value + 13 > value_0 + 1 and card.value + 13 > value_1:
                    return card
        return None
    @staticmethod
    def _seat_dominates_left_hand_dummy_tenace(player: Player, card: Card) -> bool:
        """Return True if hand dominated dummies tenace in that suit."""
        if player.dummy_on_left:
            return False
        tenace = player.dummy_suit_tenaces[card.suit.name]
        if tenace:
            if card.value > tenace.value:
                return True
        return False

    def _select_card_if_void(self, player: Player, trick: Trick) -> Card:
        """Return card if cannot follow suit."""
        # Trump if appropriate
        (value_0, value_1) = self._trick_card_values(trick, player.trump_suit)
        if player.trump_suit:
            if player.trump_cards:
                if player.is_defender:
                    if (value_1 > value_0 or
                            trick.cards[0].value <= 6 or
                            True):
                        pass
                else:
                    over_trump_partner = _overtrump_partner(player, trick)
                    if over_trump_partner:
                        return player.trump_cards[-1]

        # Signal suit preference first time it is led."""
        signal_card = self._signal_on_first_lead(player, trick)
        if signal_card:
            return signal_card

        suit = self._best_suit(player)
        other_suit = player.other_suit_for_signals(suit)
        if other_suit != player.trump_suit:
            other_suit_cards = player.suit_cards[other_suit]
            if other_suit_cards and not other_suit_cards[-1].is_honour:
                return other_suit_cards[-1]

        long_suit_cards = 0
        selected_card = None
        for suit in SUITS:
            if suit != player.trump_suit:
                cards = player.suit_cards[suit]
                if len(cards) > long_suit_cards and not cards[-1].is_honour:
                    selected_card = cards[-1]
        if selected_card:
            return selected_card


        for suit_name in SUITS:
            if suit_name != suit.name and suit_name != other_suit:
                final_suit_cards = player.suit_cards[suit_name]
                if final_suit_cards:
                    return final_suit_cards[-1]

        print(f'{player.suit_cards[suit.name][0]=}')
        return player.suit_cards[suit.name][0]

    def _signal_on_first_lead(self, player: Player, trick: Trick) -> Union[Card, None]:
        """Return a card if it is first time that partner led it."""
        suits_already_signed = []
        for board_trick in player.board.tricks:
            if board_trick.leader == player.partner_seat and board_trick != trick:
                suits_already_signed.append(board_trick.start_suit)

        if trick.start_suit not in suits_already_signed:
            suit = self._best_suit(player)
            suit_cards = player.suit_cards[suit.name]
            for card in suit_cards:
                if not card.is_honour:
                    return card
        return None

