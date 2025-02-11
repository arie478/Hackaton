# PvP Math Game

##  Project Overview

This project was done for a Web Development Environments course for educational purposes.
**PvP Math Game** is a competitive multiplayer math challenge game where two players face off to solve a randomly generated math problem as quickly as possible. The game uses socket programming for communication between the client and server, featuring both TCP and UDP protocols. Players connect to the server via broadcast discovery and compete in real-time to win the game by providing the correct answer first.

---

##  Key Features

###  Multiplayer Math Challenge
- Players compete to answer a math problem (addition, subtraction, multiplication, or division) within a 10-second timer.

###  Client-Server Communication
- Efficient communication between client and server using TCP for game data and UDP for discovery.

###  Broadcast Discovery
- Server broadcasts connection offers to clients via UDP.
- Clients automatically detect and connect to the server.

###  Real-Time Gameplay
- Handles player answers in real-time with instant winner or draw notifications.

---

##  How to Run

### **Server Setup:**
1. Ensure the `scapy` library is installed (Linux recommended).
2. Run the server script:
   ```bash
   python3 server.py
   ```

### **Client Setup:**
1. Ensure `getch` (Linux) or `msvcrt` (Windows) is available.
2. Run the client script:
   ```bash
   python3 client.py
   ```

---

##  System Requirements

- Python 3.x
- `scapy` (for server-side broadcasting on Linux)
- Linux or Windows (with `msvcrt`) for client operation

---

##  Gameplay Instructions
1. Start the server first to begin broadcasting.
2. Launch the client scripts on two different machines or terminal instances.
3. When two clients connect, they receive a math problem.
4. Players submit answers as quickly as possible within 10 seconds.
5. The server announces the winner or declares a draw.
