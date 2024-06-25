from socket import *
from threading import *
from time import *

#NEXT UP: ISSUE WITH UPDATING FILE ON PROXY
#ISSUE WITH CURL AND TIME MODIFIED. FIGURE OUT. MANUAL TESTING WORKS.

#Global variables
host = ''
port = 8888
lockedFile = 'locked.html'
lastEdit = gmtime(time())

#Create server socket
s = socket(AF_INET, SOCK_STREAM)
s.bind((host, port))
s.listen(5)
#print(s)

#This function is for debug purposes and in a real server would not exist.
#It continuously waits for input to add to the test.html file.
def update_file():
  while True:
    toAdd = input('Please write what to add to the file:')
    #'w' is used to signify it's appending.
    writer = open('test.html', 'w')
    writer.write("""<!DOCTYPE html>
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
  <p>%s</p>
</body>

</html>""" % toAdd)
    writer.close()
    global lastEdit
    lastEdit = gmtime(time())

#This function is the meat and bones of the actual server. When a client connects, they go through this.
def client_thread(conn):

    #Receive data.
    data = conn.recv(4096).decode()
    #print(data)
    yesModify = True

    #Find where the first line of the data (so the actual command) should be.
    firstLine = data.find('\r\n')
    checker = data[:firstLine]

    #In our simple server, we are only checking for the GET command. All others result in 400 error.
    if checker[0:3] == "GET":

      #This finds the file we need to grab for the client.
      fileLast = checker.find(" HTTP")
      fileToGrab = checker[5:fileLast]

      #If it's locked, we say it's not allowed.
      if fileToGrab == lockedFile:
        response = b"HTTP/1.1 403 Forbidden\r\n\r\n"
      
      #Otherwise....
      else:

        #So this complex bit of code finds if we have an If-Modified-Since condition.
        #If we do, we then convert the time into readable time....
        askedModified = data.find('If-Modified-Since:')
        if askedModified != -1:
          dateCheck = data[askedModified:]
          dateStart = dateCheck.find(': ')
          dateLast = dateCheck.find('\r\n')
          dateCheck = dateCheck[dateStart + 2:dateLast]
          #Very complex but this makes sure it gets the right time.
          timeCheck = strptime(dateCheck, "%a, %d %b %Y %H:%M:%S GMT")

          #Compare our request to when our file was last modified. If it was modified prior to
          #the requested time, we bring up a 304 error.
          if timeCheck > lastEdit:
            response = b"HTTP/1.1 304 Not Modified\r\n\r\n"
            yesModify = False
        
        #If we are all fine, we grab the file itself.
        if(yesModify):
          try:
            toSend = open(fileToGrab, 'rb')
            file = toSend.read()
            toSend.close()
            #print("closed")
            head = b"HTTP/1.1 200 OK\r\n\r\n"
            response = head + file
            #print("done")
          
          #This except statement only fails if open(fileToGrab, 'rb') gives an error. Meaning
          #the file does not exist.
          except:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"
    
    #For example, POST would cause this to send.
    else:
      response = b"HTTP/1.1 400 Bad Request\r\n\r\n"



    #test = open('test.html','rb')
    #file = test.read()
    #test.close()

    

    #head = b"HTTP/1.1 200 OK\r\n\r\n"
    #response = head + file

    #Whatever our result, we send the result back and close the connection.
    conn.send(response)


    conn.close()
        

#This thread makes sure the update_file() function goes on forever.
uf = Thread(target=update_file)
uf.start()

#Wait and connect to TCP connections that arrive, then repeat.
while True:
    clientsocket, address = s.accept()
    
    ct = Thread(target=client_thread,args=(clientsocket, ))
    #NOT SURE THIS PART WORKS RIGHT
    ct.start()
