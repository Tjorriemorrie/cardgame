import pytest

from cards.services import create_standard_cards

pytestmark = pytest.mark.django_db


def test_create_standard_cards():
    create_standard_cards()
