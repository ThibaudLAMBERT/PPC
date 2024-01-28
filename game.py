
import threading
import socket
import random
import time
import os
from multiprocessing import Process, Manager, shared_memory
import subprocess
import platform
import ast
import client
import server
import signal
import sys



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
def gagne():
    print(f"{YELLOW}")
    print(" ____   ____    ____  __ __   ___   __  __ ")
    print("|    \ |    \  /    ||  |  | /   \ |  ||  |")
    print("|  o  )|  D  )|  o  ||  |  ||     ||  ||  |")
    print("|     ||    / |     ||  |  ||  O  ||__||__|")
    print("|  O  ||    \ |  _  ||  :  ||     | __  __ ")
    print("|     ||  .  \|  |  | \   / |     ||  ||  |")
    print("|_____||__|\_||__|__|  \_/   \___/ |__||__|")
                                          
                                           

def carte(couleur, number):
    print("████████")
    print("██    ██")
    print(f"██  {number}  ██")
    print("██    ██")
    print("████████")
    
def perdu():
    print(" ██▓███  ▓█████  ██▀███  ▓█████▄  █    ██                ")
    print("▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒▒██▀ ██▌ ██  ▓██▒               ")
    print("▓██░ ██▓▒▒███   ▓██ ░▄█ ▒░██   █▌▓██  ▒██░               ")
    print("▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  ░▓█▄   ▌▓▓█  ░██░               ")
    print("▒██▒ ░  ░░▒████▒░██▓ ▒██▒░▒████▓ ▒▒█████▓  ██▓  ██▓  ██▓ ")
    print("▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░ ▒▒▓  ▒ ░▒▓▒ ▒ ▒  ▒▓▒  ▒▓▒  ▒▓▒ ")
    print("░▒ ░      ░ ░  ░  ░▒ ░ ▒░ ░ ▒  ▒ ░░▒░ ░ ░  ░▒   ░▒   ░▒  ")
    print("░░          ░     ░░   ░  ░ ░  ░  ░░░ ░ ░  ░    ░    ░   ")
    print("            ░  ░   ░        ░       ░       ░    ░    ░  ")
    print("                          ░                 ░    ░    ░  ")
def perdu2():
    print("  ▄███████▄    ▄████████    ▄████████ ████████▄  ███    █▄  ")
    print("  ███    ███   ███    ███   ███    ███ ███   ▀███ ███    ███ ")
    print("  ███    ███   ███    █▀    ███    ███ ███    ███ ███    ███ ")
    print("  ███    ███  ▄███▄▄▄      ▄███▄▄▄▄██▀ ███    ███ ███    ███ ")
    print("▀█████████▀  ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   ███    ███ ███    ███ ")
    print("  ███          ███    █▄  ▀███████████ ███    ███ ███    ███ ")
    print("  ███          ███    ███   ███    ███ ███   ▄███ ███    ███ ")
    print(" ▄████▀        ██████████   ███    ███ ████████▀  ████████▀  ")
    print("                            ███    ███                       ")



def logo():
    print("  _    _                   _     _ " )
    print(" | |  | |                 | |   (_)    ")
    print(" | |__| | __ _ _ __   __ _| |__  _ ___ ")
    print(" |  __  |/ _` | '_ \ / _` | '_ \| / __|")
    print(" | |  | | (_| | | | | (_| | |_) | \__ \ ")
    print(" |_|  |_|\__,_|_| |_|\__,_|_.__/|_|___/")


def initialisation(data, client_socket):
    client_socket.sendall(data.encode())
    nb_player = int(client_socket.recv(1024).decode())
    pid = int(client_socket.recv(1024).decode())
    return nb_player,pid

#connexion/initialisation du socket et envoi d'un ack, et reception du nombre de joueurs
#si init=False, alors on envoie juste data a travers le socket
def comm(data,client_socket):
    client_socket.sendall(data.encode())

#initilisation du deck
def deck_init(nb_players):
    deck =[[1, 1, 1, 2, 2, 3, 3, 4, 4, 5]for _ in range(nb_players)]
    return deck

#tirage d'une carte 
def tirage_carte(deck):
    if deck == []:
        return [0,0]  # Retourne None si le deck est vide
    
    couleur_index = random.randint(0, len(deck) - 1)
    
    while deck[couleur_index] == []:
        couleur_index = random.randint(0, len(deck) - 1)
    
    carte_index = random.randint(0, len(deck[couleur_index]) - 1)
    couleur = liste_couleurs[couleur_index]
    
    carte = deck[couleur_index][carte_index]
    deck[couleur_index].pop(carte_index)
    
    return [carte, couleur], deck

#tirage de 5 cartes
def tirage_main(deck):
    a_envoyer=[]
    for _ in range (5):
            carte_tirer , deck = tirage_carte(deck)
            a_envoyer.append(carte_tirer)
    return(a_envoyer)
    # comm(a_envoyer)

#si init=True, la fonction  initialise les tokens, sinon elle retire un token
def informations_token_init(nb_players):
    
    tokens=nb_players+3
    return (tokens)


def suppr_card_deck(deck, index_color, numero_carte):
    deck[index_color] = [element for element in deck[index_color] if element != numero_carte]
    return deck

#si init=True, la fonction  initialise les tokens, sinon elle retire un token
def fuse_token_init():
    return 3
    
def couleurToIndice(couleur):
    for i in range(len(liste_couleurs)):
        if liste_couleurs[i]==couleur:
            return i


def modify_shared_list(shared_list):
    shared_list.append('3')

def wait_player(client_socket):
    requete = client_socket.recv(1024)
    requete_decoded = requete.decode()
    requete_list = ast.literal_eval(requete_decoded)
    return requete_list


def remplace_cartes(liste_cartes, carte_a_remplacer, deck):
    for i, player in enumerate(liste_cartes):
        for j, cartes in enumerate(player):
            if cartes == carte_a_remplacer:
                for color in deck :
                    if color:
                        nouvelle_carte,deck = tirage_carte(deck)
                    else:   
                        nouvelle_carte = [0,0]
                liste_cartes[i][j] = nouvelle_carte
    return liste_cartes




def main(index, shared_memory,shared_memory2):
    
    HOST = "localhost"
    PORT = 6700
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        
        with client_socket:
            
            nb_players,pid = initialisation("Hello, initialize!",client_socket)
            deck = deck_init(nb_players)
            couleurs_en_jeu = liste_couleurs[:nb_players]
            shared_memory[0]=informations_token_init(nb_players)
            shared_memory[1]=fuse_token_init()
            
            
            
            for i in range (nb_players):
                shared_memory2[i] = 0 


            mains=[]
            for i in range (nb_players):
                mains.append(tirage_main(deck))
            

            #comm(str(mains),client_socket)
           

            comm(str(mains),client_socket)

            while game:
                requete = wait_player(client_socket)
                if requete[0] == 1:
                    
                    player_requete = requete[1]
                    index_card = requete[2]
                    if mains[player_requete][index_card][0]==shared_memory2[couleurToIndice(mains[player_requete][index_card][1])]+1:
                        shared_memory2[couleurToIndice(mains[player_requete][index_card][1])]+=1
                        #print(f"carte à supprimé : {mains[player_requete][index_card][0]}, {couleurToIndice(mains[player_requete][index_card][1])}")
                        for color in deck :
                            if color:
                                deck = suppr_card_deck(deck,couleurToIndice(mains[player_requete][index_card][1]),mains[player_requete][index_card][0])
                            else:
                                continue
                            
                        mains = remplace_cartes(mains,mains[player_requete][index_card],deck)

                        
                        #mains = remplace_cartes(mains,mains[player_requete][index_card],deck)

                    else:
                        shared_memory[1] -= 1
                        card_tirer,deck = tirage_carte(deck)
                        mains[player_requete][index_card] = card_tirer
                    #print(card_tirer)

                    

                    
                    compteur = 0

                    for parcours in range(nb_players):
                        if shared_memory2[parcours] == 5:
                            compteur += 1
                    
                    if compteur == nb_players:
                        gagne()
                        print("Bravo, vous avez gagné !!!")
                        
                        os.kill(pid,signal.SIGUSR1)
                        sys.exit()
                    if shared_memory[1] == 0:
                        perdu2()
                        print("Dommage, vous avez perdu...")
                        os.kill(pid,signal.SIGUSR1)
                        sys.exit()
                    


                    #print("Il a choisis de jeter une carte")
                    player_requete = requete[1]
                    index_card = requete[2]
                    #print(mains[player_requete][index_card])
                    # card_tirer = tirage_carte(deck)
                    # #print(card_tirer)
                    # if card_tirer != []:
                    #     mains[player_requete][index_card] = card_tirer
                    # else:
                    #     if mains[player_requete][index_card]:
                    #         mains[player_requete][index_card].pop()
                    #print(str(mains))
                    comm(str(mains),client_socket)

                    

                elif requete[0] == 2:
                    shared_memory[0]-=1
                    comm(str(mains),client_socket)



# liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "rose", "gris", "marron", "turquoise"]

# def couleurToIndice(couleur):
#     for i in range(len(liste_couleurs)):
#         if liste_couleurs[i]==couleur:
#             return int(i)


# mains=[[[1, 'rouge']]]
# requete=[1, 0, 0]
# pile=[0, 0]
# player_requete = requete[1]
# index_card = requete[2]
# print(mains[player_requete][index_card][0])

# print(couleurToIndice(mains[player_requete][index_card][1]))

# if mains[player_requete][index_card][0]==pile[couleurToIndice(mains[player_requete][index_card][1])]+1:
#     print("ouiiii")
#     pile[couleurToIndice(mains[player_requete][index_card][1])]+=1
# else: print("bug")
# print(pile)

                                        
    



if __name__ == "__main__":
    main()
    
    
    
