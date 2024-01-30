import sys
from multiprocessing import Process, Array
MEMORY_SIZE = 100
import player
import game
import os
import signal

#handler du process pour le supprimer à la fin de partie 
def handler(sig,frame):
    if sig == signal.SIGUSR1:
        sys.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGUSR2,handler) #mise en attente du signal

    index=2 
    shared_memory = Array('L', MEMORY_SIZE) #création de la mémoire partagée contenant les tokens
    shared_memory2 = Array('i', MEMORY_SIZE) #création de la mémoire partagée contenant les piles de couleurs
    newstdin = os.fdopen(os.dup(sys.stdin.fileno())) #création de la redirection d'entrée standard 
    
    child = Process(target=game.main, args=(index, shared_memory,shared_memory2)) #création du process enfant Game
    child1= Process(target=player.main, args=(index, shared_memory,newstdin,shared_memory2)) #création du process enfant Player
    
    #démarrage des deux process enfants
    child1.start() 
    child.start()
    
    #attente des deux processs enfants
    child1.join()
    child.join()