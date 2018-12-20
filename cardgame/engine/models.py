from random import shuffle

from django.db import models

from cards.models import Card, Ability


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
    STATUS_ORDER = [
        STATUS_SETUP, STATUS_BUSY, STATUS_DONE
    ]

    PHASE_DRAW = 'draw'
    PHASE_MAIN = 'main'
    PHASE_DEBATE = 'debate'
    PHASE_UPKEEP = 'upkeep'
    PHASE_CHOICES = (
        (PHASE_DRAW, 'Draw'),
        (PHASE_MAIN, 'Main'),
        (PHASE_DEBATE, 'Debate'),
        (PHASE_UPKEEP, 'Upkeep'),
    )
    PHASE_ORDER = [
        PHASE_DRAW, PHASE_MAIN, PHASE_DEBATE, PHASE_UPKEEP
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SETUP, null=False)
    started_at = models.DateTimeField(auto_now_add=True, null=False)
    turn = models.IntegerField(default=1, null=False)
    round = models.IntegerField(default=1, null=False)
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default=PHASE_DRAW, null=False)
    last_combat_actor = models.IntegerField(null=True)

    def __str__(self):
        return 'id={} status={} round={} turn={} phase={} started_at={}'.format(
            self.pk, self.status, self.round, self.turn, self.phase, self.started_at)


class Player(models.Model):
    BELIEVE_START = 20

    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False)
    belief = models.IntegerField(default=BELIEVE_START)
    crowd = models.IntegerField(default=0, null=False)
    last_turn_person = models.IntegerField(default=0, null=False)

    # class Meta:
    #     unique('game', 'num')

    def deck(self):
        return self.gamecard_set.filter(slot=GameCard.SLOT_DECK).all()

    def deck_size(self):
        return self.gamecard_set.filter(slot=GameCard.SLOT_DECK).count()

    def hand(self):
        return self.gamecard_set.filter(slot=GameCard.SLOT_HAND).all()

    def hand_size(self):
        return self.gamecard_set.filter(slot=GameCard.SLOT_HAND).count()

    def table(self):
        return self.gamecard_set.filter(slot=GameCard.SLOT_TABLE).all()

    def table_size(self):
        return self.gamecard_set.filter(slot=GameCard.SLOT_TABLE).count()

    def available_support(self):
        on_table = self.gamecard_set.filter(
            slot=GameCard.SLOT_TABLE).filter(
            tapped=False).filter(
            card__kind=Card.KIND_PERSON).count()
        return self.crowd + on_table

    def get_any_untapped_persons(self):
        return self.gamecard_set.filter(
            slot=GameCard.SLOT_TABLE).filter(
            tapped=False).filter(
            card__kind=Card.KIND_PERSON).get()


class DeckCardGameManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(slot=GameCard.SLOT_DECK)


class GameCard(models.Model):
    SLOT_DECK = 'deck'
    SLOT_HAND = 'hand'
    SLOT_TABLE = 'table'
    SLOT_GRAVE = 'grave'
    SLOT_CHOICES = (
        (SLOT_DECK, 'Deck'),
        (SLOT_HAND, 'Hand'),
        (SLOT_TABLE, 'Table'),
        (SLOT_GRAVE, 'Graveyard'),
    )

    # deck = DeckCardGameManager()

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    pos = models.IntegerField(null=False)
    slot = models.CharField(max_length=10, choices=SLOT_CHOICES, null=False, blank=False)
    tapped = models.BooleanField(default=False, null=False)

    class Meta:
        ordering = ['pos']

    def is_affordable(self):
        cost = self.card.support
        if not cost:
            return True
        available = self.player.available_support()
        if available >= cost:
            return True
        return False


class Event(models.Model):
    CMD_STATUS = 'status'
    CMD_SHUFFLE = 'shuffle'
    CMD_DRAW = 'draw'
    CMD_PHASE = 'phase'
    CMD_PASS = 'pass'
    CMD_PLAY = 'play'
    CMD_COST = 'cost'
    CMD_BENEFIT = 'benefit'
    CMD_CHOICES = (
        (CMD_STATUS, 'Status'),
        (CMD_DRAW, 'Draw'),
        (CMD_SHUFFLE, 'Shuffle'),
        (CMD_PHASE, 'Phase'),
        (CMD_PLAY, 'Play'),
        (CMD_COST, 'Cost'),
        (CMD_BENEFIT, 'Benefit'),
    )

    # game data
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False)
    status = models.CharField(max_length=20, choices=Game.STATUS_CHOICES, null=False)
    turn = models.IntegerField(null=False)
    round = models.IntegerField(null=False)
    phase = models.CharField(max_length=20, choices=Game.PHASE_CHOICES, null=False)
    # player data
    health1 = models.IntegerField(null=False)
    health2 = models.IntegerField(null=False)
    deck1_size = models.IntegerField(null=False)
    deck2_size = models.IntegerField(null=False)
    hand1_size = models.IntegerField(null=False)
    hand2_size = models.IntegerField(null=False)
    grave1_size = models.IntegerField(null=False)
    grave2_size = models.IntegerField(null=False)
    # event data
    occurred_at = models.DateTimeField(auto_now_add=True, null=False)
    actor = models.ForeignKey(Player, on_delete=models.CASCADE, null=False)
    command = models.CharField(max_length=250, choices=CMD_CHOICES, null=False)
    gcard = models.ForeignKey(GameCard, on_delete=models.CASCADE, null=True)
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE, null=True)
    error = models.BooleanField(default=False, null=False)
    comment = models.CharField(max_length=250, null=True)






