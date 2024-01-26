import socket
from multiprocessing import shared_memory
import numpy as np

def main(liste):
    HOST = "localhost"
    PORT = 6669

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(3)
    client_socket, address = server_socket.accept()

    a = np.array(liste)
    shm = shared_memory.SharedMemory(name='MyMemory', create=True, size=a.nbytes)
    shared_array = np.ndarray(a.shape, dtype=a.dtype, buffer=shm.buf)
    shared_array[:] = a[:]

    mess = shm.name
    print(mess)
    print("Tableau partagé (BEG) : ", shared_array)

    client_socket.sendall(mess.encode())
    conf = client_socket.recv(1024).decode()

    # Send signal to client indicating that the server has finished using the shared memory
    client_socket.sendall("DONE".encode())

    # Wait for acknowledgment from client
    acknowledgment = client_socket.recv(1024).decode()
    print("Acknowledgment from client:", acknowledgment)

    del shared_array
    server_socket.close()
    shm.close()
    shm.unlink()

    
