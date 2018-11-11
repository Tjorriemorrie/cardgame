from random import shuffle

from django.db import models


class Ability(models.Model):
    COST_CHOICES = (
        ('t', 'Tap'),
    )
    BENEFIT_CHOICES = (
        ('m1g', 'Adds 1 generic mana'),
    )
    cost = models.CharField(max_length=3, choices=COST_CHOICES)
    benefit = models.CharField(max_length=3, choices=BENEFIT_CHOICES)


class Card(models.Model):
    KIND_CHOICES = (
        ('l', 'Land'),
        ('c', 'Creature'),
    )

    # all
    kind = models.CharField(max_length=1, choices=KIND_CHOICES)
    mana = models.IntegerField()
    abilities = models.ManyToManyField(Ability)

    # creature only
    power = models.IntegerField(null=True)
    toughness = models.IntegerField(null=True)

    def __str__(self):
        return '[{}] {}/{}'.format(self.mana, self.power, self.toughness)

    def is_land(self):
        return self.kind == 'l'

    def is_creature(self):
        return self.kind == 'c'


class CardCollection(models.Model):
    pass

    # def shuffle(self):
    #     shuffle(self.cards)


class CardPosition(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    col = models.ForeignKey(CardCollection, related_name='cpos', on_delete=models.CASCADE)
    pos = models.IntegerField()

    class Meta:
        ordering = ['pos']






















