import sys
from multiprocessing import Process, Array
MEMORY_SIZE = 100
import player
import game
import os

if __name__ == "__main__":

    index=2
    shared_memory = Array('L', MEMORY_SIZE)
    shared_memory2 = Array('i', MEMORY_SIZE)
    newstdin = os.fdopen(os.dup(sys.stdin.fileno()))
    
    child = Process(target=game.main, args=(index, shared_memory,shared_memory2))
    child1= Process(target=player.main, args=(index, shared_memory,newstdin,shared_memory2))
    child1.start()
    child.start()
  
    child1.join()
    child.join()