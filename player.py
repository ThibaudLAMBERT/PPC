import threading
import socket
import queue
import multiprocessing
import time
import os
import sys
import ast
import sysv_ipc
import client
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


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def logo():
    print(f"{GREEN}  _    _                   _     _ " )
    print(" | |  | |                 | |   (_)    ")
    print(" | |__| | __ _ _ __   __ _| |__  _ ___ ")
    print(" |  __  |/ _` | '_ \ / _` | '_ \| / __|")
    print(" | |  | | (_| | | | | (_| | |_) | \__ \ ")
    print(" |_|  |_|\__,_|_| |_|\__,_|_.__/|_|___/")


def initialisation(client_socket,number_queue):
    print("ATTENTE DU SERVER")
    wait = client_socket.recv(1024)
    print(wait.decode())
    print("Recu")
    number_queue.put("START")

    
    client_socket.sendall(value.encode())

    print("NOMBRE ENVOYE")
    return reponse


def comm(data,client_socket):
    client_socket.sendall(data)


def send_card(pipe,client_socket):
    cartes = client_socket.recv(1024)
    #print(cartes.decode())
    new_cartes = cartes.decode()
    #print(new_cartes)
    list_mains = ast.literal_eval(new_cartes)
    pipe.send(list_mains)
    return list_mains



def wait_for_player(card_drop_queue):
    card_drop = card_drop_queue.get()
    return card_drop
        



def communication(number_queue,pipe,carte_drop_queue):
    HOST = "localhost"
    PORT = 6700
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        print("ATTENTE DU SERVER")
        wait = client_socket.recv(1024)
        print(wait.decode())
        print("Recu")
        number_queue.put("START")
        time.sleep(0.5)
        nb_player = number_queue.get()
    
        client_socket.sendall(nb_player.encode())

        #print("NOMBRE ENVOYE")

        #nb_player = initialisation(client_socket)
        #number_queue.put(nb_player)



#fin de l'initialisation
        last_list_mains = send_card(pipe,client_socket)
        while game:
             #recoit les cartes de game et le met sur la queue
            requete_player = wait_for_player(carte_drop_queue)
            if requete_player[0] == 1:
                #print("Il a choisis de drop")
                string_requete_player = str(requete_player)
                comm(string_requete_player.encode(),client_socket)
                send_card(pipe,client_socket)
                

            elif requete_player[0] == 2:
                #print("IL a choisis le token")
                string_requete_player = str(requete_player)
                comm(string_requete_player.encode(), client_socket)
                send_card(pipe,client_socket)






    #card_drop = carte_drop_queue.get()
    #card_drop_send = str(card_drop)
    #client_socket.sendall(card_drop_send.encode())


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
        



    

def player(i, state,nb_player,pipe,newstdin_grandchild,carte_drop_queue,information_send,mq,shared_memory,shared_memory2):
    liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "rose", "gris", "marron", "turquoise"]
    liste_info = []
    while game:
        if information_send[i] == 1:
            message , _ = mq.receive()
            liste_info.append(message.decode())
            information_send[i] = 0


        if state[i] == 1:
            print(f"Le Player {i+1} va jouer ")
            time.sleep(0.75)
            print(f"Vous avez {shared_memory[0]} informations token")
            print("Voici les piles en cours : ")
            for i in range(nb_player):
                print(shared_memory2[i])
            if liste_info != []:
                print (f"Voici les informations que tu as : {liste_info} ")

            print()
            state[i] = 0
            
            while pipe.poll():
                list_mains = pipe.recv()

            #print(type(list_mains))


            for joueur_index in range(nb_player):
                if joueur_index != i:
                    print(f"Main du joueur {joueur_index + 1}")
                    print(list_mains[joueur_index])
                    print()
            sys.stdin = newstdin_grandchild
            
            if shared_memory[0] > 0:
                choix = gestion_erreur("Tapez 1 pour jeter une carte, tapez 2 pour utiliser un jeton d'information : ",1)
                if choix == 1:
                    print("Vous avez choisis de jeter une carte")
            else:
                print("Vous n'avez plus de token d'information, vous êtes obliger de poser une carte !")
                choix = 1

            if choix == 1:
                sys.stdin = newstdin_grandchild
                choix2 = gestion_erreur("Quelle carte voulez vous jeter, donnez l'indice : ",2)

                print(f"Vous avez choisis de jeter la carte {list_mains[i][choix2-1]}")

                carte_drop_queue.put([1,i, choix2-1])

            elif choix == 2:
                print("Vous avez choisis d'utiliser un token d'information")

                choix2 = gestion_erreur("Donnez le numero du joueur : ",3,nb_player,i)

                print(f"Vous aves choisis d'informer le joueur {choix2}")

                carte_drop_queue.put([2,i])

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

                    message = f"Tu as {compteur} {choix4_lower} aux index {index}"
                    mq.send(message.encode(),type=choix2)
                    information_send[choix2-1] = 1


                    print()

            print(f"Le Player {i+1} a fini de jouer")
            player_suivant = (i+1) % nb_player
            state[player_suivant] = 1
""" 
def print(message):
    print(f"{RED} ")
    print(message)
    print(f"{RESET}" ) """

    


def main(index, shared_memory,newstdin,shared_memory2):
 
    clear()
    logo()
    
    
    # client.main()
    
    
    player_queue = queue.Queue()
    
    parent_conn, child_conn = multiprocessing.Pipe()

    card_drop_queue = multiprocessing.Queue()
    thread_communication = threading.Thread(target=communication,args=(player_queue,parent_conn,card_drop_queue))
    thread_communication.start()

    player_queue.get()
    sys.stdin = newstdin
    while True:
        try:
            input_utilisateur = input("Entrez un nombre de joueurs: ")
            nb_player = int(input_utilisateur)
            assert nb_player >= 2
            break

        except ValueError:
            print("Erreur: Ce n'est pas un nombre\n")

        except AssertionError:
            print("Le nombre doit être supérieur ou égal à 2\n")
    clear()

    nb_to_send = str(nb_player)
    player_queue.put(nb_to_send)
    

    state = multiprocessing.Array('i', range(nb_player))
    state[:] = [0] * nb_player
    state[0] = 1

    key = 112

    mq = sysv_ipc.MessageQueue(key,sysv_ipc.IPC_CREAT)

    information_send = multiprocessing.Array('i', [0] * nb_player)

    
    newstdin_grandchild = os.fdopen(os.dup(sys.stdin.fileno()))

    processes = [multiprocessing.Process(target=player, args=(i, state,nb_player,child_conn,newstdin_grandchild,card_drop_queue,information_send,mq,shared_memory,shared_memory2)) for i in range(nb_player)]


    for process in processes:
        process.start()


    for process in processes:
        process.join()

    
    thread_communication.join()



if __name__ == "__main__":
    main()