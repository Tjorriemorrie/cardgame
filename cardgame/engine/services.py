from copy import deepcopy
from random import choice, shuffle

from django.forms import model_to_dict
from treelib import Tree, Node

from cards.models import Ability, Card
from engine.models import Game, GameCard, Event


class GameAdaptor:
    
    def to_dict(self, game):
        self.data = {
            'pk': game.pk,
            'status': game.status,
            'turn': game.turn,
            'round': game.round,
            'phase': game.phase,
            'players': [],
        }
        for player in game.player_set.all():
            player_item = {
                'pk': player.pk,
                'health': player.belief,
                'pool': player.crowd,
                'last_turn_person': player.last_turn_person,
                'deck': [],
                'hand': [],
                'table': [],
            }
            for gcard in player.gamecard_set.all():
                card = {
                    'kind': gcard.card.kind,
                    'support': gcard.card.support,
                    'abilities': [],
                    'power': gcard.card.power,
                    'endurance': gcard.card.endurance,
                }
                gcard_item = {
                    'pk': gcard.pk,
                    'card': card,
                    'pos': gcard.pos,
                    'slot': gcard.slot,
                    'tapped': gcard.tapped,
                }
                player_item[gcard.slot].append(gcard_item)
            self.data['players'].append(player_item)

    def save_game(self):
        game = Game.objects.get(pk=self.data['pk'])
        game.status = self.data['status']
        game.turn = self.data['turn']
        game.round = self.data['round']
        game.phase = self.data['phase']
        game.save()

    def save_gcard(self, gcard_data):
        gcard = GameCard.objects.get(pk=gcard_data['pk'])
        gcard.pos = gcard['pos']
        gcard.slot = gcard['slot']
        gcard.tapped = gcard['tapped']
        gcard.save()

    ##############################
    # Game helpers
    ##############################
    
    def is_status_setup(self):
        return self.data['status'] == Game.STATUS_SETUP

    def is_phase_combat(self):
        return self.data['phase'] == Game.PHASE_DEBATE

    def is_phase_main(self):
        return self.data['phase'] == Game.PHASE_MAIN

    def is_status_finished(self):
        return self.data['status'] == Game.STATUS_DONE

    def get_player(self, active=True):
        i = self.data['turn'] - 1
        if not active:
            i = not i
        return self.data['players'][i]

    ##############################
    # Player helpers
    ##############################

    def has_played_person(self, active=True):
        player = self.get_player(active)
        return player['last_turn_person'] == self.data['turn']

    def get_hand_persons(self, active=True):
        player = self.get_player(active)
        persons = [gc for gc in player['hand'] if gc['card']['kind'] == Card.KIND_PERSON]
        return persons

    def get_table_opinions(self, active=True, untapped=False):
        player = self.get_player(active)
        opinions = [gc for gc in player['table'] if gc['card']['kind'] == Card.KIND_OPINION]
        if untapped:
            opinions = [gc for gc in opinions if not gc['tapped']]
        return opinions

    ##############################
    # GameCard helpers
    ##############################


class Move:
    TYPE_PERSON = 'person'

    def __init__(self, type_, gcard):
        self.type_ = type_
        self.gcard = gcard


class Engine(GameAdaptor):

    def __init__(self, game_or_data):
        if isinstance(game_or_data, Game):
            self._game = game_or_data
            self.to_dict(game_or_data)
            self.mc = False
        else:
            self._game = None
            self.data = deepcopy(game_or_data)
            self.mc = True

    def setup_game(self):
        for player in self.data['players']:
            self.shuffle_deck(player)
            self.draw(player, Game.START_DRAW_NUMBER)
        self.next_status()
        self.next_phase()

    def shuffle_deck(self, player):
        gcards = player['deck']
        new_positions = list(range(len(gcards)))
        shuffle(new_positions)
        for new_pos, gcard in zip(new_positions, gcards):
            gcard['pos'] = new_pos + 1
            self.save_gcard(gcard)
        self.log(player['pk'], Event.CMD_SHUFFLE)

    def draw(self, player, qty):
        # top card has lowest pos, as first card on deck to draw
        hand_size = len(player['hand'])
        for i in range(qty):
            gcard = player['deck'].pop()
            gcard['slot'] = GameCard.SLOT_HAND
            gcard['pos'] = hand_size + i
            player['hand'].append(gcard)
            self.save_gcard(gcard)
            self.log(player['pk'], Event.CMD_DRAW, gcard)

    def next_status(self):
        i = Game.STATUS_ORDER.index(self.data['status'])
        new_status = Game.STATUS_ORDER[i + 1]
        self.data['status'] = new_status
        self.save_game()
        self.log(self.get_player(True)['pk'], Event.CMD_STATUS)

    def next_phase(self):
        i = Game.PHASE_ORDER.index(self.data['phase'])
        try:
            new_phase = Game.PHASE_ORDER[i + 1]
        except IndexError:
            new_phase = Game.PHASE_ORDER[0]
            self.data['turn'] = 2 if self.data['turn'] == 1 else 1
            self.data['round'] += 1
        self.data['phase'] = new_phase
        self.save_game()
        self.log(self.get_player(True)['pk'], Event.CMD_PHASE)

        # auto continue phase if no moves available
        moves = self.get_available_moves()
        if not moves:
            self.next_phase()

    def get_available_moves(self):
        moves = []

        # for phase
        if self.is_phase_combat():
            opinions = self.get_table_opinions(untapped=True)
            if opinions:
                raise Exception('todo')

        elif self.is_phase_main():
            # get list of available persons to play
            if not self.has_played_person():
                hpersons = self.get_hand_persons()
                # skip to looking at other cards if you cannot play a person
                if hpersons:
                    for hperson in hpersons:
                        moves.append(Move(Move.TYPE_PERSON, hperson))
                    return moves
            # otherwise look at all other cards to play
            raise Exception('todo')
        else:
            raise Exception('what phase?')
        return moves

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

    def save_game(self):
        if self.mc:
            return
        super().save_game()

    def save_gcard(self, gcard):
        if self.mc:
            return
        super().save_gcard(gcard)

    def log(self, actor_pk, cmd, gcard_pk=None, error=False, comment=None):
        if self.mc:
            return
        Event.objects.create(
            game__id=self.data['pk'], status=self.data['status'],
            turn=self.data['turn'], round=self.data['round'], phase=self.data['phase'],
            health1=self.data['players'][0]['health'], deck1_size=len(self.data['players'][0]['deck']), 
            hand1_size=len(self.data['players'][0]['hand']), grave1_size=len(self.data['players'][0]['size']), 
            health2=self.data['players'][1]['health'], deck2_size=len(self.data['players'][1]['deck']), 
            hand2_size=len(self.data['players'][1]['hand']), grave2_size=len(self.data['players'][1]['size']), 
            actor__id=actor_pk, cmd=cmd, gcard__id=gcard_pk, error=error, comment=comment
        )


class Bot:

    def __init__(self, engine):
        self.tree = Tree()
        self.tree.create_node('root', 'root', data={'e': engine.data})

    def analyze(self):
        best_eval = self.minimax(self.tree['root'], 5, -float('inf'), float('inf'), True)
        return best_eval, self._get_best_move()

    def _get_best_move(self):
        raise Exception('todo')

    def _get_static_eval(self):
        raise Exception('todo')

    def _add_children(self, parent, maximizing_player):
        # default - do nothing
        e = Engine(parent.data['e'])
        nodes = [
            self.tree.create_node(parent=parent, data={'e': e.data, 'actions': []})
        ]
        # get all moves
        moves = e.get_available_moves()
        0/0
        # make all possible combinations
        return nodes

    def minimax(self, position, depth, alpha, beta, maximizing_player):
        data = position.data
        if not depth or data.get('game_over'):
            return self._get_static_eval()

        children = self._add_children(position, maximizing_player)

        if maximizing_player:
            max_eval = -float('inf')
            for child in children:
                eval = self.minimax(child, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval

        else:
            min_eval = float('inf')
            for child in children:
                eval = self.minimax(child, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                return min_eval

    def play(self):
        func = getattr(self, 'play_{}'.format(self.engine.game.phase))
        func()

    def play_main(self):
        p = self.engine.active_player
        # play land
        for gcard in p.hand() and gcard.is_affordable():
            if gcard.card.is_person():
                self.engine.play_land(p, gcard)
                break
        # play creature
        for gcard in p.hand():
            if gcard.card.is_creature() and gcard.is_affordable():
                self.pay(p, gcard)

    def pay(self, p, gcard):
        while p.pool < gcard.card.mana:
            # for every land see if you can tap it
            land = p.get_any_untapped_persons()
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



















