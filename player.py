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

def communication(number_queue,data_queue,send_info):
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
     
        data_queue.put(new_cartes)
        data = send_info.get()
        print(data)
        client_socket.sendall(str(data.encode()))


    

def player(i, state, sem,nb_player,data_queue,newstdin,send_info):
    while game:
        if state[i] == 1:
            print(f"Le Player {i+1} va jouer ")
            print()
            sem.release()
            state[i] = 0
            sem.acquire()
            carte = data_queue.get()
            list_mains = ast.literal_eval(carte)
            for joueur_index in range(nb_player):
                if joueur_index != i:
                    print(f"Main du joueur {joueur_index + 1}")
                    print(list_mains[joueur_index])
                    print()
            sys.stdin = newstdin
            while True: 
                try:
                    reponse = input("Tapez 1 pour jeter une carte, tapez 2 pour utiliser un jeton d'information : ")
                    choix = int(reponse)
                    assert choix == 1 or choix == 2
                    break

                except ValueError:
                    print("Erreur: Ce n'est pas un nombre\n")

                except AssertionError:
                    print("Le nombre doit être 1 ou 2\n")

            if choix == 1:
                print("Vous avez choisis de jeter une carte")
                sys.stdin = newstdin

                while True: 
                    try:
                        reponse2 = input("Quelle carte voulez vous jeter, donnez l'indice : ")
                        choix2 = int(reponse)
                        assert 0 < choix2 < 5
                        break

                    except ValueError:
                        print("Erreur: Ce n'est pas un nombre\n")

                    except AssertionError:
                        print("Le nombre doit être entre 1 et 5\n")

                print(f"Vous avez choisis de jeter la carte {list_mains[i][choix2-1]}")

                send_info.put([i, choix2])

            elif choix == 2:
                print("Vous avez choisis d'utiliser un token d'information")

            print(f"Le Player {i+1} a fini de jouer")
            player_suivant = (i+1) % nb_player
            state[player_suivant] = 1
            

    

if __name__ == "__main__":
    clear()
    logo()
    player_queue = queue.Queue()
    shared_data_queue = queue.Queue()
    send_info = multiprocessing.Queue()
    thread_communication = threading.Thread(target=communication,args=(player_queue,shared_data_queue,send_info))
    thread_communication.start()
    newstdin = os.fdopen(os.dup(sys.stdin.fileno()))
    nb_player = player_queue.get()

    state = multiprocessing.Array('i', range(nb_player))
    state[:] = [0] * nb_player
    state[0] = 1
    
    sem = multiprocessing.Semaphore(0)

    processes = [multiprocessing.Process(target=player, args=(i, state, sem,nb_player,shared_data_queue,newstdin,send_info)) for i in range(nb_player)]

    for process in processes:
        process.start()

    value = send_info.get()
    print(value)

    for process in processes:
        process.join()

    
    thread_communication.join()



