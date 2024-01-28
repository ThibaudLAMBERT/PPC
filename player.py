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
import signal

RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
BLACK = "\033[30m"
rouge = "\033[31m"
vert = "\033[32m"
jaune = "\033[33m"
bleu = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
blanc = "\033[37m"
violet = "\033[95m"
orange = "\033[33;91m"
rose = "\033[95m"
gris = "\033[90m"
marron = "\033[31;33m"
turquoise = "\033[36m"

def pile_vide(couleur):
    
    print(f"{blanc}█████████")
    print("█       █")
    print("█ vide  █")
    print("█       █")
    print(f"{blanc}█████████", end=" ")
    print()
liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "rose", "gris", "marron", "turquoise"]

liste_rgb = [rouge, bleu, vert, jaune, orange, violet, rose, gris, marron, turquoise]

def transformer(liste):
    return [[sous_liste[0], eval(sous_liste[1].strip('"'))] for sous_liste in liste]



game = True


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_carte(carte):
    
    liste=[]
    liste.append(carte)
    print_main(transformer(liste))
        
def print_main(mains):
    
    for _ in range(2):
        for carte in mains:
            print(f"{carte[1]}█████████", end="  ")
        print()     
    for carte in mains:
            print(f"{carte[1]}",end="")
            print(f"████{carte[0]}████", end="  ")
    print()
    for _ in range(2):
        for carte in mains:
            print(f"{carte[1]}█████████", end="  ")
        print()
    
    


def logo():
    print(f"{vert}  _    _                   _     _ " )
    print(" | |  | |                 | |   (_)    ")
    print(" | |__| | __ _ _ __   __ _| |__  _ ___ ")
    print(" |  __  |/ _` | '_ \ / _` | '_ \| / __|")
    print(" | |  | | (_| | | | | (_| | |_) | \__ \ ")
    print(" |_|  |_|\__,_|_| |_|\__,_|_.__/|_|___/")



def comm(data,client_socket):
    client_socket.sendall(data)


def send_card(pipe,client_socket):
    cartes = client_socket.recv(1024)
    new_cartes = cartes.decode()
    list_mains = ast.literal_eval(new_cartes)
    pipe.send(list_mains)
    return list_mains



def wait_for_player(card_drop_queue):
    card_drop = card_drop_queue.get()
    return card_drop
        



def communication(number_queue,pipe,carte_drop_queue):
    global game
    HOST = "localhost"
    PORT = 6700
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        wait = client_socket.recv(1024)
        pid = os.getpid()
        str_pid = str(pid)
        number_queue.put("START")
        time.sleep(0.5)
        nb_player = number_queue.get()
    
        client_socket.sendall(nb_player.encode())
        client_socket.sendall(str_pid.encode())







        last_list_mains = send_card(pipe,client_socket)
        while game:
            requete_player = wait_for_player(carte_drop_queue)
            if requete_player[0] == 1:
                string_requete_player = str(requete_player)
                comm(string_requete_player.encode(),client_socket)
                time.sleep(0.75)
                if game == False:
                    sys.exit()
                send_card(pipe,client_socket)
                

            elif requete_player[0] == 2:
                string_requete_player = str(requete_player)
                comm(string_requete_player.encode(), client_socket)
                send_card(pipe,client_socket)








def gestion_erreur(message,choix,nb_player=None,current_player=None,color_liste=None,list_mains=[]):
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
                assert 0 < user_input <= 5
                if list_mains[current_player][user_input-1] == ["/","blanc"]:
                    raise IndexError
                break

            except ValueError:
                print("Erreur: Ce n'est pas un nombre\n")

            except AssertionError:
                print("Le nombre doit être entre 1 et 5\n")

            except IndexError:
                print("Vous n'avez plus de carte à cet emplacement")

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
    
    elif choix == 5:
        while True: 
            try:
                reponse = input(message)
                user_input = int(reponse)
                assert 0 < user_input <= 5
                break

            except ValueError:
                print("Erreur: Ce n'est pas un nombre\n")

            except AssertionError:
                print("Le nombre doit être entre 1 et 5\n")

        return user_input



def process_handler(sig, frame):
    if sig == signal.SIGUSR1:
        sys.exit()
        


def player(i, state,nb_player,pipe,newstdin_grandchild,carte_drop_queue,information_send,mq,shared_memory,shared_memory2,couleur_compteur):
    
    signal.signal(signal.SIGUSR1,process_handler)
    
    liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "rose", "gris", "marron", "turquoise"]
    liste_couleurs = liste_couleurs[:nb_player]
    liste_rgb = [rouge, bleu, vert, jaune, orange, violet, rose, gris, marron, turquoise]
    liste_rgb = liste_rgb[:nb_player]
    
    
    
    
    
    
    liste_info = []
    while game:
        if information_send[i] == 1:
            message , _ = mq.receive(i)
            liste_info.append(message.decode())
            information_send[i] = 0


        if state[i] == 1:
            color=liste_rgb[i]
            print(f"{color}")
            print(f"Le Player {i+1} va jouer ")
            time.sleep(2)

            print(f"Vous avez {shared_memory[0]} informations token")
            print(f"Il reste {shared_memory[1]} fuse token")
            print("Voici les piles en cours : ")



            for indice_pile in range(nb_player):
                print(f"Couleur {liste_couleurs[indice_pile]} : ")
                if shared_memory2[indice_pile] == 0:
                    pile_vide(liste_rgb[indice_pile])
                    print(f"{color}")
                else: 
                    print_carte([shared_memory2[indice_pile], liste_couleurs[indice_pile]])
                    print(f"{color}")

            if liste_info != []:
                print (f"Voici les informations que tu as : {liste_info} ")

            print()
            state[i] = 0
            
            while pipe.poll():
                list_mains = pipe.recv()




            for joueur_index in range(nb_player):
                if joueur_index != i:
                    print(f"{blanc}Main du joueur {joueur_index + 1}")
                    print_main(transformer(list_mains[joueur_index]))
                    print(f"{color}")
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
                choix2 = gestion_erreur("Quelle carte voulez vous jeter, donnez l'indice : ",2,nb_player=None,current_player=i,color_liste=None,list_mains=list_mains)
                print("Vous avez choisis de jeter la carte")
                print_carte(list_mains[i][choix2-1])
                carte_drop_queue.put([1,i, choix2-1])
                print(f"{color}")
                
            elif choix == 2:
                print("Vous avez choisis d'utiliser un token d'information")

                if nb_player == 2:
                    print(f"Vous ne pouvez informer que le joueur {((i+1) % nb_player)+1}")
                    choix2 = ((i+1) % nb_player)+1

                else:
                    choix2 = gestion_erreur("Donnez le numero du joueur : ",3,nb_player,i)

                    print(f"Vous aves choisis d'informer le joueur {choix2}")

                carte_drop_queue.put([2,i])

                choix3 = gestion_erreur("Tapez 1 pour indiquer les cartes d'un certain nombre, tapez 2 pour indiquer les cartes d'un certaine couleur : ", 1)
                        
                if choix3 == 1:
                    print("Vous avez choisis d'indiquer les cartes d'un certain nombre")
                    choix4 = gestion_erreur("Quel nombre voulez vous indiquer : ", 5)
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
            clear()
            player_suivant = (i+1) % nb_player
            state[player_suivant] = 1


def handler(sig,frame,processes,mq):
    global game
    if sig == signal.SIGUSR1:
        for process in processes:
            os.kill(process.pid, signal.SIGUSR1)
        game = False
        mq.remove()
        sys.exit()
    


def main(index, shared_memory,newstdin,shared_memory2):
    clear()
    logo()
    print()
    



    
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
    couleur_compteur=0
    processes = [multiprocessing.Process(target=player, args=(i, state,nb_player,child_conn,newstdin_grandchild,card_drop_queue,information_send,mq,shared_memory,shared_memory2,couleur_compteur)) for i in range(nb_player)]


    for process in processes:
        process.start()


    signal.signal(signal.SIGUSR1, lambda sig, frame: handler(sig, frame, processes,mq))
    

    for process in processes:
        process.join()

    
    thread_communication.join()



if __name__ == "__main__":
    main()