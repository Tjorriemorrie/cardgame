from django.core.management import BaseCommand

from django.core.management import BaseCommand

from cards.models import Card
from engine.models import Game
from engine.services import create_random_game, Engine, Bot


class Command(BaseCommand):
    help = 'Simulate a game'

    # def add_arguments(self, parser):
    #     parser.add_argument('max_power', type=int)

    def handle(self, *args, **options):
        self.stdout.write('Running simulation...')

        self.stdout.write('Getting game...')
        try:
            game = Game.objects.exclude(status=Game.STATUS_DONE).get()
            self.stdout.write('Existing unfinished game found')
        except Game.DoesNotExist:
            self.stdout.write('Fetching lands...')
            lands = Card.objects.filter(kind='l').all()
            self.stdout.write('Fetching creatures...')
            creatures = Card.objects.filter(kind='c').all()
            self.stdout.write('Creating new game...', ending='')
            game = create_random_game(lands, creatures)
            self.stdout.write('done')
        except Game.MultipleObjectsReturned:
            game = Game.objects.exclude(status=Game.STATUS_DONE).first()
            self.stdout.write('First existing unfinished game retrieved')

        self.stdout.write('Creating engine...')
        engine = Engine(game)
        while not engine.is_finished():
            if engine.is_setup():
                self.stdout.write('Setting up game...')
                engine.setup_game()
            bot = Bot(game)
            bot.analyze()
            break

        self.stdout.write('Script ended')

