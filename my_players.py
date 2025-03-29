from player import Player, PlayerAction
from card import Card
import random
class PokerBot(Player):
    def __init__(self, name, stack):
        super().__init__(name, stack)
        self.initial_stack=self.stack
        self.opponent_actions = {'raise': 0, 'call': 0, 'fold': 0, 'check': 0}
        self.opponent_stacks = {}
        self.total_opponent_actions = 0

    def update_opponent_behavior(self, action, game_state):
        """Update opponent behavior and correctly track opponent stacks from game_state."""

        if action[2] in self.opponent_actions:
            self.opponent_actions[action[2]] += 1
            self.total_opponent_actions += 1

        opponent_name = action[1]  # Extract opponent name

        # Extract opponent index from game_state
        active_player_index = game_state[10]  # Index of current active player
        num_players = game_state[11]  # Total players

        # Assuming player order is fixed, derive opponent index
        opponent_index = (active_player_index + num_players - 1) % num_players  # Previous player
        opponent_stack = game_state[13 + opponent_index]  # Get opponent stack from game_state

        # Store opponent stack
        self.opponent_stacks[opponent_name] = opponent_stack

    def get_opponent_tendency(self):
        """Determine opponent's tendencies based on action history and remaining stack."""
        if self.total_opponent_actions == 0:
            return "neutral"

        raise_percentage = self.opponent_actions['raise'] / self.total_opponent_actions
        fold_percentage = self.opponent_actions['fold'] / self.total_opponent_actions
        call_percentage = self.opponent_actions['call'] / self.total_opponent_actions
        avg_stack = sum(self.opponent_stacks.values()) / len(self.opponent_stacks) if self.opponent_stacks else 1

        if raise_percentage > 0.4 and avg_stack > self.stack * 1.5:
            return "very aggressive"
        elif raise_percentage > 0.4:
            return "aggressive"
        elif fold_percentage > 0.5 and avg_stack < self.stack * 0.5:
            return "tight-passive"
        elif fold_percentage > 0.5:
            return "tight"
        elif call_percentage > 0.5 and avg_stack > self.stack * 1.5:
            return "loose-aggressive"
        elif call_percentage > 0.5:
            return "loose"
        else:
            return "neutral"

    def evaluate_preflop(self, hole_cards):
        """Improved Pre-flop hand strength evaluation."""
        ranks = [((i-1) % 13) + 1 if (i % 13) != 0 else 14 for i in hole_cards]

        suits = [(i-1) // 13 for i in hole_cards]


        is_pair = (ranks[0] == ranks[1])
        is_suited = (suits[0] == suits[1])
        is_connected = (abs(ranks[0] - ranks[1]) == 1)

        # More aggressive betting on stronger hands
        if is_pair:
            return 0.7 if ranks[0] >= 10 else 0.6 if ranks[0] >= 7 else 0.55  # Pocket pairs strong to weak
        if is_suited and is_connected:
            return 0.85 if ranks[0] >= 10 else 0.75  # High suited connectors
        if is_suited or is_connected:
            return 0.65 if ranks[0] >= 10 else 0.6  # High Suited or Connected Cards
        if ranks[0] >= 12:
            return 0.4  # High-card hands (AQ, KJ, etc.)
        return 0.3  # Weak hands

    def evaluate_flop(self, hole_cards, community_cards):
        return self.evaluate_postflop(hole_cards, community_cards[:3])

    def evaluate_turn(self, hole_cards, community_cards):
        return self.evaluate_postflop(hole_cards, community_cards[:4])

    def evaluate_river(self, hole_cards, community_cards):
        return self.evaluate_postflop(hole_cards, community_cards)

    

    def evaluate_postflop(self, hole_cards, community_cards):
        """Post-flop hand evaluation with better risk assessment."""
        all_cards = sorted(hole_cards + community_cards)

        ranks = [((i -1)% 13) + 2 if (i % 13) != 0 else 14 for i in all_cards]

        suits = [(i-1) // 13 for i in all_cards]

        def is_flush():
            return max(suits.count(suit) for suit in set(suits)) >= 5

        def is_straight():
            unique_ranks = sorted(set(ranks))
            return any(unique_ranks[i + 4] - unique_ranks[i] == 4 for i in range(len(unique_ranks) - 4))

        def is_flush_draw():
            return max(suits.count(suit) for suit in set(suits)) == 4  # Flush draw (4 same suits)

        def is_straight_draw():
            unique_ranks = sorted(set(ranks))
            return any(unique_ranks[i + 3] - unique_ranks[i] == 3 for i in range(len(unique_ranks) - 3))

        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        three_of_a_kinds = [rank for rank, count in rank_counts.items() if count == 3]
        four_of_a_kinds = [rank for rank, count in rank_counts.items() if count == 4]

        # Stronger weighting for draws
        if is_flush() and is_straight():
            return 1.0  # Straight flush
        elif four_of_a_kinds:
            return 0.95  # Four of a kind
        elif three_of_a_kinds and pairs:
            return 0.9  # Full house
        elif is_flush():
            return 0.85  # Flush
        elif is_straight():
            return 0.8  # Straight
        elif three_of_a_kinds:
            return 0.75  # Three of a kind
        elif len(pairs) >= 2:
            return 0.65  # Two pair
        elif pairs:
            return 0.55  # One pair
        elif is_flush_draw() or is_straight_draw():
            return 0.5  # Strong draws
        else:
            return 0.3  # High card

    def decide_action(self, game_state, action_history):
        """More aggressive decision-making based on improved hand evaluation and opponent moves."""
        hole_cards = game_state[:2]
        community_cards = [card for card in game_state[2:7] if card != 0]
        phase = action_history[-1][0] if action_history else "pre-flop" 
        current_raise = game_state[8]
        strength = 0.5
        updated_opponents = set()  # Track updated opponents to prevent redundant calls

        for action in list(action_history): 
            if action[1] != self.name and action[1] not in updated_opponents:
                print(f"Updating behavior: {action[1]} {action[2]} {action[3]}")
                self.update_opponent_behavior(action, game_state)
                updated_opponents.add(action[1])  # Ensure each opponent is updated only once


        opponent_tendency = self.get_opponent_tendency()
        print("Opponent Tendency:", opponent_tendency)

        if phase =='pre-flop' :
            print(1)
            strength = self.evaluate_preflop(hole_cards)
        elif phase == 'flop':
            print(2)
            strength = self.evaluate_flop(hole_cards, community_cards)
        elif phase == 'turn':
            print(3)
            strength = self.evaluate_turn(hole_cards, community_cards)
        elif phase == 'river':
            print(4)
            strength = self.evaluate_river(hole_cards, community_cards)

        print(f"Hand strength: {strength}")

        # More risk-taking: Increased all-in frequencies
        if random.randint(1,10)==7:
            return PlayerAction.ALL_IN,self.stack
        elif game_state[8] > self.stack and strength > 0.8:
            return PlayerAction.ALL_IN, self.stack
        elif phase == 'river' and strength > 0.8:
            return PlayerAction.ALL_IN, self.stack
        elif phase == 'flop' and strength > 0.9:
            return PlayerAction.ALL_IN, self.stack
        elif phase == 'turn' and strength > 0.85:
            return PlayerAction.RAISE, min(100, self.stack)
        elif strength > 0.7:
            if opponent_tendency in ['aggressive', 'loose']:
                if self.stack > (self.initial_stack * 0.70):
                    if random.sample([0, 1], 1):
                        return PlayerAction.RAISE, min(random.randrange(50, self.stack), self.stack)
                    else:
                        return PlayerAction.RAISE, min(50, self.stack)
                else:
                    return PlayerAction.CALL, game_state[8]
            else:
                return PlayerAction.CALL, game_state[8]
        elif strength > 0.5:
            return PlayerAction.CALL, game_state[8]
        else:
            return (PlayerAction.CALL, game_state[8]) if opponent_tendency == 'loose' else (PlayerAction.FOLD, 0)


    def action(self, game_state, action_history):
            return self.decide_action(game_state, action_history)