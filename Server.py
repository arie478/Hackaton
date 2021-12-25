import operator
import queue
import random
import socket
import struct
import time
import threading


def broadcast_offering(offer_message):
    while waiting_for_clients:
        # Broadcast offer every 1 second
        udp_server_socket.sendto(offer_message, ("localhost", broadcast_port))
        # print(offer_message, flush=True)
        # print("Offer sent in broadcast!", flush=True)
        time.sleep(1)


def call_draw():
    answer_queue.put((-1, 0))


def playing_with_player(client_socket, player_number):
    answer_from_client = client_socket.recv(1024)
    answer_queue.put((player_number, answer_from_client))


# Server settings
# localhost
server_ip = socket.gethostbyname(socket.getfqdn())  # alternative: socket.gethostbyname(socket.gethostname()) #local
# host / "127.0.0.1"
local_port = 2017
broadcast_port = 13117

# Create a datagram socket
udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

# Not sure if needed, enable to be re-used?
# udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Enable broadcasting mode
udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Create a stream socket
tcp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

# Bind to address and ip
# udp_server_socket.bind((server_ip, server_port))
tcp_server_socket.bind((server_ip, local_port))

# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
udp_server_socket.settimeout(0.2)

waiting_for_clients = True

# Make the offer message
# I = unsigned long(4) B = unsigned char(1) H = unsigned int(2)
magic_cookie_message_type_server_port_packed = struct.pack('!IBH', int('0xabcddcba', 16), int('0x2', 16), 2017)

# Test the unpacked message
# magic_cookie_message_type_server_port_unpacked = struct.unpack('!IBH', magic_cookie_message_type_server_port_packed)
# print(hex(magic_cookie_message_type_server_port_unpacked[0]))
# print(hex(magic_cookie_message_type_server_port_unpacked[1]))
# print(magic_cookie_message_type_server_port_unpacked[2])

print("“Server started, listening on IP address " + server_ip)

client_count = 0
# client_count_lock = threading.Lock()

# threading.Thread(target=broadcast_offering, args=(magic_cookie_message_type_server_port_packed,)).start()

client_ip_address = []
client_sockets = []
client_names = ["Instinct", "Rocket"]

# while waiting_for_clients:
#     print("Waiting for request..")
#     tcp_server_socket.listen()
#     client_sockets[client_count], client_ip_address[client_count] = tcp_server_socket.accept()
#     client_sockets[client_count].settimeout(0.2)
#     # Update the client counter
#     # client_count_lock.acquire()
#     client_count += 1
#     if client_count == 2:
#         waiting_for_clients = False
#     # client_count_lock.release()

# Now we have 2 clients! We are ready to start the game

# The equation generator
operator_type = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv}
first_number = random.randint(0, 9)
operator_chosen = random.choice(list(operator_type.keys()))

if operator_chosen == '+':
    #print("add")
    second_number = random.randint(0, 9 - first_number)

elif operator_chosen == '-':
    #print("sub")
    second_number = random.randint(0, first_number)

elif operator_chosen == '*':
    #print("mul")
    if first_number >= 5:
        second_number = 1
    elif first_number >= 2:
        second_number = random.randint(0, 6 - first_number)
    else:
        second_number = random.randint(0, 9)

else:  # operator_chosen == '/':
    #print("div")
    divisors = {9: [9, 3, 1], 8: [8, 4, 2, 1], 7: [7, 1], 6: [6, 3, 2, 1], 5: [5, 1], 4: [4, 2, 1], 3: [3, 1],
                2: [2, 1], 1: [1], 0: [9, 8, 7, 6, 5, 4, 3, 2, 1]}
    second_number = random.choice(divisors[first_number])

true_answer = operator_type.get(operator_chosen)(first_number, second_number)

print("Welcome to Quick Maths.")
print("Player 1: " + client_names[0])
print("Player 2: " + client_names[1])
print("==")
print("Please answer the following question as fast as you can:")
print('How much is {}{}{}?'.format(first_number, operator_chosen, second_number))
print(int(true_answer))

exit(0)

answer_queue = queue.Queue

# Make the 2 player threads and the draw thread
timer = threading.Timer(10, call_draw)
player_0 = threading.Thread(target=playing_with_player, args=(client_sockets[0], 0))
player_1 = threading.Thread(target=playing_with_player, args=(client_sockets[1], 1))

# Set all threads to daemons
player_0.daemon = True
player_1.daemon = True
timer.daemon = True

# Start all the threads
player_0.start()
player_1.start()
timer.start()

# Get the answer from the queue
player_num_and_answer = answer_queue.get(block=True, timeout=None)
timer.cancel()

player_num = player_num_and_answer[0]
answer = player_num_and_answer[1]

# Check if answer is right or wrong and change winner
if player_num == 0 and answer != answer:
    player_num = 1
if player_num == 1 and answer != answer:
    player_num = 0

# Game over, check for winner
# if player_num == 0, player 0 won
# if player_num == 1, player 1 won
# if player_num == -1, draw since time run out

print("Game over!")
print("The correct answer was " + answer + "!")
if player_num == 0:
    print("Congratulations to the winner: " + client_names[0])
if player_num == 1:
    print("Congratulations to the winner: " + client_names[1])
if player_num == -1:
    print("It is a draw since no one gave an answer within the time limit!")

# Reset the game and loop again
