import os
import time
from player import Player, PlayerStatus, PlayerAction
from game import PokerGame, GamePhase
from baseplayers import InputPlayer
from my_players import PokerBot


def run_game():

    players = [
        PokerBot("Alice", 1000),
    
    ]
    
    # Create game
    game = PokerGame(players, big_blind=20)

    # Run several hands
    for _ in range(2):
        game.start_new_hand()
        
        # Main game loop
        num_tries = 0
        while game.phase != GamePhase.SHOWDOWN:

            if num_tries == 3:
                game.player_action(PlayerAction.FOLD, 0)
                num_tries = 0
                continue

            player = game.players[game.active_player_index]

            if game.num_active_players() == 1 and player.bet_amount == game.current_bet:
                game.advance_game_phase()
                game.display_game_state()
                continue

            print(f"\n{player.name}'s turn")
            print(f"Your cards: {[str(c) for c in player.hole_cards]}")

            try:
                is_successful = game.get_player_input()
            except TypeError:
                is_successful = False

            if not is_successful:
                print("Invalid command received.")
                num_tries += 1
            else:
                num_tries = 0

        print("\nHand complete. Starting new hand...")
        time.sleep(5)


if __name__ == "__main__":
    run_game()
