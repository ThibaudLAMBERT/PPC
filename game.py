
import socket
import random
import time
import os
from multiprocessing import Process, Manager, shared_memory
import ast
import signal
import sys

## DECORATIONS
##couleurs
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

##clear le terminal
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    
##écran win
def gagne():
    print(f"{YELLOW}")
    print("######                    ######")
    print("## ########################## ##")
    print("##   ######################   ##")
    print("###  ######################  ###")
    print("#### ###################### ####")
    print(" ############################## ")
    print("  ############################  ")
    print("    ########################    ")
    print("     #####################      ")
    print("        ################        ")
    print("          ############          ")
    print("            %%%%%%%%            ")
    print("             %%%%%%             ")
    print("            %%%%%%%%            ")
    print("            %%%%%%%%            ")
    print("           %%%%%%%%%%           ")
    print("          %%%%%%%%%%%%          ")
    print("       ##################       ")
    print("       ####%%%%%%%%%%####       ")
    print("       ###%%%%%%%%%%%%###       ")
    print("       ####%%%%%%%%%%####       ")
    print("     %%%%%%%%%%%%%%%%%%%%%%     ")
    print("    %%%%%%%%%%%%%%%%%%%%%%%%    ")
    print(" ____   ____    ____  __ __   ___   __  __ ")
    print("|    \ |    \  /    ||  |  | /   \ |  ||  |")
    print("|  o  )|  D  )|  o  ||  |  ||     ||  ||  |")
    print("|     ||    / |     ||  |  ||  O  ||__||__|")
    print("|  O  ||    \ |  _  ||  :  ||     | __  __ ")
    print("|     ||  .  \|  |  | \   / |     ||  ||  |")
    print("|_____||__|\_||__|__|  \_/   \___/ |__||__|")
                                          
                 
#écran loose 
def perdu(color):
    print(f"{color}  ▄███████▄    ▄████████    ▄████████ ████████▄  ███    █▄  ")
    print("  ███    ███   ███    ███   ███    ███ ███   ▀███ ███    ███ ")
    print("  ███    ███   ███    █▀    ███    ███ ███    ███ ███    ███ ")
    print("  ███    ███  ▄███▄▄▄      ▄███▄▄▄▄██▀ ███    ███ ███    ███ ")
    print("▀█████████▀  ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   ███    ███ ███    ███ ")
    print("  ███          ███    █▄  ▀███████████ ███    ███ ███    ███ ")
    print("  ███          ███    ███   ███    ███ ███   ▄███ ███    ███ ")
    print(" ▄████▀        ██████████   ███    ███ ████████▀  ████████▀  ")
    print("                            ███    ███                       ")
                              

    

liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "rose", "gris", "marron", "turquoise"]




#### CORPS DU CODE 
game = True



#initialisation du socket et envoi d'un ack, et reception du nombre de joueurs
def initialisation(data, client_socket):
    client_socket.sendall(data.encode())
    nb_player = int(client_socket.recv(1024).decode())
    pid = int(client_socket.recv(1024).decode())
    return nb_player,pid


#envoi d'un message au client
def comm(data,client_socket):
    client_socket.sendall(data.encode())

#initilisation du deck avec toutes les cartes
def deck_init(nb_players):
    deck =[[1, 1, 1, 2, 2, 3, 3, 4, 4, 5]for _ in range(nb_players)]
    return deck


#tirage d'une carte dans le deck et suppression de la carte tirée, si deck vide, renvoie une carte vide
def tirage_carte(deck):
    if deck == []:
        return ["vide","blanc"]
    couleur_index = random.randint(0, len(deck) - 1)
    while deck[couleur_index] == []:
        couleur_index = random.randint(0, len(deck) - 1)
    carte_index = random.randint(0, len(deck[couleur_index]) - 1)
    couleur = liste_couleurs[couleur_index]
    carte = deck[couleur_index][carte_index]
    deck[couleur_index].pop(carte_index)
    return [carte, couleur], deck

#tirage de 5 cartes pour les mains des joueurs
def tirage_main(deck):
    a_envoyer=[]
    for _ in range (5):
            carte_tirer , deck = tirage_carte(deck)
            a_envoyer.append(carte_tirer)
    return(a_envoyer)

#initialisation des token information
def informations_token_init(nb_players):
    tokens=nb_players+3
    return (tokens)

#initialisation des token fuse
def fuse_token_init():
    return 3

#suppression d'une carte dans le deck et renvoie le nouveau deck
def suppr_card_deck(deck, index_color, numero_carte):
    deck[index_color] = [element for element in deck[index_color] if element != numero_carte]
    return deck


#fonction qui renvoie l'indice d'une couleur dans la liste des couleurs
def couleurToIndice(couleur):
    for i in range(len(liste_couleurs)):
        if liste_couleurs[i]==couleur:
            return i


#attente de la requete du joueur, et renvoie la requete string sous forme de liste
def wait_player(client_socket):
    requete = client_socket.recv(1024)
    requete_decoded = requete.decode()
    requete_list = ast.literal_eval(requete_decoded)
    return requete_list


#remplace les cartes jetées par le joueur par de nouvelles cartes
def remplace_cartes(liste_cartes, carte_a_remplacer, deck):
    for i, player in enumerate(liste_cartes):
        for j, cartes in enumerate(player):
            if cartes == carte_a_remplacer:
                for color in deck :
                    if color:
                        nouvelle_carte,deck = tirage_carte(deck)
                    else:   
                        nouvelle_carte = ["/","blanc"]
                liste_cartes[i][j] = nouvelle_carte
    return liste_cartes




def main(index, shared_memory,shared_memory2):
    
    #initialisation du socket
    HOST = "localhost"
    PORT = 6700
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        
        with client_socket:
            
            nb_players,pid = initialisation("Hello, initialize!",client_socket)
            deck = deck_init(nb_players) #initialisation du deck
            couleurs_en_jeu = liste_couleurs[:nb_players] #concaténation des couleurs en jeu
            shared_memory[0]=informations_token_init(nb_players) #initialisation des tokens informations avec la shared memory
            shared_memory[1]=fuse_token_init() #initialisation des tokens fuse avec la shared memory
            
            for i in range (nb_players):
                shared_memory2[i] = 0 #initialisation de la pile de cartes par couleur, si 0 alors rien n'est posé
                                        
            mains=[] #initialisation des mains des joueurs
            for i in range (nb_players):
                mains.append(tirage_main(deck)) #tirage aléatoire des mains des joueurs
            
            comm(str(mains),client_socket) #envoi des mains des joueurs au player
            
            
            
            #debut de la boucle de jeu
            
            while game:
                requete = wait_player(client_socket) #attente de reception d'une requete, de le forme: [numero code, numero joueur, numero carte]
                if requete[0] == 1: #requete code 1 = un joueur a posé sa carte
                    
                    player_requete = requete[1]
                    index_card = requete[2]
                    
                    #si la carte posée est un numero superieur de 1 d'une des cartes dans la pile, alors on l'ajoute à la pile de la bonne couleur
                    if mains[player_requete][index_card][0]==shared_memory2[couleurToIndice(mains[player_requete][index_card][1])]+1:
                        shared_memory2[couleurToIndice(mains[player_requete][index_card][1])]+=1
                        for color in deck : #suppression des cartes identitques à celle posée dans le deck
                            if color:
                                deck = suppr_card_deck(deck,couleurToIndice(mains[player_requete][index_card][1]),mains[player_requete][index_card][0])
                            else:
                                continue
                            
                        #suppression des cartes identiques à celle posée dans les mains des joueurs
                        mains = remplace_cartes(mains,mains[player_requete][index_card],deck) 
                        

                        
                    #sinon, on enlève un token fuse
                    else:
                        shared_memory[1] -= 1
                        for color in deck :
                            if color: #puis on supprime les cartes identiques du deck et des mains des joueurs
                                card_tirer,deck = tirage_carte(deck)
                            else:
                                card_tirer = ["/","blanc"]
                        mains[player_requete][index_card] = card_tirer

                    player_requete = requete[1]
                    index_card = requete[2]
                    comm(str(mains),client_socket) #renvoi des nouvelles mains au processus player

                    

                elif requete[0] == 2: #requete code 2 = un joueur a utilisé un token information
                    shared_memory[0]-=1
                    comm(str(mains),client_socket)
                #on compte le nombre de piles à 5
                compteur_nombre_piles_a_5 = 0

                for parcours in range(nb_players):
                    if shared_memory2[parcours] == 5:
                        compteur_nombre_piles_a_5 += 1

                #si le compteur vaut le nb de joueuers, alors c'est gagné
                if compteur_nombre_piles_a_5 == nb_players:
                    gagne()
                    print("Bravo, vous avez gagné !!!")
                    #on envoi un signal au processus player pour qu'il s'arrete
                    os.kill(pid,signal.SIGUSR1)
                    os.kill(os.getppid(),signal.SIGUSR2)
                    sys.exit()
                    
                #si le nombre de token fuse est égal à 0, alors c'est perdu
                if shared_memory[1] == 0:
                    os.kill(pid,signal.SIGUSR1)
                    os.kill(os.getppid(),signal.SIGUSR2)
                    for _ in range(4):
                        clear()
                        perdu(RED)
                        time.sleep(0.2)
                        clear()
                        perdu(BLUE)
                        time.sleep(0.2)
                        clear()
                        perdu(GREEN)
                        time.sleep(0.2)
                        clear()
                        perdu(YELLOW)
                        time.sleep(0.2)
                    print("Dommage, vous avez perdu...")
                    sys.exit()
             
    



if __name__ == "__main__":
    main()
    
    
    
