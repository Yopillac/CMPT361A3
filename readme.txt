Ryan Dykstra
Dale Albert
Adrian Cate

Status:
Server.py, Server_ehanced.py, Client.py, and Client_enhanced.py work as expected.
A deficiency is that multiple clients can connect to the server with the same client name.

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

