
import threading
import socket
import random
import time
import os
from multiprocessing import Process, Manager, shared_memory
import subprocess
import platform
import ast

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

game = True

liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "rose", "gris", "marron", "turquoise"]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def logo():
    print(f"{GREEN}  _    _                   _     _ " )
    print(" | |  | |                 | |   (_)    ")
    print(" | |__| | __ _ _ __   __ _| |__  _ ___ ")
    print(" |  __  |/ _` | '_ \ / _` | '_ \| / __|")
    print(" | |  | | (_| | | | | (_| | |_) | \__ \ ")
    print(" |_|  |_|\__,_|_| |_|\__,_|_.__/|_|___/")


def initialisation(data, client_socket):
    client_socket.sendall(data.encode())
    nb_player = int(client_socket.recv(1024).decode())
    return nb_player

#connexion/initialisation du socket et envoi d'un ack, et reception du nombre de joueurs
#si init=False, alors on envoie juste data a travers le socket
def comm(data,server_socket):
    server_socket.sendall(data.encode())

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

def wait_player(client_socket):
    requete = client_socket.recv(1024)
    requete_decoded = requete.decode()
    requete_list = ast.literal_eval(requete_decoded)
    return requete_list

    

def main():

    clear()
    logo()
    

# Chemin vers le fichier Python que vous souhaitez exécuter


    print("BACKGROUND WINDOW")

    print("Game is ready, sending ack to player")
    HOST = "localhost"
    PORT = 6700
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        with client_socket:
            print("Connected to client: ", address)
            nb_players = initialisation("Hello, initialize!",client_socket)
            print("Number of players:", nb_players)
            deck = deck_init(nb_players)
            couleurs_en_jeu = liste_couleurs[:nb_players]


            mains=[]
            for i in range (nb_players):
                mains.append(tirage_main(deck))
            print(mains)
                
            comm(str(mains),client_socket)
            print("DECK:")
            print(deck)

            while game: 
                requete = wait_player(client_socket)
                if requete[0] == 1:
                    print("Il a choisis de jeter une carte")
                    player_requete = requete[1]
                    index_card = requete[2]
                    print(mains[player_requete][index_card])
                    tirage_carte()


                                        
    



if __name__ == "__main__":
    main()
    
    
    
