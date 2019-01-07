from itertools import product

from cards.models import Ability, Card


def create_standard_cards():
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
