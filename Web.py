from socket import *
from threading import *

host = ''
port = 8888

s = socket(AF_INET, SOCK_STREAM)
s.bind((host, port))
s.listen(5)
print(s)


def client_thread(conn):
    while True:
      data = conn.recv(4096)

      print(data)
      # CHECK STATUS CODES




      test = open('test.html','rb')
      file = test.read()
      test.close()

      head = b"HTTP/1.1 200 OK\n"
      response = head + file
      conn.send(response)


    conn.close()
        


while True:
    clientsocket, address = s.accept()

    client_thread(clientsocket)



