import pytest

from cards.models import Ability, Card

pytestmark = pytest.mark.django_db


class TestAbilityModel:

    def test_save(self):
        ability = Ability.objects.create(
            cost=Ability.COST_TAP, benefit=Ability.BENEFIT_M1G)
        assert ability.cost == 't'
        assert ability.benefit == 'm1g'


class TestCardModel:

    def test_save_person(self):
        card = Card.objects.create(
            kind=Card.KIND_PERSON, support=1)
        assert card.kind == 'person'
        assert card.support == 1

    def test_save_opinion(self):
        card = Card.objects.create(
            kind=Card.KIND_OPINION, support=1, power=1, endurance=1)
        assert card.kind == 'opinion'
        assert card.support == 1
        assert card.power == 1
        assert card.endurance == 1
