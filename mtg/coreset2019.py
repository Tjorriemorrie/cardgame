url = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?action=advanced&output=standard&sort=cn+&set=+[%22Core%20Set%202019%22]'


COLORS = {
    'w': 'white',
    'b': 'blue',
    'g': 'green',
    'r': 'red',
    'k': 'black',
    'c': 'colorless',
    'm': 'multicolored',
}


class Card:

    def __init__(self, name, rules_text, color, type_, subtype, cmc, power,
                 toughness, mana_cost, rarity):
        self.name = name
        self.rules_text = rules_text
        self.color = color
        self.type_ = type_
        self.subtype = subtype
        self.cmc = cmc
        self.power = power
        self.toughness = toughness
        self.mana_cost = mana_cost
        self.rarity = rarity


cards = [
    Card('Aegis of the Heavens', 'Target creature gets +1/+7 until end of turn.', 'w', 'Instant',
         '', 2, '', '', '1p', 'uncommon'),
    Card('Aethershield Artificer', 'At the beginning of combat on your turn, target artifact '
                                   'creature you control gets +2/+2 and gains indestructible '
                                   'until end of turn. (Damage and effects that say "destroy" dont destroy it.',
         'w', 'creature', 'dwarf artificer', 4, 3, 3, '3p', 'uncommon'),
    Card('Ajani, Adversary of tyrants', '+1: Put a +1/+1 counter on each of up to two target creatures.'
                                        '−2: Return target creature card with converted mana cost 2 or less from your graveyard to the battlefield.'
                                        '−7: You get an emblem with "At the beginning of your end step, create three 1/1 white Cat creature tokens with lifelink."',
         'w', 'legendary planeswalker', 'ajani', 4, '', 4, '2pp', 'mythic rare'),
    Card('')
]

















































white:
instants:
 - Target creature gets +1/+7 until end of turn.

