from django.contrib import admin

from cards.models import Card, Ability, CardCollection

admin.site.register(Card)
admin.site.register(Ability)
admin.site.register(CardCollection)
