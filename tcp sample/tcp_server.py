# server side:

import socket
import select
import time
import random


SERVER = "192.168.1.1"
PORT = 5050
ADDR = (SERVER, PORT)


def all_sockets_closed(server_socket, starttime):
    """closes the server socket and displays the duration of the connection"""
    print("\n\nAll Clients Disconnected\nClosing The Server...")
    endtime = time.time()
    elapsed = time.strftime("%H:%M:%S", time.gmtime(endtime - starttime))
    unit = (
        "Seconds"
        if elapsed < "00:01:00"
        else "Minutes"
        if "01:00:00" > elapsed >= "00:01:00"
        else "Hours"
    )
    server_socket.close()
    print(f"\nThe Server Was Active For {elapsed} {unit}\n\n")


def active_client_sockets(connected_sockets):
    """prints the IP and PORT of all connected sockets"""
    print("\nCurrently Connected Sockets:")
    for c in connected_sockets:
        print("\t", c.getpeername())  # ('IP', PORT)


# args by order: current socket being served, server socket, all sockets being connected, start time
def serve_client(current_socket, server_socket, connected_sockets, starttime):
    """Takes the msg received from the client and handles it accordingly"""
    try:
        client_data = current_socket.recv(1024).decode()
        date_time = time.strftime("%d/%m/%Y, %H:%M:%S")
        print(
            f"\nReceived new message form client {current_socket.getpeername()} at {date_time}:"
        )

    except ConnectionResetError:
        print(f"\nThe client {current_socket.getpeername()} has disconnected...")
        connected_sockets.remove(current_socket)
        current_socket.close()
        if len(connected_sockets) != 0:  # check for other connected sockets
            active_client_sockets(connected_sockets)
        else:
            raise ValueError
        """the whole disconnection sequence is triggered from the exception handler, se we will just raise the exception
                to close the server socket"""
    else:
        print(client_data)

        if client_data == "Bye":
            current_socket.send("bye".encode())
            print(
                "Connection closed",
            )
        # if the client asks to disconnect, he sends the word "quit" and the server response with "Bye" message.
        # and when the client receives this message it automatically disconnects from the server.
        # we also know that the server response back the messages received the client.
        # so we want to make sure that if the client sends to word "Bye", the server wont send the exact same message,
        # and therefore wont force the client to disconnect.

        elif client_data.upper() == "NAME":  # send server's name
            current_socket.send("SERVER'S NAME: LOCAL HOST - MY PC".encode())
            print("Responded by: Sending The Name of the Server")

        elif client_data.upper() == "TIME":  # send current time and date
            current_time = f"Today is {time.strftime('%A %d %b %Y %I:%M:%S')}"
            current_socket.send(current_time.encode())
            print("Responded by: Sending current time and date")

        elif client_data.upper() == "RAND":  # send random number between 0 and 10
            random_number = str(round(10 * (random.random())))
            current_socket.send(f"Your random number is: {random_number}".encode())
            print(
                f"Responded by: Sending a random number between 0-10: {random_number}"
            )

        elif (
            client_data.upper() == "QUIT" or client_data.upper() == "Q"
        ):  # close connection with the client and close socket
            print(
                f"Closing the socket with client {current_socket.getpeername()} now..."
            )
            current_socket.send("Bye".encode())
            # tell the client we accepted his request to disconnect, also disconnect the client from their side
            connected_sockets.remove(current_socket)
            current_socket.close()
            if len(connected_sockets) != 0:
                active_client_sockets(connected_sockets)
            else:
                raise ValueError
            """the whole disconnection sequence is triggered from the exception handler, se we will just raise the exception
                to close the server socket"""

        else:
            current_socket.send(client_data.encode())
            print("Responded by: Sending the message back to the client")


def main():
    """server setup and socket handling"""
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDR)

    server_socket.listen()
    print("\n* Server is ON *\n")
    print("Waiting for clients to establish connection...")
    starttime = time.time()
    connected_sockets = []  # list of the client sockets being connected
    try:
        while True:
            ready_to_read, ready_to_write, in_error = select.select(
                [server_socket] + connected_sockets, [], []
            )
            for current_socket in ready_to_read:
                if (
                    current_socket is server_socket
                ):  # if the current socket is the new socket we receive from the server
                    (client_socket, client_address) = current_socket.accept()
                    print("\nNew client joined!", client_address)
                    connected_sockets.append(client_socket)
                    active_client_sockets(connected_sockets)
                    continue
                serve_client(
                    current_socket, server_socket, connected_sockets, starttime
                )

    except ValueError:
        # occurs when the last client connected is forcibly closing the socket (and not by Sending 'q' or 'quit'),
        # and the server keeps scanning with the 'select()' method.
        # In this case the select method will return -1 and raise an exception for value error.
        # we know that this exception can be raised only when the list of connected sockets is empty, so we will call a function to close the server socket.

        all_sockets_closed(server_socket, starttime)
        pass


if __name__ == "__main__":
    main()