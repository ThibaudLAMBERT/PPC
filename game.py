import threading
import socket
import random

liste_couleurs= ["rouge", "bleu", "vert", "jaune", "orange", "violet", "rose", "gris", "marron", "turquoise"]

def communication_player(data):
    import socket
 
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    import socket
 
    HOST = "localhost"
    PORT = 6669
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        with client_socket:
            print("Connected to client: ", address)
            client_socket.sendall(data.encode())
            nb_player = int(client_socket.recv(1024).decode())
            
            return(nb_player)

#initilisation du deck
def deck_init(nb_players):

    
    deck =[[1, 2, 2, 3, 3, 4, 4, 5]for _ in range(nb_players)]
    for i in range (nb_players):
        print ("cartes")
        print (liste_couleurs[i])
        print(deck[i])
    return deck
    
def tirage_carte(deck):
    couleur_index=random.randint(0,len(deck)-1)
    carte_index=random.randint(0,len(deck[couleur_index])-1)
    couleur=liste_couleurs[couleur_index]
    carte=deck[couleur_index][carte_index]
    deck[couleur_index].pop(carte_index)
    return(couleur_index, couleur, carte)
    



if __name__ == "__main__":
    print("Game is ready, sending ack to player")
    nb_players=communication_player("Game is ready, sending ack to player")
    print(nb_players)


    deck=deck_init(nb_players)
    
    
    couleurs_en_jeu=liste_couleurs[:nb_players]
    print(deck)
    print(tirage_carte(deck))
    print(deck)


    # for joueur in range (nb_players):
    #     for _ in range (5):
    #         print(tirage_carte(deck))
    #     print("Deck numéro", joueur)
    #     print(deck)

    
    
    
    
    

    while True:
        a=0
