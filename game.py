
import threading
import socket
import random
import time
import os
from multiprocessing import Process, Manager, shared_memory

RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"


liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "rose", "gris", "marron", "turquoise"]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def logo():
    print(f"{GREEN}  _    _                   _     _ " )
    print(" | |  | |                 | |   (_)    ")
    print(" | |__| | __ _ _ __   __ _| |__  _ ___ ")
    print(" |  __  |/ _` | '_ \ / _` | '_ \| / __|")
    print(" | |  | | (_| | | | | (_| | |_) | \__ \ ")
    print(f" |_|  |_|\__,_|_| |_|\__,_|_.__/|_|___/{RESET}")




#connexion/initialisation du socket et envoi d'un ack, et reception du nombre de joueurs
#si init=False, alors on envoie juste data a travers le socket
def comm(data, initialisation=False):
    if initialisation:
        global my_socket
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        HOST = "localhost"
        PORT = 6700
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen(1)
            global client_socket
            client_socket, address = server_socket.accept()
            print("Connected to client: ", address)
            client_socket.sendall(data.encode())
            nb_player = int(client_socket.recv(1024).decode())
            return nb_player, client_socket
    else:
        client_socket.sendall(data.encode())

#initilisation du deck
def deck_init(nb_players):
    deck =[[1, 2, 2, 3, 3, 4, 4, 5]for _ in range(nb_players)]
    return deck

#tirage d'une carte 
def tirage_carte(deck):
    couleur_index=random.randint(0,len(deck)-1)
    carte_index=random.randint(0,len(deck[couleur_index])-1)
    couleur=liste_couleurs[couleur_index]
    carte=deck[couleur_index][carte_index]
    deck[couleur_index].pop(carte_index)
    liste=[carte, couleur]
    return(liste)

#tirage de 5 cartes
def tirage_main(deck):
    print("cartes joueur numero")
    a_envoyer=[]
    for _ in range (5):
            a_envoyer.append(tirage_carte(deck))
    return(a_envoyer)
    # comm(a_envoyer)

#si init=True, la fonction  initialise les tokens, sinon elle retire un token
def informations_token(nb_token, nb_players, initialisation=False):
    if initialisation==True:
        tokens=nb_players+3
        return (tokens)
    else:
        return(nb_token-1)

#si init=True, la fonction  initialise les tokens, sinon elle retire un token
def fuse_token(nb_token, initialisation=False):
    if initialisation==True:
        tokens=3
    else:
        return(nb_token-1)
    

def modify_shared_list(shared_list):
    shared_list.append('3')

def main():

    clear()
   



    
   







    
    logo()
    print("Game is ready, sending ack to player")
    nb_players, client_sock = comm("Hello, initialize!", initialisation=True)
    print("Number of players:", nb_players)
    deck=deck_init(nb_players)
    couleurs_en_jeu=liste_couleurs[:nb_players]


    mains=[]
    for i in range (nb_players):
        mains.append(tirage_main(deck))
    print(mains)
    
    comm(str(mains))
    print("DECK:")
    print(deck)

    while True:
        recu=client_socket.recv(1024)
        if recu == ("code1"):
            fuse_token()
                                
    



if __name__ == "__main__":
    main()
    
    
    
