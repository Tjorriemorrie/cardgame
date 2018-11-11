from django.shortcuts import render

from cards.models import Card


def index(request):
    cards = Card.objects.all()
    return render(request, 'cards/index.html', {'cards': cards})
