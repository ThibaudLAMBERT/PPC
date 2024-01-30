import threading
import socket
import queue
import multiprocessing
import time
import os
import sys
import ast
import sysv_ipc
import signal


###DECORATION

#couleurs
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

#liste couleurs, en string et avec les variables
liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "gris", "marron", "turquoise", "rose"]
liste_rgb = [rouge, bleu, vert, jaune, orange, violet, gris, marron, turquoise, rose]

##impression carte vide pour les piles vides
def pile_vide(couleur):
    print(f"{couleur}█████████")
    print("█       █")
    print("█ vide  █")
    print("█       █")
    print(f"{couleur}█████████", end=" ")
    print()
    
##tranforme une liste de liste avec des string, en variable (enleve les guillemets)
def transformer(liste):
    return [[sous_liste[0], eval(sous_liste[1].strip('"'))] for sous_liste in liste]

#clear terminal
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

#impression d'une carte unique, elle transforme la carte unique 
# en liste de liste qui peut etre placee en argument de print_main
def print_carte(carte):
    liste=[]
    liste.append(carte)
    print_main(transformer(liste))

#impression des mains des joueurs
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

#impression du logo
def logo():
    print(f"{vert}  _    _                   _     _ " )
    print(" | |  | |                 | |   (_)    ")
    print(" | |__| | __ _ _ __   __ _| |__  _ ___ ")
    print(" |  __  |/ _` | '_ \ / _` | '_ \| / __|")
    print(" | |  | | (_| | | | | (_| | |_) | \__ \ ")
    print(" |_|  |_|\__,_|_| |_|\__,_|_.__/|_|___/")




##CORPS DU CODE

#initiation d'un boolen globale pour supprimer le thread communication à la fin
game = True


#communication d'information avec le process Game
def comm(data,client_socket):
    client_socket.sendall(data)


#attente des cartes du process Game et renvoit aux process enfants des joueurs
def send_card(pipe,client_socket):
    cartes = client_socket.recv(1024)
    new_cartes = cartes.decode()
    list_mains = ast.literal_eval(new_cartes)
    pipe.send(list_mains)
    return list_mains


#attente d'une action des joueurs
def wait_for_player(choix_player):
    choix_player = choix_player.get()
    return choix_player
        

#thread communication
def communication(number_queue,pipe,choix_player):
    global game
    #connexion au socket
    HOST = "localhost"
    PORT = 6700
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        wait = client_socket.recv(1024) #attente d'un message pour verifier la connexion au socket
        pid = os.getpid()
        str_pid = str(pid)
        number_queue.put("START") #Signalement au process Player de demander le nombre de joueurs
        time.sleep(0.5)
        nb_player = number_queue.get() #récupération du nombre de joueur
        client_socket.sendall(nb_player.encode()) #envoie du pid au process Game
        client_socket.sendall(str_pid.encode()) # envoi du nombre de joueur au process Game
        last_list_mains = send_card(pipe,client_socket) #récupération et envoie des cartes aux enfants
        while game: #boucle du jeu
            requete_player = wait_for_player(choix_player) #attente de la reqête du joueur
            if requete_player[0] == 1: #si il a posé une carte
                string_requete_player = str(requete_player)
                comm(string_requete_player.encode(),client_socket) #envoie de la reqête au process Game
                time.sleep(0.75)
                if game == False: #si le booleen global est pasé à faux, suppresion du thread
                    sys.exit()
                send_card(pipe,client_socket) #récupération et envoie des nouvelles cartes
            elif requete_player[0] == 2: #si il a utilisé un token d'information
                string_requete_player = str(requete_player)
                comm(string_requete_player.encode(), client_socket) #envoie de la reqête au process Game
                send_card(pipe,client_socket) #attente et renvoie des cartes aux enfants


#fonction de gestion d'erreur permettant de gérer les différents input 
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


#handler des process enfants pour les supprimer 
def process_handler(sig, frame):
    if sig == signal.SIGUSR1: 
        sys.exit()
        
#process enfant pour chaque joueur
def player(i, state,state_lock,nb_player,pipe,newstdin_grandchild,choix_player,information_send,information_send_lock,mq,mq_lock,shared_memory,shared_memory2,couleur_compteur):
    signal.signal(signal.SIGUSR1,process_handler) #mise en attente du signal
    liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "gris", "marron", "turquoise", "rose"] #initialisation des couleurs du jeu
    liste_couleurs = liste_couleurs[:nb_player] #réduction des couleurs pour le nombre de joueurs
    #couleur pour l'affichage 
    liste_rgb = [rouge, bleu, vert, jaune, orange, violet, gris, marron, turquoise, rose] 
    liste_rgb = liste_rgb[:nb_player]
    
    liste_info = [] #liste contenant les informations que possède chaque joueur
    while game: #boucle de la partie
        #récupération des informations
        if information_send[i] == 1: 
                with mq_lock: #lock de la messageQueue
                    message , _ = mq.receive(i) #récupération de l'information
                    liste_info.append(message.decode()) #ajout de l'information à la liste des informations
                with information_send_lock: #utilisations d'un lock pour modifier le array partagé
                    information_send[i] = 0
        if state[i] == 1: #verification du joueur qui doit jouer
            #affichage des informations
            logo()
            color=liste_rgb[i]
            print(f"{color}")
            print(f"Le Player {i+1} va jouer ")
            time.sleep(2)
            print(f"{blanc}")
            print(f"Vous avez {shared_memory[0]} informations token")
            print(f"Il reste {shared_memory[1]} fuse token")
            print("Voici les piles en cours : ")
            print(f"{color}")
            for indice_pile in range(nb_player):
                print(f"{eval(liste_couleurs[indice_pile])}")
                print(f"Couleur {liste_couleurs[indice_pile]} : ")
                if shared_memory2[indice_pile] == 0:
                    pile_vide(liste_rgb[indice_pile])
                    print(f"{color}")
                else: 
                    print_carte([shared_memory2[indice_pile], liste_couleurs[indice_pile]])
                    print(f"{color}")
            if liste_info != []:
                print(f"{blanc}")
                print (f"Voici les informations que tu as : {liste_info} ")
            print()

            with state_lock:
                state[i] = 0 #modification de l'état du joueur à 0 pour pas qu'il rejoue
            
            while pipe.poll():
                list_mains = pipe.recv() #récupération des dernières cartes

            #affichage des cartes
            for joueur_index in range(nb_player):
                if joueur_index != i:
                    print(f"{blanc}Main du joueur {joueur_index + 1}")
                    print_main(transformer(list_mains[joueur_index]))
                    print(f"{color}")
                    print()

            sys.stdin = newstdin_grandchild #redirection d'entrée standard pour faire des input
            if shared_memory[0] > 0: #verification si il reste des tokens d'informations
                print(f"{blanc}")
                choix = gestion_erreur("Tapez 1 pour poser une carte, tapez 2 pour utiliser un jeton d'information : ",1)
                if choix == 1: #demande au joueur ce qu'il souhaite faire
                    print("Vous avez choisis de poser une carte")
            else:
                print("Vous n'avez plus de token d'information, vous êtes obliger de poser une carte !")
                choix = 1
            if choix == 1: #si il a choisis de posé une carte
                sys.stdin = newstdin_grandchild #redirection d'entrée standard pour faire des input
                choix2 = gestion_erreur("Quelle carte voulez vous poser, donnez l'indice : ",2,nb_player=None,current_player=i,color_liste=None,list_mains=list_mains)
                print("Vous avez choisis de poser cette carte")
                print_carte(list_mains[i][choix2-1]) #affichage de la carte posé
                choix_player.put([1,i, choix2-1]) #envoie au thread communication via une multiprocessing.queue
                print(f"{color}") 
                
            elif choix == 2: #si il a choisis d'utiliser un token d'information
                print("Vous avez choisis d'utiliser un token d'information")

                if nb_player == 2: #si il n'y a que deux joueurs, envoie que à l'autre joueur
                    print(f"Vous ne pouvez informer que le joueur {((i+1) % nb_player)+1}")
                    choix2 = ((i+1) % nb_player)+1

                else: #demande à quel joueur veut il envoyer l'information
                    choix2 = gestion_erreur("Donnez le numero du joueur : ",3,nb_player,i)

                    print(f"Vous aves choisis d'informer le joueur {choix2}")

                choix_player.put([2,i]) #envoie du choix au thread communication via la multiprocessing.queue

                choix3 = gestion_erreur("Tapez 1 pour indiquer les cartes d'un certain nombre, tapez 2 pour indiquer les cartes d'un certaine couleur : ", 1)
                        
                if choix3 == 1: #si il a décidé d'indiquer un chiffre
                    print("Vous avez choisis d'indiquer les cartes d'un certain nombre")
                    choix4 = gestion_erreur("Quel nombre voulez vous indiquer : ", 5)
                    current_index = 1
                    index = []
                    compteur = 0
                    #parcours de la liste des cartes du joueurs pour récupérer les informations
                    for c in list_mains[choix2-1]:
                        if c[0] == choix4:
                            index.append(current_index)
                            compteur += 1
                        current_index += 1

                    message = f"Tu as {compteur} chiffre(s) {choix4} aux index {index}" #message de l'information
                    mq.send(message.encode(),type=choix2) #envoie du message avec la message queue en mettant le type pour le joueur
                    with information_send_lock:
                        information_send[choix2-1] = 1 #modification de l'array pour que le joueur concerné récupère l'information
                    


                    print()

                elif choix3 == 2: #si il a décidé d'indiquer une couleur
                    print("Vous avez choisis d'indiquer les cartes d'une certaine couleur")
                    choix4 = gestion_erreur(f"Quel couleur voulez vous choisir parmis cette liste : {liste_couleurs} ", 4,color_liste=liste_couleurs)
                    index = []
                    compteur = 0
                    current_index = 1
                    #parcours de la liste des cartes du joueurs pour récupérer les informations
                    for c in list_mains[choix2-1]:
                        if c[1] == choix4.lower():
                            index.append(current_index)
                            compteur += 1
                        current_index += 1

                    choix4_lower = choix4.lower()

                    message = f"Tu as {compteur} {choix4_lower} aux index {index}" #message de l'information
                    mq.send(message.encode(),type=choix2) #envoie du message avec la message queue en mettant le type pour le joueur
                    with information_send_lock:
                        information_send[choix2-1] = 1 #modification de l'array pour que le joueur concerné récupère l'information


                    print()


            #affichage de fin de tour
            print(f"Le Player {i+1} a fini de jouer")
            print("Au tour du joueur suivant dans")
            time.sleep(1)
            print("3")
            time.sleep(1)
            print("2")      
            time.sleep(1)
            print("1")
            time.sleep(1)
            
            clear()
            player_suivant = (i+1) % nb_player #récupère l'index du joueur suivant
            with state_lock:
                state[player_suivant] = 1 #changement de l'array contenant le joueur qui peut jouer


#handler du process pour le supprimer 
def handler(sig,frame,processes,mq):
    global game
    if sig == signal.SIGUSR1:
        for process in processes: #envoie d'un signal aux enfants pour les supprimer
            os.kill(process.pid, signal.SIGUSR1)
        game = False #passage de la variable globale game à False pour supprimer le thread secondaire
        mq.remove() #supression de la message queue
        sys.exit() #exit du programme
    

#process principal
def main(index, shared_memory,newstdin,shared_memory2):
    clear()
    logo()
    print() #affichage 
   
    player_queue = queue.Queue() #création de la queue.Queue pour communiquer le nombre de joueurs
    
    parent_conn, child_conn = multiprocessing.Pipe() #création de la pipe pour la communication du thread cmmunication avec les joueurs

    choix_player = multiprocessing.Queue() #création de la queue pour la communication du thread communication avec les joueurs 
    thread_communication = threading.Thread(target=communication,args=(player_queue,parent_conn,choix_player)) #création du thread communication
    thread_communication.start() #démarrage du thread comunication

    player_queue.get() #attente du signal du thread communication
    sys.stdin = newstdin #redirection d'entrée standard pour input
    while True: #demande du nombre de joueur à l'utilisateur avec gestion des erreurs
        try:
            input_utilisateur = input("Entrez un nombre de joueurs: ")
            nb_player = int(input_utilisateur)
            assert nb_player >= 2 and nb_player < 10
            break

        except ValueError:
            print("Erreur: Ce n'est pas un nombre\n")

        except AssertionError:
            print("Le nombre doit être supérieur ou égal à 2 et inférieur ou égal à 9 \n")
    clear()

    nb_to_send = str(nb_player)
    player_queue.put(nb_to_send) #envoie du nombre au thread communication
    

    state = multiprocessing.Array('i', range(nb_player)) #création de l'array partagé pour l'état des joueurs
    state[:] = [0] * nb_player #initialisation des états à 0 (personne ne joue)
    state[0] = 1 #modification de l'état du joueur 1 à 1, pour qu'il joue
    state_lock = multiprocessing.Lock() #création d'un Lock pour controler la modification de cet array

    #création de la message queeu
    key = 112

    mq = sysv_ipc.MessageQueue(key,sysv_ipc.IPC_CREAT)
    mq_lock = multiprocessing.Lock() #création d'un verrou pour controler l'accès à la message queue


    information_send = multiprocessing.Array('i', [0] * nb_player) #création d'un array partagé pour les informations des joueurs
    information_send_lock = multiprocessing.Lock() #création d'un verrou pour controler la modification de cet array
    
    newstdin_grandchild = os.fdopen(os.dup(sys.stdin.fileno())) #création de la redirection d'entrée standard
    couleur_compteur=0
    #création des process pour chaque joueur
    processes = [multiprocessing.Process(target=player, args=(i, state,state_lock,nb_player,child_conn,newstdin_grandchild,choix_player,information_send,information_send_lock,mq,mq_lock,shared_memory,shared_memory2,couleur_compteur)) for i in range(nb_player)]

    #démarrage des process enfants
    for process in processes:
        process.start()

    #attente d'un signal pour la fin de partie
    signal.signal(signal.SIGUSR1, lambda sig, frame: handler(sig, frame, processes,mq))
    
    #attente des process enfants
    for process in processes:
        process.join()

    #attente du thread
    thread_communication.join()



if __name__ == "__main__":
    main()