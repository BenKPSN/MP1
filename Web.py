from socket import *
from threading import *

host = ''
port = 8888

s = socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)

while True:
    clientsocket, address = s.accept()

    #For now, this is discarded. When we check if the connection is correct we need to look at this.
    reveived_data = clientsocket.recv(1024).decode()
    
    http_response = """
HTTP/1.1 200 OK
<html>

<head>
  <meta charset="utf-8">
  <title></title>
  <meta name="author" content="">
  <meta name="description" content="">
  <meta name="viewport" content="width=device-width, initial-scale=1">

</head>

<body>

  <p>Congratulations! Your Web Server is Working!</p>

</body>

</html>
"""
    clientsocket.send(http_response.encode())
    clientsocket.close()
