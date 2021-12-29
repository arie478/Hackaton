import operator
import queue
import random
import socket
import struct
import time
import threading
import scapy.all as scapy

# function called in by thread, broadcasts the message it got to all the Ip addresses in the port
def broadcast_offering(offer_message):
    # Generate a list of all IP addresses in the port
    server_ip = socket.gethostbyname(socket.gethostname())
    ip_prefix = server_ip[:server_ip.rfind('.') + 1]
    ip_ranges = ['{}{}'.format(ip_prefix, ip_num) for ip_num in range(0, 256)]

    # Broadcast while we search for players
    while waiting_for_clients:
        for ip in ip_ranges:
            # Create a datagram socket
            udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

            # Not sure if needed, enable to be re-used?
            udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Enable broadcasting mode
            udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            udp_server_socket.sendto(offer_message, (ip, broadcast_port))
            #print("Offer sent in broadcast!", flush=True)
            udp_server_socket.close()
        # Broadcast offer every 1 second
        time.sleep(1)

# function called in by thread to get the client number's name from his connection socket
def ask_for_name(client_socket, client_num):
    # Try to get the client's name from his socket
    try:
        name = client_socket.recv(1024).decode()
    except:
        name = "Disconnected"
    # Put the client's name along with his number in the queue
    names_from_teams.put((client_num, name))

# function called in by timbered thread
def call_draw():
    # Puts -1 in the queue
    # We later know that if we got -1 its a draw
    answer_queue.put((-1, str(0).encode()))

# function called in thread, gets the players number and his connection socket
def playing_with_player(client_socket, player_number):
    # Try to get an answer from the player
    try:
        answer_from_client = client_socket.recv(1024)
    except:
        answer_from_client = -1
    # And save it in the queue
    answer_queue.put((player_number, answer_from_client))


# Server settings

# For Windows
server_ip = socket.gethostbyname(socket.getfqdn())
# alternative: socket.gethostbyname(socket.gethostname()) #local

# For Linux
# server_ip = scapy.get_if_addr('eth1')

local_port = 2017
broadcast_port = 13117
while True:
    try:
        # Create a stream socket
        tcp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to address and ip
        tcp_server_socket.bind((server_ip, local_port))

        waiting_for_clients = True

        # Make the offer message
        # I = unsigned long(4) b = unsigned char(1) H = unsigned int(2)
        magic_cookie_message_type_server_port_packed = struct.pack('!IbH', int('0xabcddcba', 16), int('0x2', 16), local_port)

        print("“Server started, listening on IP address " + server_ip)

        client_count = 0

        # Broadcasting the offer
        broadcast_thread = threading.Thread(name="Broadcast_thread", target=broadcast_offering,
                                            args=(magic_cookie_message_type_server_port_packed,), daemon=True)
        broadcast_thread.start()

        # Initialize parameters needed to supervise the game
        client_ip_addresses = [None] * 2
        client_sockets = [None] * 2
        client_names = [None] * 2
        names_from_teams = queue.Queue()
        tcp_server_socket.listen()

        # While we don't have 2 clients, wait to accept cliens
        while client_count < 2:
            print("Waiting for request..")
            client_sockets[client_count], client_ip_addresses[client_count] = tcp_server_socket.accept()
            print("request eccepted")
            ask_name = threading.Thread(name="name_asker_thread", target=ask_for_name,
                                        args=(client_sockets[client_count], client_count))
            ask_name.start()
            ask_name.join()
            client_count += 1

        # Broadcast has stopped and no need for welcoming socket anymore:
        waiting_for_clients = False
        tcp_server_socket.close()

        print("got two players, asking for names:")

        (first_client_num, first_team_name) = names_from_teams.get(block=True, timeout=None)
        print("Got player 0 :")
        print((first_client_num, first_team_name))
        (second_client_num, second_team_name) = names_from_teams.get(block=True, timeout=None)
        print("Got player 1 :")
        print((second_client_num, second_team_name))
        client_names[first_client_num], client_names[second_client_num] = first_team_name, second_team_name

        # Now we have 2 clients! We are ready to start the game in 10 seconds
        time.sleep(10)

        print("game_started")


        # The equation generator
        # Makes sure first(operation)second is always between 0-9 for one digit answer
        operator_type = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv}
        first_number = random.randint(0, 9)
        operator_chosen = random.choice(list(operator_type.keys()))

        if operator_chosen == '+':
            second_number = random.randint(0, 9 - first_number)

        elif operator_chosen == '-':
            second_number = random.randint(0, first_number)

        elif operator_chosen == '*':
            if first_number >= 5:
                second_number = 1
            elif first_number >= 2:
                second_number = random.randint(0, 6 - first_number)
            else:
                second_number = random.randint(0, 9)

        else:  # operator_chosen == '/':
            divisors = {9: [9, 3, 1], 8: [8, 4, 2, 1], 7: [7, 1], 6: [6, 3, 2, 1], 5: [5, 1], 4: [4, 2, 1], 3: [3, 1],
                        2: [2, 1], 1: [1], 0: [9, 8, 7, 6, 5, 4, 3, 2, 1]}
            second_number = random.choice(divisors[first_number])

        true_answer = int(operator_type.get(operator_chosen)(first_number, second_number))

        game_begin_message_from_server = f"Whlcome to Quick Maths.\n" \
                                         f"Player 1: {client_names[0]}" \
                                         f"Player 2: {client_names[1]}" \
                                         f"==\n" \
                                         f"Please answer the following question as fast as you can:\n" \
                                         f"How much is {first_number}{operator_chosen}{second_number}?".encode()

        # Send the game message to both players
        client_sockets[0].send(game_begin_message_from_server)
        client_sockets[1].send(game_begin_message_from_server)

        answer_queue = queue.Queue()

        # Make the 2 player threads and the draw thread
        timer = threading.Timer(10, call_draw)
        player_0 = threading.Thread(name="player_0_player_thread", target=playing_with_player,
                                    args=(client_sockets[0], 0))
        player_1 = threading.Thread(name="player_1_player_thread", target=playing_with_player,
                                    args=(client_sockets[1], 1))

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

        #Cancel timer if still going since we got answer
        timer.cancel()

        # Get the answer from the player and check if its valid
        player_num = player_num_and_answer[0]
        try:
            answer = int(player_num_and_answer[1].decode())
        except ValueError:
            answer = -1

        # Check if answer is right or wrong and change winner
        if player_num == 0 and answer != true_answer:
            #Player 0 did wrong, 1 is winner
            player_num = 1
        elif player_num == 1 and answer != true_answer:
            #Player 1 did wrong, 0 is winner
            player_num = 0

        # Game over, check for winner
        # if player_num == 0, player 0 won
        # if player_num == 1, player 1 won
        # if player_num == -1, draw since time run out

        # Construct the 'END GAME' message:
        game_over_message = f"Game Over!\n" \
                            f"The correct answer was {true_answer}!\n"
        if player_num == 0:
            game_over_message += f"Congratulations to the winner: {client_names[0]}"
        elif player_num == 1:
            game_over_message += f"Congratulations to the winner: {client_names[1]}"
        elif player_num == -1:
            game_over_message += "It is a draw since no one gave an answer within the time limit!"

        print(game_over_message)
        # server sends the 'END GAME' message two the two players:
        client_sockets[0].send(game_over_message.encode())
        client_sockets[1].send(game_over_message.encode())

        client_sockets[0].close()
        client_sockets[1].close()

        # Reset the game and loop again
        print("Game over, sending out offer requests...")

    except BaseException as err:
        print(err)
        continue
