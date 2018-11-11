from random import choice, shuffle

from cards.models import CardCollection, CardPosition
from engine.models import Game


class Engine:

    def __init__(self, game):
        self.game = game

    def is_setup(self):
        return self.game.is_status(Game.STATUS_SETUP)

    def is_finished(self):
        return self.game.is_status(Game.STATUS_DONE)

    def game_setup(self):
        for player in self.game.players:
            player.deck.shuffle()
            player.draw(Game.START_DRAW_NUMBER)


class DeckGenerator:

    @classmethod
    def create(cls, lands, creatures):
        deck = CardCollection()
        deck.save()

        # add 20 lands
        n = 20
        for l in range(n):
            random_land = choice(lands)
            cpos = CardPosition(card=random_land, col=deck, pos=l + 1)
            cpos.save()

        # add 10 creatures x4
        for c in range(10):
            random_creature = choice(creatures)
            for i in range(4):
                n += 1
                cpos = CardPosition(card=random_creature, col=deck, pos=n)
                cpos.save()

        return deck


class NewGame:

    @classmethod
    def create(cls, player1, player2):
        game = Game()
        game.save()

        game.players.add(player1)
        game.players.add(player2)
        game.save()

        return game



















