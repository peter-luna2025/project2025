import pytest
from project import (
    create_deck,
    card_value,
    SetupRoutine
)

def test_create_deck_has_52_unique_cards():
    deck = create_deck()
    assert len(deck) == 52
    assert len(set(deck)) == 52


def test_card_value_comparison():
    # A♠ should beat K♦
    assert card_value("AS") > card_value("KD")

    # 10♥ should beat 9♣
    assert card_value("10H") > card_value("9C")

    # Same rank, suit decides (Spades > Hearts)
    assert card_value("7S") > card_value("7H")


def test_get_player_positions_two_players():
    game = SetupRoutine()  # no pygame needed
    game.players = ["Alice", "Bob"]

    positions = game.get_player_positions()

    assert len(positions) == 2
    assert isinstance(positions[0], tuple)
    assert isinstance(positions[1], tuple)
    assert positions[0] != positions[1]
