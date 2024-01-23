import threading
import socket

def communication():
    HOST = "localhost"
    PORT = 6666
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        print("ATTENTE DU SERVER")
        wait = client_socket.recv(1024)
        print("Recu")
        value = int(input("Y'a combien de joueur ? "))
        client_socket.sendall(value.encode())
        print("NOMBRE ENVOYE")



if __name__ == "__main__":
    thread_communication = threading.Thread(target=communication)
    thread_communication.start()
    thread_communication.join()
