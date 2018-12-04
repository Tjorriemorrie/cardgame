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
    KIND_PERSON = 'person'  # land
    KIND_OPINION = 'opinion'  # creature
    KIND_PAPER = 'paper'  # enchantment
    KIND_EVIDENCE = 'evidence'  # enchant creature
    KIND_CHOICES = (
        (KIND_PERSON, 'Person'),
        (KIND_OPINION, 'Opinion'),
        (KIND_PAPER, 'Paper'),
        (KIND_EVIDENCE, 'Evidence'),
    )

    # all
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, null=False)
    support = models.IntegerField(null=False)
    abilities = models.ManyToManyField(Ability)

    # creature only
    power = models.IntegerField(null=True)
    endurance = models.IntegerField(null=True)

    def __str__(self):
        return '[{}] {}/{}'.format(self.support, self.power, self.endurance)

    def is_person(self):
        return self.kind == self.KIND_PERSON

    def is_story(self):
        return self.kind == self.KIND_STORY

