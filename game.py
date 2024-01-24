
import threading
import socket
import random

liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "rose", "gris", "marron", "turquoise"]



import socket


def comm(data, initialisation=False):
    if initialisation:
        global my_socket
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        HOST = "localhost"
        PORT = 6700
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen(1)
            
            global client_socket
            client_socket, address = server_socket.accept()
            
            print("Connected to client: ", address)
            client_socket.sendall(data.encode())
            nb_player = int(client_socket.recv(1024).decode())
            
            return nb_player, client_socket
    else:
        try:
            client_socket.sendall(data.encode())
        except NameError:
            print("Le socket client n'est pas initialisé. Appelez la fonction avec initialisation=True au moins une fois.")



#initilisation du deck
def deck_init(nb_players):
    deck =[[1, 2, 2, 3, 3, 4, 4, 5]for _ in range(nb_players)]
    return deck
    
def tirage_carte(deck):
    couleur_index=random.randint(0,len(deck)-1)
    carte_index=random.randint(0,len(deck[couleur_index])-1)
    couleur=liste_couleurs[couleur_index]
    carte=deck[couleur_index][carte_index]
    deck[couleur_index].pop(carte_index)
    return(couleur_index, couleur, carte)
    

def main():
    print("Game is ready, sending ack to player")
    nb_players, client_sock = comm("Hello, initialize!", initialisation=True)
    print("Number of players:", nb_players)
    deck=deck_init(nb_players)
    
    
    couleurs_en_jeu=liste_couleurs[:nb_players]


    comm("Hello from main!")

    for i in range (nb_players):
        print("cartes joueur numero")
        print(i)
        for _ in range (5):
            
            print(str(tirage_carte(deck)))

    while True:
        a=0



if __name__ == "__main__":
    main()