from unittest.mock import patch

import pytest

from cards.management.commands.generate_cards import Command

pytestmark = pytest.mark.django_db


@patch('cards.management.commands.generate_cards.create_standard_cards')
def test_handle(*args):
    cmd = Command()
    cmd.handle()
