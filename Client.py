import socket

# Client settings
broadcast_port = 13117
bufferSize = 1024

# Create a UDP socket at client side
udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

# Not sure if needed, enable to be re-used?
# udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Enable broadcasting mode
udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Connect to the broadcasting port
udp_client_socket.bind(("", broadcast_port))

looking_for_a_server = True

while looking_for_a_server:
    offer_message, offer_address = udp_client_socket.recvfrom(bufferSize)
    print("received offer message: %s" % offer_message)
    print("received offer address: %s" % offer_address)

