from django.db import models


class Ability(models.Model):
    COST_TAP = 't'
    COST_CHOICES = (
        (COST_TAP, 'Tap'),
    )
    BENEFIT_M1G = 'm1g'
    BENEFIT_CHOICES = (
        (BENEFIT_M1G, 'Adds 1 generic mana'),
    )
    cost = models.CharField(max_length=3, choices=COST_CHOICES)
    benefit = models.CharField(max_length=3, choices=BENEFIT_CHOICES)


class Card(models.Model):
    KIND_LAND = 'l'
    KIND_CREATURE = 'c'
    KIND_CHOICES = (
        (KIND_LAND, 'Land'),
        (KIND_CREATURE, 'Creature'),
    )

    # all
    kind = models.CharField(max_length=1, choices=KIND_CHOICES, null=False)
    mana = models.IntegerField(null=False)
    abilities = models.ManyToManyField(Ability)

    # creature only
    power = models.IntegerField(null=True)
    toughness = models.IntegerField(null=True)

    def __str__(self):
        return '[{}] {}/{}'.format(self.mana, self.power, self.toughness)

    def is_land(self):
        return self.kind == self.KIND_LAND

    def is_creature(self):
        return self.kind == self.KIND_CREATURE

