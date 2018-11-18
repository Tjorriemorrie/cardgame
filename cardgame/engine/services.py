from random import choice, shuffle

from treelib import Tree

from cards.models import Ability
from engine.models import Game, GameCard, Event


class Engine:

    def __init__(self, game, persist=True):
        self.game = game
        self.persist = persist

    @property
    def active_player(self):
        players = self.game.player_set.all()
        return players[self.game.turn - 1]

    def is_setup(self):
        return self.game.is_status(Game.STATUS_SETUP)

    def is_finished(self):
        return self.game.is_status(Game.STATUS_DONE)

    def setup_game(self):
        for player in self.game.player_set.all():
            self.shuffle_deck(player)
            self.draw(player, Game.START_DRAW_NUMBER)
        self.next_status()
        self.next_phase()

    def next_status(self):
        i = Game.STATUS_ORDER.index(self.game.status)
        new_status = Game.STATUS_ORDER[i + 1]
        self.game.status = new_status
        self.log(self.active_player, Event.CMD_STATUS)
        self.game.save()

    def next_phase(self):
        i = Game.PHASE_ORDER.index(self.game.phase)
        try:
            new_phase = Game.PHASE_ORDER[i + 1]
        except IndexError:
            new_phase = Game.PHASE_ORDER[0]
        self.game.phase = new_phase
        self.log(self.active_player, Event.CMD_PHASE)
        self.game.save()

    def shuffle_deck(self, player):
        gcards = player.gamecard_set.filter(slot__exact=GameCard.SLOT_DECK).all()
        new_positions = list(range(len(gcards)))
        shuffle(new_positions)
        for new_pos, gcard in zip(new_positions, gcards):
            gcard.pos = new_pos + 1
            gcard.save()
        self.log(player, Event.CMD_SHUFFLE)

     def draw(self, player, qty):
        # top card has lowest pos, as first card on deck to draw
        gcards = player.gamecard_set.filter(slot=GameCard.SLOT_DECK).all()[:qty]
        hand_size = player.gamecard_set.filter(slot=GameCard.SLOT_HAND).count()
        for i, gcard in enumerate(gcards):
            gcard.slot = GameCard.SLOT_HAND
            gcard.pos = hand_size + i
            gcard.save()
            self.log(player, Event.CMD_DRAW, gcard)

    def play_land(self, player, gcard):
        table_size = player.table_size()
        gcard.slot = GameCard.SLOT_TABLE
        gcard.pos = table_size
        gcard.save()
        self.log(player, Event.CMD_PLAY, gcard)
            
    def play_creature(self, player, gcard):
        # todo handle spells
        # if spell, it should be not be moved to table, but trigger
        # ability and go to grave
        hand_size = player.table_size()
        gcard.slot = GameCard.SLOT_TABLE
        gcard.pos = hand_size
        gcard.save()
        # trigger ability?
        self.log(player, Event.CMD_PLAY, gcard)

    def use_ability(self, player, gcard, ability):
        assert ability in gcard.abilities
        assert gcard.player == player
        self.ability_cost(player, gcard, ability)
        self.ability_benefit(player, gcard, ability)

    def ability_cost(self, player, gcard, ability):
        if ability.cost == Ability.COST_TAP:
            gcard.tapped = True
            gcard.save()
            self.log(player, Event.CMD_COST, gcard, ability, comment=ability.cost)
        else:
            raise Exception('unknown cost {}'.format(ability.cost))

    def ability_benefit(self, player, gcard, ability):
        if ability.benefit == Ability.BENEFIT_M1G:
            player.pool += 1
            player.save()
            self.log(player, Event.CMD_BENEFIT, gcard, comment=ability.benefit)
        else:
            raise Exception('unknown benefit {}'.format(ability.benefit))


    def log(self, actor, cmd, gcard=None, error=False, comment=None):
        Event.objects.create(
            game=self.game, status=self.game.status, turn=self.game.turn, round=self.game.round, phase=self.game.phase,
            health1=self.p1.health, deck1_size=self.p1.deck_size(), hand1_size=self.p1.hand_size(), grave1_size=self.p1.grave_size(), 
            health2=self.p2.health, deck2_size=self.p2.deck_size(), hand2_size=self.p2.hand_size(), grave2_size=self.p2.grave_size(), 
            actor=actor, cmd=cmd, gcard=gcard, error=error, comment=comment
        )


class Bot:

    def __init__(self, game):
        self.engine = Engine(game, False)
        self.tree = Tree()
        self.tree.create_node('root', 'root')

    def analyze(self):
        # create structure
        p = self.engine.active_player
        node = self.tree['root']
        self._add_available_moves(p, node)

    def _add_available_moves(self, player, node):
        if 

    def play(self):
        func = getattr(self, 'play_{}'.format(self.engine.game.phase))
        func()

    def play_main(self):
        p = self.engine.active_player
        # play land
        for gcard in p.hand() and gcard.is_affordable():
            if gcard.card.is_land():
                self.engine.play_land(p, gcard)
                break
        # play creature
        for gcard in p.hand():
            if gcard.card.is_creature() and gcard.is_affordable():
                self.pay(p, gcard)

    def pay(self, p, gcard):
        while p.pool < gcard.card.mana:
            # for every land see if you can tap it
            land = p.get_any_untapped_land()
            self.engine.use_ability(p, land, land.abilities.get())


# def minimax(position, depth, alpha, beta, maximizingPlayer):
#     if depth == 0 or game_over in position:
#         return static evaluation of position
#
#     if maximizingPlayer:
#         maxEval = -infinity
#         for each child of position
#             eval = minimax(child, depth - 1, alpha, beta false)
#             maxEval = max(maxEval, eval)
#             alpha = max(alpha, eval)
#             if beta <= alpha
#                 break
#         return maxEval
#
#     else
#         minEval = +infinity
#         for each child of position
#             eval = minimax(child, depth - 1, alpha, beta true)
#             minEval = min(minEval, eval)
#             beta = min(beta, eval)
#             if beta <= alpha
#                 break
#             return minEval
#
# // initial
# call minimax(currentPosition, 3, -∞, +∞, true)


def create_random_deck(player, lands, creatures):
    # add 20 lands
    n = 20
    for l in range(n):
        random_land = choice(lands)
        GameCard.objects.create(player=player, card=random_land, pos=(l + 1))

    # add 10 creatures x4
    for c in range(10):
        random_creature = choice(creatures)
        for i in range(4):
            n += 1
            GameCard.objects.create(player=player, card=random_creature, pos=n)

    return player.gamecard_set.all()


def create_random_game(lands, creatures):
    # game
    game = Game.objects.create()
    # players
    player1 = game.player_set.create()
    player2 = game.player_set.create()
    # decks
    deck1 = create_random_deck(player1, lands, creatures)
    deck2 = create_random_deck(player2, lands, creatures)
    # done
    return game



















