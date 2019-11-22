from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

key = RSA.generate(2048)

recipient = input("Who are these keys for? ")

private = open(recipient + "_private.pem", "wb")
private.write(key.export_key())
private.close()

public = open(recipient + "_public.pem", "wb")
public.write(key.publickey().export_key())
public.close()