from itertools import product
import sqlite3


# class Card:
#
#     def __init__(self, name, rules_text, color, type_, subtype, cmc, power,
#                  toughness, mana_cost, rarity):
#         self.name = name
#         self.rules_text = rules_text
#         self.color = color
#         self.type_ = type_
#         self.subtype = subtype
#         self.cmc = cmc
#         self.power = power
#         self.toughness = toughness
#         self.mana_cost = mana_cost
#         self.rarity = rarity


sqlite_file = 'db.sqlite'
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()


class Card:

    def __init__(self, cost):
        self.cost = cost


class Creature(Card):

    def __init__(self, power, toughness, *args, **kwargs):
        super(Creature, self).__init__(*args, **kwargs)
        self.power = power
        self.toughness = toughness


class Deck:

    def __init__(self):
        self.cards = []

    def take_top_card(self):
        # last item is top
        card = self.cards.pop()
        return card


class Player:

    def __init__(self, deck):
        self.deck = deck
        self.hand = []

    def draw(self, size):
        for i in range(size):
            card = self.deck.take_top_card()
            self.hand.append(card)


class Engine:

    STARTING_HAND_SIZE = 7

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.player1.draw(7)
        self.player2.draw(7)
        self.turn = 1


def run_simulation():
    deck1 = Deck()
    player1 = Player(deck1)
    deck2 = Deck()
    player2 = Player(deck2)
    engine = Engine(player1, player2)


def generate_cards():
    setup_db()

    res = list(product(range(0, 6), range(1, 6)))
    print(len(res))
    print(res)


def setup_db():
    """
    INTEGER: A signed integer up to 8 bytes depending on the magnitude of the value.
    REAL: An 8-byte floating point value.
    TEXT: A text string, typically UTF-8 encoded (depending on the database encoding).
    BLOB: A blob of data (binary large object) for storing binary data.
    NULL: A NULL value, represents missing data or an empty cell.
    """
    c.execute("""
    CREATE TABLE creature (
        id INTEGER PRIMARY KEY,
        power INTEGER NOT NULL,
        toughness INTEGER NOT NULL,
        UNIQUE (power, toughness)
    )
    """)
    conn.commit()


if __name__ == '__main__':
    generate_cards()
    # run_simulation()
