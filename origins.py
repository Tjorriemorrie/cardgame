url = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?sort=cn+&set=[%22Magic%20Origins%22]'

class Card:

    def __init__(self, color=None, name=None, cost=None, klass=None, power=None, toughness=None,
                 ability=None, rarity=None):
        self.color = color
        self.name = name
        self.cost = cost
        self.klass = klass
        self.power = power
        self.toughness = toughness
        self.ability = ability
        self.rarity = rarity


cards = [
    Card('w', 'Akroan Jailer', 'p', 'creature - human soldier', 1, 1, '2p, t: Tap target creature', 'common'),
    Card('w', 'Ampryn Tactician', '2pp', 'creature - human soldier', 3, 3, 'When Ampryn Tactician enters the battlefield, creatures you control get +1/+1 until end of turn.', 'common'),

]
