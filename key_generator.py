from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

key = RSA.generate(2048)
#private_key = key.export_key()
#public_key = key.publickey().export_key()

private = open("private.pem", "wb")
private.write(key.export_key())
private.close()

public = open("public.pem", "wb")
public.write(key.publickey().export_key())
public.close()