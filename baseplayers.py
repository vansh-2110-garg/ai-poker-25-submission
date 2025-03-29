from player import Player, PlayerAction
from game import PokerGame, GamePhase
from card import Card


class FoldPlayer(Player):

    def action(self, game_state: list[int], action_history: list):
        return PlayerAction.FOLD, 0


class RaisePlayer(Player):

    def action(self, game_state: list[int], action_history: list):
        current_raise = game_state[8]
        if self.stack > (current_raise + 40):
            return PlayerAction.RAISE, current_raise + 40
        return PlayerAction.ALL_IN, self.stack


class InputPlayer(Player):
    def action(self, game_state: list[int], action_history: list):
        call_amount = game_state[8] - self.bet_amount

        # Display available actions
        print("Available actions:")
        if call_amount == 0:
            print("1. Check")
            print("2. Bet")
        else:
            print("1. Fold")
            print("2. Call", call_amount)
            print("3. Raise")

        action_input = input("Enter choice: ")

        try:
            if call_amount == 0:
                if action_input == "1":
                    return PlayerAction.CHECK, 0
                elif action_input == "2":
                    amount = int(input("Enter bet amount: "))
                    return PlayerAction.BET, amount
            else:
                if action_input == "1":
                    return PlayerAction.FOLD, 0
                elif action_input == "2":
                    return PlayerAction.CALL, call_amount
                elif action_input == "3":
                    amount = int(input(f"Enter total raise amount: "))
                    return PlayerAction.RAISE, amount
                else:
                    return PlayerAction.FOLD, 0
        except ValueError:
            print("Invalid input")
            return PlayerAction.FOLD, 0
