import socket
import time
import threading

# Server settings
server_ip = "127.0.0.1"
broadcast_port = 13117

# Create a datagram socket
udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

# Not sure if needed, enable to be re-used?
# udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Enable broadcasting mode
udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Bind to address and ip
# udp_server_socket.bind((server_ip, server_port))

# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
udp_server_socket.settimeout(0.2)

waiting_for_clients = True

# Make the offer message
magic_cookie = b"0xabcddcba"
message_type = b"0x2"
server_port = b"2017"
offer_message = magic_cookie + message_type + server_port

print("“Server started, listening on IP address " + server_ip)

client_count = 0

while waiting_for_clients:

    # Broadcast offer every 1 second
    udp_server_socket.sendto(offer_message, ("localhost", broadcast_port))
    # print("offer sent!", flush=True)
    time.sleep(1)

