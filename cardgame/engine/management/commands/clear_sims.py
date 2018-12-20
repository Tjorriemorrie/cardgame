from django.core.management import BaseCommand

from engine.models import Game


class Command(BaseCommand):
    help = 'Clear simulate data in db'

    # def add_arguments(self, parser):
    #     parser.add_argument('max_power', type=int)

    def handle(self, *args, **options):
        self.stdout.write('Clearing all data...')
        Game.objects.all().delete()
        self.stdout.write('Done')
