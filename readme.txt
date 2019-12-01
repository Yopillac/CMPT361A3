Ryan Dykstra
Dale Albert
Adrian Cate

Status:
Server.py, Server_ehanced.py, Client.py, and Client_enhanced.py work as expected.
A deficiency is that multiple clients can connect to the server with the same client name.

  Server.py:
    -Creates a serverSocket object and listens for client connections
    -creates list of clients permitted to use the server
    -reads stored server_private.pem file, generates RSA private key/ cypher
    -upon new connection request to serversocket, creates new fork for each client
    -decrypts client name and checks for eligibility
    -gets clients public key from file
    -generates symmetric key for use in current connection, sends to client encrypted with pub key
    -prompts newly connected client for filename, checks filesize
    -uploads to clients folder in server storage as cliet, write to file in 1000 byte chunks
    -updates ack # after each chunk and sends to client
    -close file, print completion msg
    -terminate connection
    
  Client.py
    -prompts user for requested server and their client username
    -connet client to server on port 13000
    -once connencted gets servers pubkey from a file
    -encrypt and send client name to server
    -if clientname accepted, get clients private key and decrypts symmetric key from server
    -send server filename and calculate/send filesize once prompted
    -if accepted, send file 1000 bytes at a time, upon ack of last piece received from server
    -confirmation message,close connection

Tests:
Client enters invalid client name: Connection is terminated
Client enters valid client name: Connection is granted
Client enters file > MAX_FILE_SIZE: Connection is terminated
Client enters file <= MAX_FILE_SIZE: File is transfered successfully
Client enters file that must be transfered in more than 1 chunk: Transfers successfully
All these scenarios work with 1-3 clients connected to server
These tests were also conducted with Server_enhanced.py and Client_enhanced.py, and work
as expected
These tests were also conducted while sshing to the lab machines, and all work as expected

Section V:
    Server_enhanced.py
      -Sets max file size to 100000
      -Sets server port number to 13000
      -Creates and initializes a socket called serverSocket and binds the socket
      -Displays message indicating server is ready
      -serverSocket listens for clients (max 3)
      -Creates and initializes a list of client names 
      -Obtains server's private key from the file server_private.pem 
      -Creates a cipher with obtained private key
      -Creates new fork each time a connection request is issued on serverSocket (max 3)
      -Checks if pid is equal to 0 (0 = child process)
      -If true, closes serverSocket
      -Receives and decrypts nonce from client, prints it, and then increments it by one
      -Receives and decrypts client name from client
      -Checks if client name is in the list of eligible client names
      -If true, obtains client's public key from client's public key file and creates a cipher
      -Generates symmetric key and 256 AES cipher
      -Encrypts symmetric key with client's public key and sends it to client
      -Calls funcSendNonce to send incremented nonce to client, then returns nonce that is incremented again
      -Prompts client for filename
      -Calls recieveNonce to check if the received nonce matches the expected nonce 
      -Returns with nonce and incremented expected nonce  
      -Receives filename and prompts client for file size
      -Checks file size to see if its less than max file size, terminates connection is false
      -Receives data from client and writes it to server directory (1000 bytes per data block)
      -Sends confirmation message upon completion 
      -Terminates connection 
    
    Client_enhanced.py
      -Prompts user for server IP or name and client name 
      -Creates a socket called client socket
      -Establishes connection with server using inputted server name or IP
      -Acquires server's public key from server_public.pem file, creates a cipher
      -Generates nonce and sends it to server
      -Sends client name to server
      -Acquire client's private key from file, generates a cipher 
      -Receives symmetric key from server and generates 256 AES cipher 
      -Receives prompt for filename and sends filename to server
      -Receives prompt for file size, counts file size, and sends file size to server 
      -Receives acceptance or rejection message 
      -If accepted, reads and sends 1000 bytes of the file 
      -Connection is terminated after whole file is sent

