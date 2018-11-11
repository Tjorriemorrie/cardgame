from itertools import product

from django.core.management import BaseCommand

from cards.models import Card, Ability, CardCollection
from engine.models import Game, Player
from engine.services import DeckGenerator, Engine, NewGame


class Command(BaseCommand):
    help = 'Simulate a game'

    # def add_arguments(self, parser):
    #     parser.add_argument('max_power', type=int)

    def handle(self, *args, **options):
        self.stdout.write('Running simulation...')

        self.stdout.write('Getting game...')
        try:
            game = Game.objects.filter(status=Game.STATUS_BUSY).get()
            self.stdout.write('Existing unfinished game found')
        except Game.DoesNotExist:
            self.stdout.write('Fetching lands...')
            lands = Card.objects.filter(kind='l').all()
            self.stdout.write('Fetching creatures...')
            creatures = Card.objects.filter(kind='c').all()
            self.stdout.write('Generating deck 1...')
            deck1 = DeckGenerator.create(lands, creatures)
            self.stdout.write('Generating deck 2...')
            deck2 = DeckGenerator.create(lands, creatures)
            self.stdout.write('Creating players...')
            player1 = Player(deck=deck1)
            player1.save()
            player2 = Player(deck=deck2)
            player2.save()
            self.stdout.write('Creating new game...', ending='')
            game = NewGame.create(player1, player2)
            self.stdout.write('done')

        engine = Engine(game)
        # while not engine.is_finished():
        #     if engine.is_setup():
        #         engine.game_setup()


