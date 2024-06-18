from socket import *
from threading import *

host = ''
port = 8889

s = socket(AF_INET, SOCK_STREAM)
s.bind((host, port))
s.listen(5)
print(s)


def client_thread(conn):

    data = conn.recv(4096)
    print(data)
    # CHECK STATUS CODES



    test = open('test.html','rb')
    file = test.read()
    test.close()

    

    head = b"HTTP/1.1 200 OK\r\n\r\n"
    response = head + file
    conn.send(response)


    conn.close()
        



while True:
    clientsocket, address = s.accept()
    data = clientsocket.recv(4096)
    
    try:
        check = open('test.html','rb')
    except:
        proxysocket = socket(AF_INET, SOCK_STREAM)
        proxysocket.connect(('',8888))
        sentence = 'GET /test.html HTTP/1.1\r\n\r\n'
        proxysocket.send(sentence.encode())
        result = proxysocket.recv(1024)
        modresult = result.decode()
        linechar = modresult.find('\n')
        modresult = modresult[linechar + 1:]
        check = open('test.html', 'a')
        check.append(modresult)
    
    file = check.read()
    check.close()
    head = b"HTTP/1.1 200 OK\n"
    response = head + file
    clientsocket.send(response)
    
    clientsocket.close()

