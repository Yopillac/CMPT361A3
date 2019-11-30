#CMPT361 Assignment 3
#Server_enhanced.py
#Ryan Dykstra, Dale Albert, Adrian Cate

import socket
import sys
import os
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import PKCS1_OAEP

MAX_FILE_SIZE = 100000
serverPort = 13000

#####################################
''' server function: 
    Input: None
    Function: 
        - listens and processes client file transfers
    Return: None
 '''
def server():

	try:
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as e:
		print('Error in server socket creation:', e)
		sys.exit(1)

	try:
		serverSocket.bind(('', serverPort))
	except socket.error as e:
		print('Error in server socket binding', e)
		sys.exit(1)

	print('The server is ready to accept connections')
	serverSocket.listen(3)

	#Allow clients with these names
	clients = ["client1", "client2", "client3"]

	#Get the server's private key from a file and create a cipher
	serPrivFile = open('server_private.pem', 'rb')
	serPrivKey = serPrivFile.read()
	serPrivFile.close()
	serPriv = RSA.import_key(serPrivKey)
	serCipher = PKCS1_OAEP.new(serPriv)

	while 1:
		try:
			connectionSocket, addr = serverSocket.accept()
			pid = os.fork()

			#If the process is a child process
			if pid == 0:

				serverSocket.close()
				
				#Receive nonce from client
				rcvNonce = connectionSocket.recv(256)
				nonce = int(unpad(serCipher.decrypt(rcvNonce), 16).decode('ascii'))
				print("Nonce:", nonce)
				expectedNonce = nonce + 1

				#Receive client name
				encryptClientName = connectionSocket.recv(2048)
				clientName = unpad(serCipher.decrypt(encryptClientName), 16).decode('ascii')
					

				#Check if client name is valid
				if clientName in clients:
					
					#Get the client's public key from a file
					cliPubFile = open(clientName + '_public.pem', 'rb')
					cliPubKey = cliPubFile.read()
					cliPubFile.close()
					cliPub = RSA.import_key(cliPubKey)
					cliCipher = PKCS1_OAEP.new(cliPub)

					#Generate symmetric key and cipher (256 AES) 
					sym_key = get_random_bytes(32)
					cipher = AES.new(sym_key, AES.MODE_ECB)

					#Send sym_key to client, encrypted with public key
					encryptSymKey = cliCipher.encrypt(pad(sym_key, 16))
					connectionSocket.send(encryptSymKey)

					#Print acceptance message
					print("Connection Accepted and Symmetric Key Generated for client:", clientName)
				
				else:
					#Otherwise, send
					invalid = ("Invalid clientName")
					connectionSocket.send(invalid.encode('ascii'))
					print("The received client:", clientName, "is invalid (Connection Terminated).")
					connectionSocket.close()
					return

				#Send nonce for requesting filename message
				nonce = nonce+1
				expectedNonce = funcSendNonce(connectionSocket, cipher, nonce)

				#Send message asking for filename
				fileMsg = "Enter filename: "
				encryptFileMsg = cipher.encrypt(pad(fileMsg.encode('ascii'), 16))
				connectionSocket.send(encryptFileMsg)
				print("Server is now processing client", clientName, "request.")

				#Receive nonce for filename
				nonce, expectedNonce = receiveNonce(connectionSocket, cipher, expectedNonce, 16)

				#Receive filename
				encryptFilename = connectionSocket.recv(2048)
				filename = unpad(cipher.decrypt(encryptFilename), 16).decode('ascii')
				print("The server received the file name", filename, "from client:", clientName)

				#Send nonce for requesting file size from client
				nonce = nonce+1
				expectedNonce = funcSendNonce(connectionSocket, cipher, nonce)

				#Send message requesting file size
				rqstSize = "Server Requested file size"
				encryptRqstSize = cipher.encrypt(pad(rqstSize.encode('ascii'), 16))
				connectionSocket.send(encryptRqstSize)

				#Receive nonce for filesize
				nonce, expectedNonce = receiveNonce(connectionSocket, cipher, expectedNonce, 16)

				#Receive filesize
				encryptFileSize = connectionSocket.recv(2048)
				fileSize = unpad(cipher.decrypt(encryptFileSize), 16).decode('ascii')
				fileSize = int(fileSize)

				#Send nonce for if filesize is ok or not
				nonce = nonce+1
				expectedNonce = funcSendNonce(connectionSocket, cipher, nonce)

				#If filesize is greater than MAX_FILE_SIZE, close connection
				if (fileSize > MAX_FILE_SIZE):
					status = "No"
					encryptStatus = cipher.encrypt(pad(status.encode('ascii'), 16))
					connectionSocket.send(encryptStatus)
					print("File size exceeds the threshold. Terminating Connection with", clientName)
					connectionSocket.close()
					return

				#Otherwise, send OK status
				status = "OK"
				encryptStatus = cipher.encrypt(pad(status.encode('ascii'), 16))
				connectionSocket.send(encryptStatus)
				print("Uploading data from:", clientName)

				#Set path that file will be uploaded to
				path = (clientName + "/" + filename)
				file = open(path, "w")

				ack=0
				#Receive data from client
				encryptData = connectionSocket.recv(1024)
				#While receiving data:
				while(encryptData):

					#Decrypt and write to file
					data = unpad(cipher.decrypt(encryptData), 16).decode('ascii')
					file.write(data)

					#Increment ack and send to client
					ack=ack+1
					encryptAck = cipher.encrypt(pad(str(ack).encode('ascii'), 16))
					connectionSocket.send(encryptAck)

					#Receive the next data from the client
					encryptData = connectionSocket.recv(1024)

				#Close file and print completion message
				file.close()
				print("Upload complete for:", clientName, "\nTerminating connection")

				connectionSocket.close()
				return

			connectionSocket.close()

		except socket.error as e:
			print("An error occured:", e)
			serverSocket.close()
			sys.exit(1)

		except:
			print("Some kind of error")
			serverSocket.close()
			sys.exit(0)

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

server()