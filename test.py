
import multiprocessing
import subprocess
import os





def start_game(shared_memory):
    subprocess.run(["python", "game.py", str(shared_memory)])

def start_player(shared_memory):
    subprocess.run(["python", "player.py", str(shared_memory)])

if __name__ == "__main__":
    # Créez une mémoire partagée
    shared_memory = multiprocessing.Value('i', 0)

    # Lancez game.py et player.py avec la mémoire partagée
    game_process = multiprocessing.Process(target=start_game, args=(shared_memory,))
    player_process = multiprocessing.Process(target=start_player, args=(shared_memory,))

    game_process.start()
    player_process.start()

    game_process.join()
    player_process.join()
    
