# CMPT361A3
CMPT361 Assignment 3
Group members: Adrian Cate, Ryan Dykstra, Dale Albert

Program state:
  server.py:
    -Creates a serverSocket object and listens for client connections
    -creates list of clients permitted to use the server
    -reads stored server_private.pem file, generates RSA private key/ cypher
    -upon new connection request to serversocket, creates new fork for each client
    -decrypts client name and checks for eligibility
    -gets clients public key from file
    -generates symmetric key for use in current connection, sends to client encrypted with pub key
    -prompts newly cononected client for filename
    -   
  client.py:
    -
 
Tests Conducted:
  -
Attack and Solution:
  -
