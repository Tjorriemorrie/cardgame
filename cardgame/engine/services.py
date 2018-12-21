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
                'deck': {},
                'hand': {},
                'table': {},
                'grave': {},
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
                player_item[gcard.slot][gcard.pk] = gcard_item
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
        gcard.pos = gcard_data['pos']
        gcard.slot = gcard_data['slot']
        gcard.tapped = gcard_data['tapped']
        gcard.save()

    ##############################
    # Game helpers
    ##############################
    
    def is_status_setup(self):
        return self.data['status'] == Game.STATUS_SETUP

    def is_phase_draw(self):
        return self.data['phase'] == Game.PHASE_DRAW

    def is_phase_main(self):
        return self.data['phase'] == Game.PHASE_MAIN

    def is_phase_debate(self):
        return self.data['phase'] == Game.PHASE_DEBATE

    def is_action_phase(self):
        return self.data['phase'] in [Game.PHASE_MAIN, Game.PHASE_DEBATE]

    def is_phase_upkeep(self):
        return self.data['phase'] == Game.PHASE_UPKEEP

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
        persons = [gc for gc in player['hand'].values() if gc['card']['kind'] == Card.KIND_PERSON]
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
    TYPE_PASS = 'pass'
    TYPE_PERSON = 'person'
    TYPE_DRAW = 'draw'

    def __init__(self, type_, gcard=None):
        self.type_ = type_
        self.gcard = gcard

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.type_)

    def is_type_pass(self):
        return self.type_ == self.TYPE_PASS

    def is_type_person(self):
        return self.type_ == self.TYPE_PERSON

    def is_type_draw(self):
        return self.type_ == self.TYPE_DRAW


class Engine(GameAdaptor):

    def __init__(self, game_or_data):
        if isinstance(game_or_data, Game):
            self._game = game_or_data
            self.to_dict(game_or_data)
        else:
            self._game = None
            self.data = deepcopy(game_or_data)

    def __repr__(self):
        return '{}(_game={})'.format(self.__class__.__name__, bool(self.__game))

    def setup_game(self):
        for player in self.data['players']:
            self.shuffle_deck(player)
            self.draw(player, Game.START_DRAW_NUMBER)
        self.next_status()
        self.next_phase()

    def shuffle_deck(self, player):
        # randomizes the deck dictionary
        gcards = list(player['deck'].values())
        shuffle(gcards)
        player['deck'] = {}
        for i, gcard in enumerate(gcards):
            gcard['pos'] = i + 1
            self.save_gcard(gcard)
            player['deck'][gcard['pk']] = gcard
        self.log(player['pk'], Event.CMD_SHUFFLE)

    def draw(self, player, qty):
        # top card located at end of list, as first card on deck to draw
        # move from deck to hand
        hand_size = len(player['hand'])
        for i in range(qty):
            gcard = list(player['deck'].values()).pop()  # <-- handle if empty!
            gcard['slot'] = GameCard.SLOT_HAND
            gcard['pos'] = hand_size + i
            del player['deck'][gcard['pk']]
            player['hand'][gcard['pk']] = gcard
            self.save_gcard(gcard)
            self.log(player['pk'], Event.CMD_DRAW, gcard['pk'])

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
            # round increases only after player 2 finished
            self.data['round'] += 1 if self.data['turn'] == 2 else 0
            self.data['turn'] = 2 if self.data['turn'] == 1 else 1
        self.data['phase'] = new_phase
        self.save_game()
        self.log(self.get_player()['pk'], Event.CMD_PHASE)

        # auto continue phase if no moves available
        moves = self.get_available_moves()
        if not moves:
            self.next_phase()

    def get_available_moves(self):
        """get moves but for new moves the action has to have been taken on the engine copy"""
        moves = []

        # for phase
        if self.is_phase_debate():
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

        elif self.is_phase_draw():
            moves.append(Move(Move.TYPE_DRAW))

        elif self.is_phase_upkeep():
            # not doing anything till such logic is required
            pass
        else:
            raise Exception('what phase?')

        return moves

    def play_pass(self):
        self.next_phase()
        self.log(self.get_player(), Event.CMD_PASS)

    def play_person(self, gcard):
        # move from hand to table
        player = self.get_player()
        table_size = len(player['table'])
        gcard['slot'] = GameCard.SLOT_TABLE
        gcard['pos'] = table_size
        del player['hand'][gcard['pk']]
        player['table'][gcard['pk']] = gcard
        self.save_gcard(gcard)
        self.log(player, Event.CMD_PLAY, gcard)
        # no next phase, can still play opinions
            
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
        super().save_game()

    def save_gcard(self, gcard_data):
        super().save_gcard(gcard_data)

    def log(self, actor_pk, cmd, gcard_pk=None, error=False, comment=None):
        Event.objects.create(
                game_id=self.data['pk'], status=self.data['status'],
            turn=self.data['turn'], round=self.data['round'], phase=self.data['phase'],
            health1=self.data['players'][0]['health'], deck1_size=len(self.data['players'][0]['deck']), 
            hand1_size=len(self.data['players'][0]['hand']), grave1_size=len(self.data['players'][0]['grave']),
            health2=self.data['players'][1]['health'], deck2_size=len(self.data['players'][1]['deck']), 
            hand2_size=len(self.data['players'][1]['hand']), grave2_size=len(self.data['players'][1]['grave']),
            actor_id=actor_pk, command=cmd, gcard_id=gcard_pk, error=error, comment=comment
        )


class MonteCarloEngine(Engine):

    def save_game(self, *args, **kwargs):
        return

    def save_gcard(self, *args, **kwargs):
        return

    def log(self, *args, **kwargs):
        return


class Bot:

    def __init__(self, engine):
        self.tree = Tree()
        self.tree.create_node('root', 'root', data={'edata': engine.data, 'game_over': False,
                                                    'moves': []})

    def analyze(self):
        depth = 1
        root = self.tree['root']
        is_player_1 = root.data['edata']['turn'] == 1
        best_eval = self.minimax(root, depth, is_player_1)
        return best_eval, self._get_best_moves()

    def _get_best_moves(self):
        best_moves = None
        max_value = float('-inf')
        root = self.tree['root']
        for child_id in root.fpointer:
            child = self.tree[child_id]
            value = child.data['value']
            if value > max_value:
                max_value = value
                best_moves = child.data['moves']
        if not best_moves:
            raise Exception('expected best moves')
        return best_moves

    def _get_static_eval(self, final_position):
        value = 0
        edata = final_position.data['edata']
        p1 = edata['players'][0]
        p2 = edata['players'][1]

        # add health
        p1_health = p1['health']
        p2_health = p2['health']
        value += p1_health - p2_health

        # add card counts
        slot_scales = {
            GameCard.SLOT_TABLE: 0.3,
            GameCard.SLOT_HAND: 0.2,
            GameCard.SLOT_DECK: 0.03,
            GameCard.SLOT_GRAVE: 0.02,
        }
        for slot_key, scale in slot_scales.items():
            p1_slot_cnt = len(p1[slot_key])
            p2_slot_cnt = len(p2[slot_key])
            value += p1_slot_cnt * scale - p2_slot_cnt * scale

        # adjust eval perspective (requires prev pos to determine if maximizing player)
        # e.g if maximizing player is p2, then flip eval
        parent = self.tree[final_position.bpointer]
        flip_value = 1 if parent.data['edata']['turn'] == 1 else -1
        value *= flip_value

        return value

    def _create_node_from_moves(self, parent, moves):
        e = MonteCarloEngine(parent.data['edata'])
        turn_at_start = e.data['turn']
        for move in moves:

            if move.is_type_pass():
                if len(moves) != 1:
                    raise Exception('should only be one move')
                # handle separately
                e.play_pass()
                # next phase included in play_pass
                same_player = e.data['turn'] == turn_at_start
                node = self.tree.create_node(parent=parent, data={'edata': e.data, 'moves': [move], 'game_over': False,
                                                                  'same_player': same_player})
                return node

            elif move.is_type_person():
                if len(moves) != 1:
                    raise Exception('should only be one move')
                # handle separately
                e.play_person(move.gcard)
                # no next_phase here, only after opinions were played
                same_player = e.data['turn'] == turn_at_start
                node = self.tree.create_node(parent=parent, data={'edata': e.data, 'moves': [move], 'game_over': False,
                                                                  'same_player': same_player})
                return node

            elif move.is_type_draw():
                if len(moves) != 1:
                    raise Exception('should only be one move')
                e.draw(e.get_player(), 1)
                e.next_phase()
                # can be next player if unable to play any hand card, and nothing on table
                same_player = e.data['turn'] == turn_at_start
                node = self.tree.create_node(parent=parent, data={'edata': e.data, 'moves': [move], 'game_over': False,
                                                                  'same_player': same_player})
                return node

            else:
                raise Exception('what type_ {}?'.format(move.type_))
        raise Exception('expected moves...')

    def _add_children(self, parent):
        e = MonteCarloEngine(parent.data['edata'])
        nodes = []

        # pass
        if e.is_action_phase():
            pass_move = Move(Move.TYPE_PASS)
            node = self._create_node_from_moves(parent, [pass_move])
            nodes.append(node)

        # get all moves
        moves = e.get_available_moves()
        if not moves:
            return nodes

        # make all possible combinations

        # persons
        # add each person as a node, no combinations
        if moves[0].is_type_person():
            for move in moves:
                node = self._create_node_from_moves(parent, [move])
                nodes.append(node)

        # draw
        # there can only be 1 draw for active player
        elif moves[0].is_type_draw():
            node = self._create_node_from_moves(parent, moves)
            nodes.append(node)

        else:
            raise Exception('todo move type')
        return nodes

    def minimax(self, position, depth, is_player_1):
        pdata = position.data
        pmoves = pdata['moves']
        if depth <= 0 or pdata.get('game_over'):
            return self._get_static_eval(position)

        pround = pdata['edata']['round']
        pturn = pdata['edata']['turn']
        pphase = pdata['edata']['phase']

        children = self._add_children(position)

        if is_player_1:
            value = -float('inf')
            for child in children:
                cdata = child.data
                cmoves = cdata['moves']

                cround = cdata['edata']['round']
                cturn = cdata['edata']['turn']
                cphase = cdata['edata']['phase']
                next_is_player_1 = is_player_1 if cdata['same_player'] else not is_player_1

                pos_value = self.minimax(child, depth - 1, next_is_player_1)
                cdata['value'] = pos_value
                value = max(value, pos_value)

        else:  # player 2
            value = float('inf')
            for child in children:
                cdata = child.data
                cmoves = cdata['moves']

                cround = cdata['edata']['round']
                cturn = cdata['edata']['turn']
                cphase = cdata['edata']['phase']
                next_is_player_1 = is_player_1 if cdata['same_player'] else not is_player_1
                pos_value = self.minimax(child, depth - 1, next_is_player_1)
                cdata['value'] = pos_value
                value = min(value, pos_value)

        return value

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


def create_random_deck(player, persons, opinions):
    # add 20 persons
    for p in range(20):
        random_person = choice(persons)
        GameCard.objects.create(player=player, card=random_person, pos=(p + 1),
                                slot=GameCard.SLOT_DECK)

    # add 40 opinions
    for o in range(40):
        random_opinion = choice(opinions)
        n = 20 + o
        GameCard.objects.create(player=player, card=random_opinion, pos=n,
                                slot=GameCard.SLOT_DECK)

    return player.gamecard_set.all()


def create_random_game(persons, opinions):
    # game
    game = Game.objects.create()
    # players
    player1 = game.player_set.create()
    player2 = game.player_set.create()
    # decks
    deck1 = create_random_deck(player1, persons, opinions)
    deck2 = create_random_deck(player2, persons, opinions)
    # done
    return game



