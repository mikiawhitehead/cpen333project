# Group#: G33
# Student Names: Emmanuel Santacruz, Mikia Whitehead

#server

import socket
import random

from time import sleep

HOST = "127.0.0.1"  # local host
PORT = 65432        # port used by the server

#creating server socket and binding it to the client
ss = socket.socket()  
ss.bind((HOST, PORT))  

# determine that the server can only listen to 1 client
ss.listen(1)

#accept the connection with client
conn, address = ss.accept()  

#debugging purposes #
#print("Connection established from: " + str(address))
i = 1

while True:

    # recieve data. packet cannot be greater than 1024 bytes
    clientMessage = conn.recv(1024).decode()

    if not clientMessage:
        # if data is not received break, not necessary but for proper coding purposes 
        break

    #debugging purposes, print client message to ensure the message number is increasing 
    #print(str(clientMessage))

    #modify message and wait a random amount of time, between 5ms to 50 ms
    modifiedMessage = str("PING " + str(i) + " : ditto!")
    waitTime = random.uniform(0.005,0.05)

    #debugging purposes, print the server wait time and see if its similar to RTT in client
    #print("server wait time %f ms" %(waitTime*1000))

    #sleep the random amount of time
    sleep(waitTime)

    #declaring lost packet variable
    lostp = random.randrange(1,11,1)

    # if packet not the 10% then packet is sent to client, if it is 10% then it is lost 
    if lostp != 1:
        conn.send(modifiedMessage.encode())
        i = i + 1

    else: 
        #ignores message if packet is lost
        continue
        #debugging purposes, server prints message lost
        #print("message lost :( \n")
    

conn.close()  # close the connection