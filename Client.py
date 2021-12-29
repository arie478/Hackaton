import multiprocessing
import socket
import struct
import sys
import threading
import time
from multiprocessing import Process
from select import select


class MyThread (multiprocessing.Process):
    def __init__(self, client_socket):
        super(MyThread, self).__init__()
        self.playing_socket = client_socket

    def run(self):
        # Try get answer from Linux
        try:
            import getch

            player_answer = getch.getch()
            try:
                self.playing_socket.send(player_answer.encode())
            except BaseException as err:
                print(err)
                pass

        # Try get answer from Windows
        except ImportError:
            import msvcrt

            player_answer = msvcrt.getch()
            #print(player_answer.decode())
            try:
                self.playing_socket.send(player_answer)
            except BaseException as err:
                print(err)
                pass
            #print("Answer sent!")


def main():
    try:
        while True:
            try :
                # Client settings
                broadcast_port = 13117
                bufferSize = 1024

                # Create a UDP socket at client side
                udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

                # Enable to be re-used
                udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                # Enable broadcasting mode
                udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

                # Connect to the broadcasting port
                udp_client_socket.bind(("", broadcast_port))
                print("Client started, listening for offer requests...")

                offer_message, offer_address = udp_client_socket.recvfrom(bufferSize)
                udp_client_socket.close()

                magic, message, port = struct.unpack('!IbH', offer_message)
                print(magic, message, port)
                # Check if the packet is in the proper format :
                if not (offer_message[:4] == bytes([0xab, 0xcd, 0xdc, 0xba])) or not (offer_message[4] == 0x2):
                    print("invalid format")
                    # Not an offer message, drop and try again
                    continue

                offer_ip = offer_address[0]

                print(f"Received offer from {offer_ip}, attempting to connect...")

                offer_port = struct.unpack('!H', offer_message[5:7])[0]

                # TCP Client Side:
                group_name = "Testy the test client"
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientSocket.connect((offer_ip, offer_port))

                clientSocket.send(f"{group_name}\n".encode())

                print("Connected, waiting for game to start")
                start_game_message_from_server = clientSocket.recv(1024).decode()

                print(start_game_message_from_server)

                # Play the game

                game_in_progress = True

                playing_game_process = MyThread(clientSocket)
                playing_game_process.start()

            # Finish playing the game
            except BaseException as err:
                continue
                print(err)

            end_game_message_from_server = clientSocket.recv(1024).decode()

            playing_game_process.kill()

            print(end_game_message_from_server)
    except BaseException as err:
        pass
        print(err)


if __name__ == '__main__':
    main()
