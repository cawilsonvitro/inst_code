# client side:

import socket
import sys


SERVER = "127.0.0.1" #192.168.1.1"
PORT = 5050
ADDR = (SERVER, PORT)


soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    soc.connect(ADDR)

except TimeoutError or ConnectionResetError:
    print(
        "\nCould not receive a response from the server.\n"
        "Please check the IP and PORT numbers provided.\n"
    )
    sys.exit()

except OSError or ConnectionRefusedError:
    print(
        "\nPlease check if the server is connected to the internet\n"
        "and that the IP and PORT numbers are correct on both ends\n"
    )
    sys.exit()


data = ""
flag = 0


# while data != "Bye":
#     try:
#         if flag == 0:
#             long_msg_txt = (
#                 "\nWelcome! \n\n"
#                 "Please enter your message, or type:\n"
#                 "NAME - to get the name of the server\n"
#                 "TIME -  to get the current time and date\n"
#                 "RAND - to receive a random number between 0-10\n"
#                 "QUIT or Q - to close the socket\n\n"
#                 "Enter your message Here: "
#             )
#             long_msg = input(long_msg_txt)
#             soc.send(long_msg.encode())
#             flag += 1
#         else:
#             msg = input("Enter your message Here: ")
#             soc.send(msg.encode())
#         data = soc.recv(1024).decode()
#     except ConnectionResetError or ConnectionAbortedError:

#         print("\nThe connection was forcibly closed by the remote host\n")
#         break
#     else:
#         # received message from server(1024=max bytes size)
#         print(f"\nThe server sent: {data}\n")

# when data == "Bye"
soc.send("hi".encode())
soc.recv(1024)
print("Closing the socket with the server")
soc.close()  # close the connection