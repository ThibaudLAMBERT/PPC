import socket
from multiprocessing import shared_memory
import numpy as np
import time

def main():
    HOST = "localhost"
    PORT = 6669

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        data = str(client_socket.recv(10240).decode())
        print("Nom du la shared memory reçu : ", data)
        existing_shm = shared_memory.SharedMemory(name=data)
        shared_array = np.ndarray((6,), dtype=np.int64, buffer=existing_shm.buf)
        print(shared_array)
        shared_array[2] = 666
        m = "18"
        client_socket.sendall(m.encode())

        # Wait for signal from server indicating that it has finished using the shared memory
        signal = client_socket.recv(1024).decode()
        print("Signal from server:", signal)

        # Acknowledge to the server that the client has received the signal
        client_socket.sendall("ACK".encode())

        del shared_array
        client_socket.close()
        existing_shm.close()
        existing_shm.unlink()

        
      
