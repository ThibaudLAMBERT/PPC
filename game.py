import threading
import socket


def communication_player(data):
    import socket
 
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    import socket
 
    HOST = "localhost"
    PORT = 6667
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        with client_socket:
            print("Connected to client: ", address)
            client_socket.sendall(data.encode())
            nb_player = int(client_socket.recv(1024).decode())
            print(nb_player)
            



if __name__ == "__main__":
    print("Game is ready, sending ack to player")
    communication_player("Game is ready, sending ack to player")
