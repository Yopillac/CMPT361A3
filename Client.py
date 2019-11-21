import socket
import sys
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import PKCS1_OAEP

def client():

	serverName = input("Enter the server IP or name: ")
	serverPort = 13000
	clientName = input("Enter your client name: ")

	try:
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as e:
		print("Error in client socket creation:", e)
		sys.exit(1)

	#Get the server's public key from a file
	serPubFile = open('server_public.pem', 'rb')
	serPubKey = serPubFile.read()
	serPubFile.close()
	serPub = RSA.import_key(serPubKey)
	serCipher = PKCS1_OAEP.new(serPub)

	#Get the client's private key from a file
	cliPrivFile = open('client1_private.pem', 'rb')
	cliPrivKey = cliPrivFile.read()
	cliPrivFile.close()
	cliPriv = RSA.import_key(cliPrivKey)
	cliCipher = PKCS1_OAEP.new(cliPriv)

	#try:
	clientSocket.connect((serverName, serverPort))

	#Send client name to server
	#Need to encrypt it with server's public key
	encryptClientName = serCipher.encrypt(pad(clientName.encode('ascii'), 16))
	clientSocket.send(encryptClientName)

	acceptMsg = clientSocket.recv(2048)
	#if (acceptMsg.decode('ascii') == "Invalid clientName"):
	if (acceptMsg.can_decrypt()):
		sym_key = unpad(serCipher.decrypt(acceptMsg), 16).decode('ascii')
	else:
	 	print("Invalid client name.\nTerminating.")
	 	clientSocket.close()
	 	return
	 	
	print("Received the symmetric key from the server.")
	cipher = AES.new(sym_key, AES.MODE_ECB)

	#Encrypt all further messages to the server with sym_key

	encryptFileMsg = clientSocket.recv(2048)
	fileMsg = unpad(cipher.decrypt(encryptFileMsg), 16).decode('ascii')

	filename = input(fileMsg)
	encryptFilename = cipher.encrypt(pad(filename.encode('ascii'), 16))
	clientSocket.send(encryptFilename)

	encryptRqstSize = clientSocket.recv(2048)
	rqstSize = unpad(cipher.decrypt(encryptRqstSize), 16).decode('ascii')
	print(rqstSize)
	#Count number of characters in file and record it in count
	count = str(1)
	encryptCount = cipher.encrypt(pad(count.encode('ascii'), 16))
	clientSocket.send(encryptCount)

	encryptStatus = clientSocket.recv(2048)
	status = unpad(cipher.decrypt(encryptStatus), 16).decode('ascii')
	if (status == "No"):
		print("The file size is too large.\nTerminating")
		clientSocket.close()
		return

	#Encrypt file and send to server
	print("The file size is OK.\nSending the file contents to the server.\nThe file is saved.")

	clientSocket.close()
	return

	#except:

client()