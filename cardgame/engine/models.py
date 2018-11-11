from django.db import models

from cards.models import CardCollection


class Player(models.Model):
    HEALTH_START = 20

    health = models.IntegerField(default=HEALTH_START)
    deck = models.ForeignKey(CardCollection, related_name='deck', on_delete=models.CASCADE)
    hand = models.ForeignKey(CardCollection, related_name='hand', on_delete=models.CASCADE)
    grave = models.ForeignKey(CardCollection, related_name='grave', on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        # check collections
        for col in ['deck', 'hand', 'grave']:
            if col not in kwargs:
                cardcol = CardCollection()
                cardcol.save()
                kwargs[col] = cardcol
        super().__init__(*args, **kwargs)

    def draw(self, n):
        for _ in range(n):
            card = self.deck.cards.pop()
            self.hand.cards.add(card)
        self.save()


class Game(models.Model):
    START_DRAW_NUMBER = 7
    STATUS_SETUP = 'setup'
    STATUS_BUSY = 'busy'
    STATUS_DONE = 'done'
    STATUS_CHOICES = (
        (STATUS_SETUP, 'Setup'),
        (STATUS_BUSY, 'Busy'),
        (STATUS_DONE, 'Done'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SETUP)
    started_at = models.DateTimeField(auto_now_add=True)
    turn = models.IntegerField(default=1)
    players = models.ManyToManyField(Player)

    def __str__(self):
        return 'id={} status={} turn={} started_at={}'.format(
            self.pk, self.status, self.turn, self.started_at)

    def is_status(self, value):
        return self.status == value

    # def draw(self, p, n):
    #     for _ in range(n):
    #         card = self.
















