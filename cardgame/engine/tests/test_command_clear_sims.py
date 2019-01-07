import pytest

from engine.management.commands.clear_sims import Command

pytestmark = pytest.mark.django_db


class TestClearSimsCommand:

    def test_default(self):
        cmd = Command()
        cmd.handle()
