#CMPT361 Assignment 3
#Client.py
#Ryan Dykstra, Dale Albert, Adrian Cate

import socket
import sys
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

		#Send client name to server
		encryptClientName = serCipher.encrypt(pad(clientName.encode('ascii'), 16))
		clientSocket.send(encryptClientName)

		acceptMsg = clientSocket.recv(2048)

		#If the sever sends "Invalid clientName", close the connection
		if (acceptMsg == ("Invalid clientName").encode('ascii')):
		 	print("Invalid client name.\nTerminating.")
		 	clientSocket.close()
		 	return
		#Otherwise, get the client's private key from a file
		else:
			cliPrivFile = open(clientName + '_private.pem', 'rb')
			cliPrivKey = cliPrivFile.read()
			cliPrivFile.close()
			cliPriv = RSA.import_key(cliPrivKey)
			cliCipher = PKCS1_OAEP.new(cliPriv)
			sym_key = unpad(cliCipher.decrypt(acceptMsg), 16)

		#Create a cipher
		print("Received the symmetric key from the server.")
		cipher = AES.new(sym_key, AES.MODE_ECB)

		#Receive message asking for filename
		encryptFileMsg = clientSocket.recv(2048)
		fileMsg = unpad(cipher.decrypt(encryptFileMsg), 16).decode('ascii')

		#Input filename and send to server
		filename = input(fileMsg)
		encryptFilename = cipher.encrypt(pad(filename.encode('ascii'), 16))
		clientSocket.send(encryptFilename)

		#Receive message asking for size of file
		encryptRqstSize = clientSocket.recv(2048)
		rqstSize = unpad(cipher.decrypt(encryptRqstSize), 16).decode('ascii')
		print(rqstSize)

		#Count number of characters in file and record it in count, send to server
		file = open(filename)
		data = file.read()
		file.close()
		count = str(len(data))
		print(count)
		encryptCount = cipher.encrypt(pad(count.encode('ascii'), 16))
		clientSocket.send(encryptCount)

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

client()