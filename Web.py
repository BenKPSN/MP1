import socket
import threading

host = ''
port = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)

while True:
    clientsocket, address = s.accept()


    reveived_data = clientsocket.recv(1024)
    
    http_response = b"""\
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
    clientsocket.sendall(http_response)
    clientsocket.close()