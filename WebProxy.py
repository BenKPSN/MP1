from socket import *
from threading import *
from time import *

#Global variables.
host = ''
port = 8889
lockedFile = 'locked.html'
lastEdit = gmtime(time())

#Create server socket.
s = socket(AF_INET, SOCK_STREAM)
s.bind((host, port))
s.listen(5)

#This is the function that makes this server a proxy.
def proxy_check(file):

    #First we check if the proxy has the webpage cached. If it does, we're good.
    try:
        check = open(file, 'rb')
        check.close()
        return b"good"
    
    #Otherwise, we need to connect to the main server and GET the file.
    except:
        proxysocket = socket(AF_INET, SOCK_STREAM)
        proxysocket.connect(('localhost',8888))
        sentence = 'GET /' + file + ' HTTP/1.1\r\n\r\n'
        proxysocket.send(sentence.encode())
        result = proxysocket.recv(1024)
        modresult = result.decode()

        #Ok, now that that's succeeded, we check the resulting status code.
        firstSpace = modresult.find(' ')
        statusCode = modresult[firstSpace + 1:firstSpace + 4]

        #These are the three non-200 OK statuses we can receive. If we get any, something's gone wrong.
        if statusCode == "400":
            return b"HTTP/1.1 400 Bad Request\r\n\r\n"
        elif statusCode == "403":
            return b"HTTP/1.1 403 Forbidden\r\n\r\n"
        elif statusCode == "404":
            return b"HTTP/1.1 404 Not Found\r\n\r\n"
        
        #If everything's good, we create a file to cache the webpage.
        linechar = modresult.find('\r\n\r\n')
        modresult = modresult[linechar + 4:]
        check = open(file, 'a')
        check.write(modresult)
        check.close()
        global lastEdit
        lastEdit = gmtime(time())
        return b"good"

#This function is used to check if we have an up to date version of the file for the client.
def gatherModify(file, timeModified):

    #We first assume we don't and request an up to date version from the server.
    proxysocket = socket(AF_INET, SOCK_STREAM)
    proxysocket.connect(('localhost',8888))
    sentence = 'GET /' + file + ' HTTP/1.1\r\nIf-Modified-Since: ' + timeModified + '\r\n\r\n'
    proxysocket.send(sentence.encode())
    result = proxysocket.recv(1024)
    modresult = result.decode()

    #We then check the received status code.
    firstSpace = modresult.find(' ')
    statusCode = modresult[firstSpace + 1:firstSpace + 4]
    
    #If we get 200 OK, that means the server has a more up to date version, so we replace our file
    #with this new one.
    #If we don't, then we got 304 Not Modified, meaning we have the most up to date version.
    if statusCode == "200":
        fileBegin = modresult.find('\r\n\r\n')
        modresult = modresult[fileBegin + 4:]
        check = open(file, 'w')
        check.write(modresult)
        check.close()
        global lastEdit
        lastEdit = gmtime(time())

#Most of this is identical to client_thread() in Web.py. I'll only comment on the differences.
def proxy_thread(conn):

    data = conn.recv(4096).decode()
    firstLine = data.find('\r\n')
    checker = data[:firstLine]
    if checker[0:3] == "GET":
        fileLast = checker.find(" HTTP")
        fileToGrab = checker[5:fileLast]

        #Here we check if we have the file, and if we don't we ask for it from the server.
        success = proxy_check(fileToGrab)

        #If everything goes well, we have the file, and thus can continue as normal.
        if success == b"good":
            if fileToGrab == lockedFile:
                response = b"HTTP/1.1 403 Forbidden\r\n\r\n"
            else:
                askedModified = data.find('If-Modified-Since:')
                if askedModified != -1:
                    dateCheck = data[askedModified:]
                    dateStart = dateCheck.find(': ')
                    dateLast = dateCheck.find('\r\n')
                    dateCheck = dateCheck[dateStart + 2:dateLast]
                    timeCheck = strptime(dateCheck, "%a, %d %b %Y %H:%M:%S GMT")

                    #Instead of bringing up a 304, we ask the server for help.
                    if timeCheck > lastEdit:
                        gatherModify(fileToGrab, dateCheck)
                try:
                    toSend = open(fileToGrab, 'rb')
                    file = toSend.read()
                    toSend.close()
                    head = b"HTTP/1.1 200 OK\r\n\r\n"
                    response = head + file
                except:
                    response = b"HTTP/1.1 404 Not Found\r\n\r\n"
        
        #If the server did not send the file to us in proxy_check(), we send the client its status code.
        else:
            response = success
    
    else:
      response = b"HTTP/1.1 400 Bad Request\r\n\r\n"
    conn.send(response)


    conn.close()
        



while True:
    clientsocket, address = s.accept()
    
    ct = Thread(target=proxy_thread,args=(clientsocket, ))
    ct.start()
