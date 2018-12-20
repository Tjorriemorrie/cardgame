from itertools import product

from django.core.management import BaseCommand

from cards.models import Card, Ability


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

        # creating abilities
        # tap for mana
        tap_ability = Ability(cost='t', benefit='m1g')
        tap_ability.save()

        # creating land
        card = Card(kind='person', support=0)
        card.save()
        card.abilities.add(tap_ability)
        card.save()

        # creating creatures
        for power, endurance in product(range(0, 6), range(1, 6)):
            card = Card(kind='opinion', support=1, power=power, endurance=endurance)
            card.save()

        self.stdout.write('Done')
