import socket
import sys
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

MAX_FILE_SIZE = 100
serverPort = 13000

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

	clients = ["Client1", "Client2", "Client3"]

	while 1:
		#try:
		connectionSocket, addr = serverSocket.accept()
		pid = os.fork()

		if pid == 0:

			serverSocket.close()
			
			#Receive client name and check if it is valid
			clientName = connectionSocket.recv(2048)
			clientName = clientName.decode('ascii')
			if clientName in clients:
				#Generate sym_key (256 AES) and send to client, encrypted with client pubkey
				sym_key = get_random_bytes(32)
				cipher = AES.new(sym_key, AES.MODE_ECB)
				#Send to client, encrypted with client public key
				connectionSocket.send(sym_key)
				#Print acceptance message
				print("Connection Accepted and Symmetric Key Generated for client:", clientName)
			else:
				invalid = ("Invalid clientName")
				connectionSocket.send(invalid)
				print("The received client:", clientName, "is invalid (Connection Terminated).")
				connectionSocket.close()
				return

			#Encrypt all future messages with client with sym_key

			fileMsg = "Enter filename: "
			encryptFileMsg = cipher.encrypt(pad(fileMsg.encode('ascii'), 16))
			connectionSocket.send(encryptFileMsg)
			print("Server is now processing client", clientName, "request.")

			encryptFilename = connectionSocket.recv(2048)
			filename = unpad(cipher.decrypt(encryptFilename), 16).decode('ascii')
			print("The server received the file name", filename, "from client:", clientName)

			rqstSize = "Server Requested file size"
			encryptRqstSize = cipher.encrypt(pad(rqstSize.encode('ascii'), 16))
			connectionSocket.send(encryptRqstSize)

			encryptFileSize = connectionSocket.recv(2048)
			fileSize = unpad(cipher.decrypt(encryptFileSize), 16).decode('ascii')
			fileSize = int(fileSize)
			if (fileSize > MAX_FILE_SIZE):
				status = "No"
				encryptStatus = cipher.encrypt(pad(status.encode('ascii'), 16))
				connectionSocket.send(encryptStatus)
				print("File size exceeds the threshold. Terminating Connection with", clientName)
				connectionSocket.close()
				return

			status = "OK"
			encryptStatus = cipher.encrypt(pad(status.encode('ascii'), 16))
			connectionSocket.send(encryptStatus)
			print("Uploading data from:", clientName)

			#Receive file from client, write it to proper directory
			print("Upload complete for:", clientName, "Terminating connection")

			connectionSocket.close()
			return

		connectionSocket.close()

		#except:

server()