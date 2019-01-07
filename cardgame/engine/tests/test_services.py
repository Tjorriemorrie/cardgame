from copy import deepcopy
from random import choice
from unittest.mock import MagicMock, patch

import pytest

from cards.models import Card
from cards.services import create_standard_cards
from engine.models import Game, GameCard
from engine.services import create_random_deck, create_random_game, GameAdaptor, Engine, Bot

pytestmark = pytest.mark.django_db


@pytest.fixture
def cards_created():
    create_standard_cards()


@pytest.fixture
def persons_and_opinions(cards_created):
    persons = Card.objects.filter(kind=Card.KIND_PERSON).all()
    opinions = Card.objects.filter(kind=Card.KIND_OPINION).all()
    return persons, opinions


@patch('engine.services.create_random_deck')
def test_create_random_game(*args):
    persons = Card.objects.filter(kind=Card.KIND_PERSON).all()
    opinions = Card.objects.filter(kind=Card.KIND_OPINION).all()
    res = create_random_game(persons, opinions)
    assert isinstance(res, Game)


def test_create_random_deck(persons_and_opinions):
    persons, opinions = persons_and_opinions
    game = Game.objects.create()
    player = game.player_set.create()
    res = create_random_deck(player, persons, opinions)
    assert len(res) == 60


@pytest.fixture
def example_game(persons_and_opinions):
    # game
    game = Game.objects.create()
    # players
    player1 = game.player_set.create()
    player2 = game.player_set.create()
    players = [player1, player2]
    # decks
    persons, opinions = persons_and_opinions
    for player in players:
        # add 20 persons
        for p in range(20):
            random_person = choice(persons)
            GameCard.objects.create(player=player, card=random_person, pos=(p + 1),
                                    slot=GameCard.SLOT_DECK)
        # add 40 opinions
        for o in range(40):
            random_opinion = choice(opinions)
            n = 20 + o
            GameCard.objects.create(player=player, card=random_opinion, pos=n,
                                    slot=GameCard.SLOT_DECK)
    # done
    return game


@pytest.fixture
def set_up_engine(example_game):
    engine = Engine(example_game)
    engine.setup_game()
    return engine


class TestGameAdaptor:

    def test_to_dict(self, example_game):
        adaptor = GameAdaptor()
        adaptor.to_dict(example_game)
        assert adaptor.is_status_setup()


class TestEngine:

    def test_setup_game(self, example_game):
        engine = Engine(example_game)
        assert engine.is_status_setup()
        engine.setup_game()
        assert engine.is_status_busy()
        assert engine.is_phase_draw()
        for player in engine.data['players']:
            assert len(player['hand']) == Game.START_DRAW_NUMBER
            assert len(player['deck']) == 60 - Game.START_DRAW_NUMBER

    def test_shuffle_deck(self, example_game):
        engine = Engine(example_game)
        original_deck = deepcopy(engine.data['players'][0]['deck'])
        engine.shuffle_deck(engine.data['players'][0])
        assert original_deck != engine.data['players'][0]['deck']





class TestBot:

    def test_analyze(self, set_up_engine):
        bot = Bot(set_up_engine)
        best_value, best_moves = bot.analyze()
        assert best_value > 0
        assert len(best_moves)
