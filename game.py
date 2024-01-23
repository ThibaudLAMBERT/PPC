import threading
import socket


def communication_player(data):
    import socket
 
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    import socket
 
    HOST = "localhost"
    PORT = 6666
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        with client_socket:
            print("Connected to client: ", address)
            client_socket.sendall(data.encode)



if __name__ == "__main__":
    print("HANABIS ")
    print("Bienvenue")
    while True:
        try:
            input_utilisateur = input("Entrez un nombre de joueurs: ")
            nombre = int(input_utilisateur)
            break

        except ValueError:
            print("Erreur: Ce n'est pas un nombre\n")

