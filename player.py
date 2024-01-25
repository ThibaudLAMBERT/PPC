import threading
import socket
import queue
import multiprocessing
import time
import os
import sys
import ast

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


def gestion_erreur(message,choix):
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



    

def player(i, state, sem,nb_player,card_queue,newstdin,carte_drop_queue):
    while game:
        if state[i] == 1:
            print(f"Le Player {i+1} va jouer ")
            print()
            sem.release()
            state[i] = 0
            sem.acquire()
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
    
    sem = multiprocessing.Semaphore(0)

    processes = [multiprocessing.Process(target=player, args=(i, state, sem,nb_player,card_queue,newstdin,card_drop_queue)) for i in range(nb_player)]

    for process in processes:
        process.start()


    for process in processes:
        process.join()

    
    thread_communication.join()



