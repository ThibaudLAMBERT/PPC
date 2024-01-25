import threading
import socket
import queue
import multiprocessing
import time
import os
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

def communication(number_queue,data_queue):
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
        print(cartes.decode())

     
        data_queue.put(cartes)


    

def player(i, state, sem,nb_player,data_queue):
    while game:
        if state[i] == 1:
            print(f"Le Player {i+1} va jouer")
            sem.release()
            state[i] = 0
            sem.acquire()
            carte = data_queue.get()
            print(carte[i])
            print(f"Le Player {i+1} a fini de jouer")
            player_suivant = (i+1) % nb_player
            state[player_suivant] = 1

    

if __name__ == "__main__":
    clear()
    logo()
    player_queue = queue.Queue()
    shared_data_queue = queue.Queue()
    thread_communication = threading.Thread(target=communication,args=(player_queue,shared_data_queue))
    thread_communication.start()

    nb_player = player_queue.get()

    state = multiprocessing.Array('i', range(nb_player))
    state[:] = [0] * nb_player
    state[0] = 1
    
    sem = multiprocessing.Semaphore(0)
    

    processes = [multiprocessing.Process(target=player, args=(i, state, sem,nb_player,shared_data_queue)) for i in range(nb_player)]

    for process in processes:
        process.start()


    for process in processes:
        process.join()

    
    thread_communication.join()



