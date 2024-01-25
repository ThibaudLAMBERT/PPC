import threading
import socket
import queue
import multiprocessing
import time
import os
import sys
import ast
import sysv_ipc



game = True


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
def logo():
    print("  _    _                   _     _     ")
    print(" | |  | |                 | |   (_)    ")
    print(" | |__| | __ _ _ __   __ _| |__  _ ___ ")
    print(" |  __  |/ _` | '_ \ / _` | '_ \| / __|")
    print(" | |  | | (_| | | | | (_| | |_) | \__ \ ")
    print(" |_|  |_|\__,_|_| |_|\__,_|_.__/|_|___/")

def communication(number_queue,card_queue,carte_drop_queue):
    HOST = "localhost"
    PORT = 6700
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        print("ATTENTE DU SERVER")
        wait = client_socket.recv(1024)
        print(wait.decode())
        print("Recu")

        while True:
            try:
                input_utilisateur = input("Entrez un nombre de joueurs: ")
                reponse = int(input_utilisateur)
                assert reponse >= 2
                break

            except ValueError:
                print("Erreur: Ce n'est pas un nombre\n")

            except AssertionError:
                print("Le nombre doit être supérieur ou égal à 2\n")
        clear()
        number_queue.put(reponse)
        value = str(reponse)
        client_socket.sendall(value.encode())
        print("NOMBRE ENVOYE")


        cartes = client_socket.recv(1024)
        new_cartes=cartes.decode()
     
        card_queue.put(new_cartes)
        card_drop = carte_drop_queue.get()
        card_drop_send = str(card_drop)
        client_socket.sendall(card_drop_send.encode())


def gestion_erreur(message,choix,nb_player=None,current_player=None,color_liste=None):
    if choix == 1:
        while True: 
            try:
                reponse = input(message)
                user_input = int(reponse)
                assert user_input == 1 or user_input == 2
                break

            except ValueError:
                print("Erreur: Ce n'est pas un nombre\n")

            except AssertionError:
                print("Le nombre doit être 1 ou 2\n")

        return user_input
    
    elif choix == 2:
        while True: 
            try:
                reponse = input(message)
                user_input = int(reponse)
                assert 0 < user_input < 5
                break

            except ValueError:
                print("Erreur: Ce n'est pas un nombre\n")

            except AssertionError:
                print("Le nombre doit être entre 1 et 5\n")

        return user_input

    elif choix == 3:
        while True: 
            try:
                reponse = input(message)
                user_input = int(reponse)
                assert 0 < user_input <= nb_player
                assert user_input != current_player+1
                break

            except ValueError:
                print("Erreur: Ce n'est pas un nombre\n")

            except AssertionError:
                print(f"Le nombre doit être entre 1 et {nb_player} et vous ne pouvez pas vous choisir vous même\n")

        return user_input

    elif choix == 4:
        while True: 
            try:
                reponse = input(message)
                user_input = str(reponse).lower()
                assert user_input in color_liste
                break

            except ValueError:
                print("Ce n'est pas une chaîne de caractère\n")

            except AssertionError:
                print(f"La couleur choisis n'est pas dans la liste \n")

    return user_input
        



    

def player(i, state,nb_player,card_queue,newstdin,carte_drop_queue,information_send,mq):
    liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "rose", "gris", "marron", "turquoise"]
    liste_info = []
    while game:
        if information_send[i] == 1:
            message , _ = mq.receive()
            liste_info.append(message.decode())
            information_send[i] = 0


        if state[i] == 1:
            print(f"Le Player {i+1} va jouer ")
            if liste_info != []:
                print (f"Voici les informations que tu as : {liste_info} ")

            print()
            state[i] = 0
            carte = card_queue.get()
            list_mains = ast.literal_eval(carte)
            for joueur_index in range(nb_player):
                if joueur_index != i:
                    print(f"Main du joueur {joueur_index + 1}")
                    print(list_mains[joueur_index])
                    print()
            sys.stdin = newstdin
            choix = gestion_erreur("Tapez 1 pour jeter une carte, tapez 2 pour utiliser un jeton d'information : ",1)

            if choix == 1:
                print("Vous avez choisis de jeter une carte")
                sys.stdin = newstdin
                choix2 = gestion_erreur("Quelle carte voulez vous jeter, donnez l'indice : ",2)

                print(f"Vous avez choisis de jeter la carte {list_mains[i][choix2-1]}")

                carte_drop_queue.put([i, choix2])

            elif choix == 2:
                print("Vous avez choisis d'utiliser un token d'information")

                choix2 = gestion_erreur("Donnez le numero du joueur : ",3,nb_player,i)

                print(f"Vous aves choisis d'informer le joueur {choix2}")

                choix3 = gestion_erreur("Tapez 1 pour indiquer les cartes d'un certain nombre, tapez 2 pour indiquer les cartes d'un certaine couleur : ", 1)
                        
                if choix3 == 1:
                    print("Vous avez choisis d'indiquer les cartes d'un certain nombre")
                    choix4 = gestion_erreur("Quel nombre voulez vous indiquer : ", 2)
                    current_index = 1
                    index = []
                    compteur = 0
                    for c in list_mains[choix2-1]:
                        if c[0] == choix4:
                            index.append(current_index)
                            compteur += 1
                        current_index += 1

                    message = f"Tu as {compteur} chiffre(s) {choix4} aux index {index}"
                    mq.send(message.encode(),type=choix2)
                    information_send[choix2-1] = 1


                    print()

                elif choix3 == 2:
                    print("Vous avez choisis d'indiquer les cartes d'une certaine couleur")
                    liste_couleurs = liste_couleurs[:nb_player]
                    choix4 = gestion_erreur(f"Quel couleur voulez vous choisir parmis cette liste : {liste_couleurs} ", 4,color_liste=liste_couleurs)
                    index = []
                    compteur = 0
                    current_index = 1
                    for c in list_mains[choix2-1]:
                        if c[1] == choix4.lower():
                            index.append(current_index)
                            compteur += 1
                        current_index += 1

                    choix4_lower = choix4.lower()

                    message = "Tu as {} {} aux index {}".format(compteur, choix4_lower, index)
                    mq.send(message.encode(),type=choix2)
                    information_send[choix2-1] = 1


                    print()

            print(f"Le Player {i+1} a fini de jouer")
            player_suivant = (i+1) % nb_player
            state[player_suivant] = 1



    

if __name__ == "__main__":
    clear()
    logo()
    player_queue = queue.Queue()
    card_queue = queue.Queue()
    card_drop_queue = multiprocessing.Queue()
    thread_communication = threading.Thread(target=communication,args=(player_queue,card_queue,card_drop_queue))
    thread_communication.start()
    newstdin = os.fdopen(os.dup(sys.stdin.fileno()))
    nb_player = player_queue.get()

    state = multiprocessing.Array('i', range(nb_player))
    state[:] = [0] * nb_player
    state[0] = 1

    key = 112

    mq = sysv_ipc.MessageQueue(key,sysv_ipc.IPC_CREAT)

    information_send = multiprocessing.Array('i', [0] * nb_player)

    

    processes = [multiprocessing.Process(target=player, args=(i, state,nb_player,card_queue,newstdin,card_drop_queue,information_send,mq)) for i in range(nb_player)]

    for process in processes:
        process.start()


    for process in processes:
        process.join()

    
    thread_communication.join()



