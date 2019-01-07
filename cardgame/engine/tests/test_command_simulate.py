import pytest

from engine.management.commands.simulate import Command

pytestmark = pytest.mark.django_db


class TestSimulateCommand:

    def test_default(self):
        cmd = Command()
        cmd.handle()
