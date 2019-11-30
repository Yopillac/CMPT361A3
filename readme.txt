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

