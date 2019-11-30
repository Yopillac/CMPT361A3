#CMPT361 Assignment 3
#Client_enhanced.py
#Ryan Dykstra, Dale Albert, Adrian Cate

import socket
import sys
import random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import PKCS1_OAEP

#####################################
''' client function: 
    Input: None
    Function: 
        - communicates with a server to send a file
    Return: None
 '''
def client():

	serverName = input("Enter the server IP or name: ")
	serverPort = 13000
	clientName = input("Enter your client name: ")

	try:
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as e:
		print("Error in client socket creation:", e)
		sys.exit(1)

	try:
		clientSocket.connect((serverName, serverPort))

		#Get the server's public key from a file
		serPubFile = open('server_public.pem', 'rb')
		serPubKey = serPubFile.read()
		serPubFile.close()
		serPub = RSA.import_key(serPubKey)
		serCipher = PKCS1_OAEP.new(serPub)

		#Send nonce for client name to server
		nonce = random.randint(10000, 20000)
		expectedNonce = funcSendNonce(clientSocket, serCipher, nonce)

		#Send client name
		encryptClientName = serCipher.encrypt(pad(clientName.encode('ascii'), 16))
		clientSocket.send(encryptClientName)
		
		acceptMsg = clientSocket.recv(256)

		#If the sever sends "Invalid clientName", close the connection
		if (acceptMsg == ("Invalid clientName").encode('ascii')):
		 	print("Invalid client name.\nTerminating.")
		 	clientSocket.close()
		 	return
		else:
			#Get the client's private key from a file
			cliPrivFile = open(clientName + '_private.pem', 'rb')
			cliPrivKey = cliPrivFile.read()
			cliPrivFile.close()
			cliPriv = RSA.import_key(cliPrivKey)
			cliCipher = PKCS1_OAEP.new(cliPriv)

		#Get symmetric key from server and create a cipher
		sym_key = unpad(cliCipher.decrypt(acceptMsg), 16)
		print("Received the symmetric key from the server.")
		cipher = AES.new(sym_key, AES.MODE_ECB)

		#Receive nonce for filename message
		nonce, expectedNonce = receiveNonce(clientSocket, cipher, expectedNonce, 16)
		
		#Receive filename message
		encryptFileMsg = clientSocket.recv(2048)
		fileMsg = unpad(cipher.decrypt(encryptFileMsg), 16).decode('ascii')

		#Send nonce for filename
		nonce = nonce+1
		expectedNonce = funcSendNonce(clientSocket, cipher, nonce)
		
		#Send filename
		filename = input(fileMsg)
		encryptFilename = cipher.encrypt(pad(filename.encode('ascii'), 16))
		clientSocket.send(encryptFilename)

		#Receive nonce for message requesting file size
		nonce, expectedNonce = receiveNonce(clientSocket, cipher, expectedNonce, 16)
		
		#Receive message requesting file size
		encryptRqstSize = clientSocket.recv(2048)
		rqstSize = unpad(cipher.decrypt(encryptRqstSize), 16).decode('ascii')
		print(rqstSize)

		#Count number of characters in file and record it in count
		file = open(filename)
		data = file.read()
		file.close()
		count = str(len(data))
		print(count)

		#Send nonce for count
		nonce = nonce+1
		expectedNonce = funcSendNonce(clientSocket, cipher, nonce)

		#Send count
		encryptCount = cipher.encrypt(pad(count.encode('ascii'), 16))
		clientSocket.send(encryptCount)

		#Receive nonce for if file is accepted/rejected
		nonce, expectedNonce = receiveNonce(clientSocket, cipher, expectedNonce, 16)
		
		#Receive acceptance/rejection message
		encryptStatus = clientSocket.recv(2048)
		status = unpad(cipher.decrypt(encryptStatus), 16).decode('ascii')

		#If "No", close connection
		if (status == "No"):
			print("The file size is too large.\nTerminating")
			clientSocket.close()
			return

		#Open file and read first 1000 bytes
		file = open(filename)
		data = file.read(1000)

		#While reading data:
		while (data):

			#Send encrypted data
			encryptData = cipher.encrypt(pad(data.encode('ascii'), 16))
			clientSocket.send(encryptData)

			#Receive an ack each time
			encryptAck = clientSocket.recv(128)
			ack = unpad(cipher.decrypt(encryptAck), 16).decode('ascii')

			#Read more characters
			data = file.read(1000)
			
		file.close()
		print("The file size is OK.\nSending the file contents to the server.\nThe file is saved.")

		clientSocket.close()
		return

	except socket.error as e:
		print('An error occured:', e)
		clientSocket.close()
		sys.exit(1)

#####################################
''' receiveNonce function: 
    Input:
    	- socket: a socket object
    	- cipher: a cipher object
    	- expected: the expected next nonce
    	- byte: how many bytes to receive
    Function: 
        - receives nonce and checks to make sure it is expected
    Return:
    	- nonce: the received nonce
    	- expected+1: the new expected nonce
 '''
def receiveNonce(socket, cipher, expected, byte):

	rcvNonce = socket.recv(byte)
	nonce = int(unpad(cipher.decrypt(rcvNonce), 16).decode('ascii'))
	print("Nonce:", nonce)

	while (nonce != expected):
		rcvNonce = socket.recv(byte)
		nonce = int(unpad(cipher.decrypt(rcvNonce), 16).decode('ascii'))

	return nonce, expected+1

#####################################
''' receiveNonce function: 
    Input:
    	- socket: a socket object
    	- cipher: a cipher object
    	- nonce: the nonce to send
    Function:
    	 - sends nonce to a socket
    Return:
    	- nonce+1: the new expected nonce
 '''
def funcSendNonce(socket, cipher, nonce):

	sendNonce = cipher.encrypt(pad(str(nonce).encode('ascii'), 16))
	socket.send(sendNonce)

	return nonce+1

client()