"""The manager supervises play and holds persistant data. It is created in global.py."""
from typing import List, Dict, Union, Tuple

from bridgeobjects import SEATS, SUITS, Card, Hand, Suit, RANKS
from bfgsupport import Board

DECLARER_STRATEGY = {
    0: 'Draw trumps and establish long suit',
}

ranks = [rank for rank in RANKS]
ranks.reverse()
RANKS = ranks[:-1]

class Manager():
    def __init__(self):
        # self.board = board
        self._board = None
        self.threats = None

    @property
    def board(self):
        """Return the current Board."""
        return self._board

    @board.setter
    def board(self, value):
        """Set the value of the current board"""
        self._board = value

    def unplayed_cards(self) -> Dict[str, Card]:
        """Return a dict of suits with a list of unplayed cards in descending order."""
        unplayed = {suit: [] for suit in SUITS}
        for seat in SEATS:
            for card in self.board.hands[seat]:
                unplayed[card.suit.name].append(card)

        for suit in SUITS:
            sorted_cards = []
            for rank in RANKS:
                if Card(rank, suit) in unplayed[suit]:
                    sorted_cards.append(card)
            unplayed[suit] = [card for card in sorted_cards]
        return unplayed


    def set_declarer_strategy(self):
        """Set the declarers initial strategy."""
        board = self.board
        declarer = self.board.contract.declarer
        declarer_index = SEATS.index(declarer)
        dummy_index = (declarer_index + 2) % 4
        dummy = SEATS[dummy_index]
        declarers_hand = board.hands[declarer]
        dummys_hand = board.hands[dummy]
        if board.contract.is_nt:
            pass
        else:
            trump_suit = board.contract.denomination.name
            (long_hand, short_hand) = Manager.get_long_hand(declarers_hand, dummys_hand, trump_suit)
            threats = self._get_declarers_threats(long_hand, short_hand, trump_suit)
            shortages_in_short_hand = self._get_shortages_in_short_hand(long_hand, short_hand, trump_suit)
            trumps_remaining_after_drawing = 0
            # for suit, cards in threats.items():

            print(f'{shortages_in_short_hand=}')

    @staticmethod
    def _get_declarers_threats(long_hand: Hand, short_hand: Hand, trump_suit: Suit) -> Dict[str, Card]:
        """Return a dict of cards by suit that threaten declarers cards."""
        losers = {suit: [] for suit in SUITS}

        for suit in SUITS:
            long_cards = long_hand.cards_by_suit[suit]
            short_cards = short_hand.cards_by_suit[suit]
            cards = long_cards + short_cards
            missing = 13 - len(cards)
            winners = 0
            skip_card = False
            for index, rank in enumerate(RANKS):
                ranking_card = Card(rank, suit)
                if ranking_card in cards:
                    if not skip_card:
                        winners += 1
                    skip_card = False
                else:
                    losers[suit].append(ranking_card)
                    # skip card means that the next card in the suit is assumed to have been beaten
                    skip_card = True

                # No more cards to lose
                if winners > missing:
                    break

                #losers only in long hand
                if index + 1 >= len(long_cards):
                    break
        return losers

    @staticmethod
    def _get_shortages_in_short_hand(long_hand: Hand, short_hand: Hand, trump_suit: Suit) -> Dict[str, Card]:
        """Return a dict of cards by suit that represent a shortage in the short hand."""
        shortages = {suit: 0 for suit in SUITS}
        for suit in SUITS:
            if not suit == trump_suit:
                long_hand_cards = long_hand.cards_by_suit[suit]
                short_hand_cards = short_hand.cards_by_suit[suit]
                if len(long_hand_cards) > len(short_hand_cards):
                    shortages[suit] = len(long_hand_cards)-len(short_hand_cards)
        return shortages

    @staticmethod
    def get_long_hand(declarers_hand: Hand, dummys_hand: Hand, trump_suit: Suit) -> Tuple[Hand, Hand]:
        """Return a tuple of long_hand and sort hand."""
        declarers_trumps = declarers_hand.cards_by_suit[trump_suit]
        dummys_trumps = dummys_hand.cards_by_suit[trump_suit]
        if len(dummys_trumps) > len(declarers_trumps):
            long_hand = dummys_hand
            short_hand = declarers_hand
        else:
            long_hand = declarers_hand
            short_hand = dummys_hand
        return(long_hand, short_hand)