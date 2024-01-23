import threading
import socket

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

    
    deck =[[1, 2, 2, 3, 3, 4, 4, 5]]* nb_players
    for i in range (nb_players):
        print ("cartes")
        print (liste_couleurs[i])
        print(deck[i])
    return deck
    



if __name__ == "__main__":
    print("Game is ready, sending ack to player")
    nb_players=communication_player("Game is ready, sending ack to player")
    print(nb_players)


    deck=deck_init(nb_players)
    
    couleurs_en_jeu=liste_couleurs[:nb_players]

    
    
    
    

    while True:
        a=0
