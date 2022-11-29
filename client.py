# Group#: G33
# Student Names: Emmanuel Santacruz, Mikia Whitehead

#client 

import socket
import time

HOST = "127.0.0.1" # local host
PORT = 65432 # port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sc:
    #establishing connection and delaring message counter
    sc.connect((HOST,PORT))
    i = 1

    clientMessage = str("PING " + str(i) + " - hello world" )

    #repeat loop for 5 consecutive messages
    while i <= 5:

        #send the client message to the server, encode
        #note send time in variable 
        sc.send(clientMessage.encode())  
        sent_time_ms = time.time()

        #setting a timeout for if the server doesn't send a message for 1 second 
        sc.settimeout(1)

        #see if there is a message recieved from server
        try: 
            serverMessage = sc.recv(1024).decode()      # receive response
            recv_time_ms = time.time()                  # noting recieved time 
            
            #calculating RTT time and rounding to 3 decimal places 
            rtt_time_ms = round((recv_time_ms - sent_time_ms)*1000, 3)

            print("RTT: " + str(rtt_time_ms) + " ms\n Return Message: " + str(serverMessage))  # show in terminal

            #incrememnt message number
            i = i + 1
            clientMessage = str("PING " + str(i) + " - hello world" ) # making next message

        #if no message recieved for 1 s, then program times out and closes
        except:
            print("request timed out")
            sc.close()
    

    sc.close()  # close the connection