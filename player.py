import threading
import socket
from queue import Queue
import multiprocessing

def communication(queue):
    HOST = "localhost"
    PORT = 6667
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
                break

            except ValueError:
                print("Erreur: Ce n'est pas un nombre\n")

        queue.put(reponse)
        value = str(reponse)
        client_socket.sendall(value.encode())
        print("NOMBRE ENVOYE")

def player(i):
    print(f"Je suis le joueur {i+1}")

if __name__ == "__main__":
    player_queue = Queue()
    thread_communication = threading.Thread(target=communication,args=(player_queue,))
    thread_communication.start()

    nb_player = player_queue.get()

    processes = [multiprocessing.Process(target=player, args=(i,)) for i in range(nb_player)]

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    thread_communication.join()
