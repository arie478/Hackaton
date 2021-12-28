import multiprocessing
import socket
import struct
import sys
import time
from multiprocessing import Process
from select import select


def kbhit():
    dr, dw, de = select([sys.stdin], [], [], 0)
    return dr != []

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

            # Check if the packet is in the proper format :
            # Magic cookie [0:4] = 0xabcddcba
            # m_type [4] = 0x2
            # if not (offer_message[:4] == bytes([0xab, 0xcd, 0xdc, 0xba])) or not (offer_message[4] == 0x2):
            #     exit(0)
            #     # Not an offer message, drop and try again
            #     # continue

            offer_ip = offer_address[0]

            print(f"Received offer from {offer_ip}, attempting to connect...")

            offer_port = struct.unpack('>H', offer_message[5:7])[0]

            print(f"{offer_ip}, {offer_port}")

            # TCP Client Side:
            group_name = "Test_Client>"
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((offer_ip, offer_port))

            clientSocket.send(f"{group_name}\n".encode())

            start_game_message_from_server = clientSocket.recv(1024).decode()

            print(start_game_message_from_server)

            time_out = time.time() + 10

            # Play the game

            #playing_game_process = Process(target=playing_game, args=(clientSocket,))
            #playing_game_process.start()

            player_answer = ""

            print("Waiting for answer: ")
            try:
                import getch

                while time.time() < time_out:
                    if kbhit():
                        player_answer = getch.getch()
            except ImportError:
                import msvcrt

            while time.time() < time_out:
                try:
                    if msvcrt.kbhit():
                        player_answer = msvcrt.getch()
                        print(player_answer.decode())
                        clientSocket.send(player_answer)
                        print("Answer sent!")

                except BaseException as err:
                    print(err)
                    print("Couldn't send")
                    break

        # Finish playing the game
        except BaseException as err:
            print(err)

        end_game_message_from_server = clientSocket.recv(1024).decode()

        print(end_game_message_from_server)

except BaseException as err:
    print(err)
