import socket
import struct
# Client settings
group_name = "Team 2"
broadcast_port = 13117
bufferSize = 1024

# Create a UDP socket at client side
udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

# Not sure if needed, enable to be re-used?
udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Enable broadcasting mode
udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Connect to the broadcasting port
udp_client_socket.bind(("", broadcast_port))
print("Client started, listening for offer requests...")

offer_message, offer_address = udp_client_socket.recvfrom(bufferSize)
udp_client_socket.close()
print (f"Received offer from {offer_address}, attempting to connect...")
magic_cookie_message_type_server_port_unpacked = struct.unpack('!IBH', offer_message)

# print(hex(magic_cookie_message_type_server_port_unpacked[0]))
# print(hex(magic_cookie_message_type_server_port_unpacked[1]))
# print(magic_cookie_message_type_server_port_unpacked[2])
server_port = magic_cookie_message_type_server_port_unpacked[2]

print(f"{offer_address}, {server_port}")
# TCP Client Side:
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((offer_address[0], server_port))

clientSocket.send(f"{group_name}\n".encode())

start_game_message_from_server = clientSocket.recv(1024).decode()

print(start_game_message_from_server)

# print("Waiting for answer: ")
try:
    import getch

    player_answer = getch.getch()
except ImportError:
    import msvcrt

    player_answer = msvcrt.getch()

print(player_answer.decode())

player_answer = msvcrt.getch()  # getch.getch()
# print(player_answer)

clientSocket.send(player_answer)

# Finish playing the game

end_game_message_from_server = clientSocket.recv(1024).decode()
print(end_game_message_from_server)


# looking_for_a_server = True
#
# while looking_for_a_server:
#     offer_message, offer_address = udp_client_socket.recvfrom(bufferSize)
#     print("received offer message: %s" % offer_message)
#     print("received offer address: %s" % offer_address)

