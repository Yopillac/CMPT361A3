import socket
import sys

def client():

	serverName = input("Enter the server IP or name: ")
	serverPort = 13000
	clientName = input("Enter your client name: ")

	try:
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as e:
		print("Error in client socket creation:", e)
		sys.exit(1)

	#try:
	clientSocket.connect((serverName, serverPort))

	#Send client name to server
	#Need to encrypt it with server's public key
	encryptClientName = clientName.encode('ascii')
	clientSocket.send(encryptClientName)

	acceptMsg = clientSocket.recv(2048)
	acceptMsg = acceptMsg.decode('ascii')
	if (acceptMsg == "Invalid clientName"):
		print("Invalid client name.\nTerminating.")
		clientSocket.close()
		return

	sym_key = acceptMsg
	print("Received the symmetric key from the server.")

	#Encrypt all further messages to the server with sym_key

	encryptFileMsg = clientSocket.recv(2048)
	fileMsg = encryptFileMsg.decode('ascii')

	filename = input(fileMsg)
	encryptFilename = filename.encode('ascii')
	clientSocket.send(encryptFilename)

	encryptRqstSize = clientSocket.recv(2048)
	rqstSize = encryptRqstSize.decode('ascii')
	print(rqstSize)
	#Count number of characters in file and record it in count
	count = str(1)
	encryptCount = count.encode('ascii')
	clientSocket.send(encryptCount)

	encryptStatus = clientSocket.recv(2048)
	status = encryptStatus.decode('ascii')
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