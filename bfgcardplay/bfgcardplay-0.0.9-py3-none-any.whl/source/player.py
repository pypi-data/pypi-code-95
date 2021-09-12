"""Common functionality for cardplay."""

import logging
import os

from termcolor import colored

logging_level = logging.DEBUG
logging_level = logging.WARNING

logging.basicConfig(level=logging_level)

from typing import List, Dict, Tuple
import random

from bridgeobjects import Suit, Card, SEATS, SUITS, CARD_NAMES
from bfgsupport import Board, Hand, Trick

import bfgcardplay.source.global_variables as global_vars

global_vars.initialize()


class Player():
    """Object to represent the player: their hand and memory."""
    def __init__(self, board):
        self.board = board

        # Seats and roles
        self.seat = self._get_seat()
        self.seat_index = SEATS.index(self.seat)
        self.partner_seat = self.get_partners_seat(self.seat)
        self.declarer = board.contract.declarer
        self.declarer_index = SEATS.index(self.declarer)
        self.is_declarer = self.seat == self.declarer
        self.dummy_index = (self.declarer_index + 2) % 4
        self.dummy = SEATS[self.dummy_index]
        self.is_dummy = self.seat == self.dummy
        self.is_defender = not (self.is_declarer or self.is_dummy)

        # Hands suits and cards
        self.cards = board.hands[self.seat].unplayed_cards
        self.suit_cards = self.get_cards_by_suit(self.cards)
        self.longest_suit = self._longest_suit()
        self.trump_suit = self._get_trump_suit()
        self.trump_cards = self._cards_for_trump_suit()
        self.our_cards: Dict[str, List[Card]] = self._get_partnership_cards(self.seat)
        opponents_seat = SEATS[(self.seat_index + 1) % 4]
        self.opponents_cards: Dict[str, List[Card]] = self._get_partnership_cards(opponents_seat)
        self.opponents_trumps = self._opponents_trumps()
        self.declarers_hand = board.hands[self.declarer]
        self.dummys_hand = board.hands[self.dummy]

        # Declarer and Dummy
        # These card properties must be assigned in this order
        self.declarers_cards = board.hands[self.declarer].unplayed_cards
        self.declarers_suit_cards = self.get_cards_by_suit(self.declarers_cards)
        self.dummys_cards = board.hands[self.dummy].unplayed_cards
        self.dummys_suit_cards: Dict[str, List[Card]] = self.get_cards_by_suit(self.dummys_cards)
        self.dummy_suit_strength = self.get_suit_strength(self.dummys_cards)
        self.dummy_suit_tenaces = self._get_tenaces(self.dummys_suit_cards)

        # Defenders
        if self.is_defender:
            self.dummy_on_left = ((self.seat_index - self.dummy_index) % 4) == 3
            self.dummy_on_right = not self.dummy_on_left
        else:
            self.dummy_on_left = None
            self.dummy_on_right = None

        # Partners
        self.partners_cards = []
        if self.is_declarer:
            self.partners_cards = self.dummys_cards
        elif self.is_dummy:
            self.partners_cards = self.declarers_cards
        self.partners_suit_cards = self.get_cards_by_suit(self.partners_cards)

        # Information
        self.trick_number = len(board.tricks) + 1

    @staticmethod
    def get_partners_seat(seat: str) -> str:
        """Return partner's seat."""
        seat_index = SEATS.index(seat)
        partners_index = (seat_index + 2) % 4
        partners_seat = SEATS[partners_index]
        return partners_seat

    def _get_seat(self) -> str:
        """Return the current user's seat."""
        trick = self.board.tricks[-1]
        leader = trick.leader
        leader_index = SEATS.index(leader)
        seat_index = (leader_index + len(trick.cards)) % 4
        seat = SEATS[seat_index]
        return seat

    def _longest_suit(self) -> Suit:
        """Return the suit with most cards."""
        max_length = 0
        suits = []
        for suit in SUITS:
            if len(self.suit_cards[suit]) > max_length:
                max_length = len(self.suit_cards[suit])
        for suit in SUITS:
            if len(self.suit_cards[suit]) == max_length:
                suits.append(suit)
        return Suit(random.choice(suits))

    def cards_for_trick_suit(self, trick: Trick) -> List[Card]:
        """Return a list of cards in the trick suit."""
        suit = trick.start_suit
        return self.suit_cards[suit.name]

    def _cards_for_trump_suit(self) -> List[Card]:
        """Return a list of cards in the trump suit."""
        if self.trump_suit:
            return self.suit_cards[self.trump_suit.name]
        return []

    def _opponents_trumps(self) -> List[Card]:
        """Return a list of opponents' trumps."""
        if self.trump_suit:
            return self.opponents_cards[self.trump_suit.name]
        return []

    @staticmethod
    def other_suit_for_signals(suit: Suit) -> str:
        """Return the other suit for signalling."""
        if suit.name == 'S':
            other_suit = 'C'
        elif suit.name == 'C':
            other_suit = 'S'
        elif suit.name == 'H':
            other_suit = 'D'
        elif suit.name == 'D':
            other_suit = 'H'
        return other_suit

    def _get_trump_suit(self) -> Suit:
        """Return the trump suit for the board (if any)."""
        if self.board.contract.is_nt:
            return None
        return self.board.contract.denomination

    def get_cards_by_suit(self, cards: List[Card]) -> Dict[str, List[Card]]:
        """Return a dict of suit cards keyed on suit name."""
        suit_cards = {suit_name: [] for suit_name, suit in SUITS.items()}
        for card in cards:
            for suit, items in suit_cards.items():
                if card.suit.name == suit:
                    suit_cards[suit].append(card)
        return suit_cards

    @staticmethod
    def get_suit_strength(cards: List[Card]) -> Dict[str, int]:
        """Return a dict of suit high card points keyed on suit name."""
        suit_points = {suit_name: 0 for suit_name, suit in SUITS.items()}
        for card in cards:
            suit_points[card.suit.name] += card.high_card_points
        return suit_points

    def _get_tenaces(self, cards: Dict[str, Card]) -> Dict[str, Card]:
        """Return a dict of suit tenaces keyed on suit name."""
        suit_tenaces = {suit_name: None for suit_name, suit in SUITS.items()}
        for suit, cards in cards.items():
            for index, card in enumerate(cards[:-2]):
                if index < len(cards) - 1:
                    if ((card.is_honour and card.value == cards[index+1].value + 2) or
                        (card.is_honour and card.value == cards[index+1].value + 3)):
                        suit_tenaces[suit] = card
        return suit_tenaces

    def card_has_been_played(self, card: Card) -> bool:
        """Return True if the card has already been played."""
        for seat in SEATS:
            hand = self.board.hands[seat]
            if card in hand.unplayed_cards:
                return False
        return True

    def _get_partnership_cards(self, seat: str) -> Dict[str, List[Card]]:
        """Return a dict containing the partnership's unplayed cards."""
        partnership_cards =  {suit_name: [] for suit_name, suit in SUITS.items()}
        partners_seat = Player.get_partners_seat(seat)
        seats = [seat, partners_seat]
        for player_seat in seats:
            for suit_name, suit in SUITS.items():
                unplayed_cards = self.unplayed_cards_by_suit(suit, player_seat)
                partnership_cards[suit.name] += unplayed_cards
        for suit_name, suit in SUITS.items():
            sorted_cards = self._sort_cards(partnership_cards[suit.name])
            partnership_cards[suit.name] = sorted_cards
        return partnership_cards

    def unplayed_cards_by_suit(self, suit: Suit, seat: str) -> List[Card]:
        """Return a tuple containing declarers and opponents unplayed cards in a suit."""
        hand = self.board.hands[seat]
        cards = hand.cards_by_suit[suit.name]
        unplayed_cards = [card for card in cards if card in hand.unplayed_cards]
        return unplayed_cards

    def total_unplayed_cards_by_suit(self, suit: Suit) -> Tuple[List[Card], List[Card]]:
        """Return a tuple containing declarers and opponents unplayed cards in a suit."""
        declarers_cards = []
        defenders_cards = []
        for seat in SEATS:
            unplayed_cards = self.unplayed_cards_by_suit(suit, seat)
            for card in unplayed_cards:
                if seat in [self.dummy, self.declarer]:
                    declarers_cards.append(card)
                else:
                    defenders_cards.append(card)
        return (declarers_cards, defenders_cards)

    @staticmethod
    def _sort_cards(cards: List[Card]) -> List[Card]:
        """Return a sorted list of cards."""
        return sorted(cards, reverse=True)

    def get_long_hand(self, first_hand: Hand, second_hand: Hand, suit: Suit) -> Tuple[Hand, Hand]:
        """Return a tuple of long_hand and sort hand."""
        first_hand_unplayed_cards = first_hand.unplayed_cards
        first_hand_cards = self.get_cards_by_suit(first_hand_unplayed_cards)
        second_hand_unplayed_cards = second_hand.unplayed_cards
        second_hand_cards = self.get_cards_by_suit(second_hand_unplayed_cards)
        if len(second_hand_cards[suit.name]) > len(first_hand_cards[suit.name]):
            long_hand = second_hand_cards
            short_hand = first_hand_cards
        else:
            long_hand = first_hand_cards
            short_hand = second_hand_cards
        return(long_hand, short_hand)

    def get_long_hand_seat(self, first_seat: str, second_seat: str, suit: Suit) -> str:
        """Return a tuple of long_hand and sort hand."""
        first_hand_unplayed_cards = self.board.hands[first_seat].unplayed_cards
        first_hand_cards = self.get_cards_by_suit(first_hand_unplayed_cards)
        second_hand_unplayed_cards = self.board.hands[second_seat].unplayed_cards
        second_hand_cards = self.get_cards_by_suit(second_hand_unplayed_cards)
        if len(second_hand_cards[suit.name]) > len(first_hand_cards[suit.name]):
            return second_seat
        return first_seat

    def holds_all_winners_in_suit(self, suit: Suit) -> bool:
        """Return True if the partnership holds all the winners in a suit."""
        our_cards = self.our_cards[suit.name]
        opponents_cards = self.opponents_cards[suit.name]
        if our_cards and not opponents_cards:
            return True
        elif our_cards and opponents_cards:
            if our_cards[-1].value > opponents_cards[0].value:
                return True
            else:
                if our_cards[0].value > opponents_cards[0].value:
                    sequence = [our_cards[0]]
                    for index, card in enumerate(our_cards[:-1]):
                        if card.value == our_cards[index+1].value + 1:
                            sequence.append(our_cards[index+1])
                    if len(sequence) > len(opponents_cards):
                        return True
        return False

    def dummy_holds_adjacent_card(self, card: Card) -> bool:
        """Return True if the hand contains the adjacent card."""
        cards = self.dummys_suit_cards[card.suit.name]
        for other_card in cards:
            if other_card.value == card.value + 1 or other_card.value == card.value - 1:
                return True
        return False

    def partnership_long_suits(self, ignore_trumps=True):
        """Return a list of the longest partnership suits."""
        long_suits = []
        max_length = 0
        for suit in SUITS:
            if ignore_trumps and suit != self.trump_suit.name:
                length = len(self.our_cards[suit])
                if length >= max_length:
                    max_length = length

        for suit in SUITS:
            if suit != self.trump_suit.name:
                length = len(self.our_cards[suit])
                if length == max_length:
                    long_suits.append(suit)
        return long_suits

    def can_lead_toward_tenace(self, long_suit: str) -> bool:
        """Return True if we can lead to higher honour in partner's hand."""
        if self.partners_suit_cards[long_suit] and self.suit_cards[long_suit]:
            partners_best_card = self.partners_suit_cards[long_suit][0]
            my_best_card = self.suit_cards[long_suit][0]
            if partners_best_card.is_honour:
                if partners_best_card.value > my_best_card.value + 1:
                    return True
        return False

