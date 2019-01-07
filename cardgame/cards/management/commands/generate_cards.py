from django.core.management import BaseCommand

from cards.models import Ability, Card
from cards.services import create_standard_cards


class Command(BaseCommand):
    help = 'Generates the cards'

    # def add_arguments(self, parser):
    #     parser.add_argument('max_power', type=int)

    def handle(self, *args, **options):
        self.stdout.write('Deleting all existing cards...')
        Card.objects.all().delete()
        Ability.objects.all().delete()
        self.stdout.write('Done')

        self.stdout.write('Generating cards...')

        create_standard_cards()

        self.stdout.write('Done')
