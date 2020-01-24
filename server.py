#  coding: utf-8 
import socketserver
import os
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# Reference: 
# L. Ratnaparkhi, “How to find the mime type of a file in python?,” Stack Overflow, 11-Dec-2019. [Online]. 
# Available: https://stackoverflow.com/questions/43580/how-to-find-the-mime-type-of-a-file-in-python. 
# [Accessed: 22-Jan-2020].

class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.data = self.data.split()
        method = self.data[0].decode('utf-8')
        if method == "GET":
            self.verifyPath()
        else:
            statusCode = "HTTP/1.1 405 Method Not Allowed\r\n"
            self.sendData(statusCode)

    def verifyPath(self):
        path = self.data[1].decode('utf-8')
        currDir = os.getcwd()
        wDir = os.path.join(currDir, "www")
        reqDir = os.path.join(wDir, path[1:])
        commonPath = os.path.commonpath([os.path.abspath(reqDir), os.path.abspath(currDir)])
        if commonPath != os.path.abspath(currDir):
            self.getErrorPage()
            return False
        if os.path.exists(reqDir):
            if os.path.isdir(reqDir):
                if not path.endswith("/"):
                    statusCode = "HTTP/1.1 301 Moved Permanently\r\n"
                    location = "Location: " + path + "/\r\n"
                    self.sendData(statusCode, location = location)
                    return False
                reqDir = os.path.join(reqDir, "index.html")
            if os.path.isfile(reqDir):
                statusCode = "HTTP/1.1 200 OK\r\n"
                self.sendData(statusCode, file = reqDir)
        else:
            self.getErrorPage()

    def getErrorPage(self):
        statusCode = "HTTP/1.1 404 Not Found\r\n"
        errorPage = os.path.join(os.getcwd(), "www/errorPage.html")
        self.sendData(statusCode, file = errorPage)
    
    def sendData(self, statusCode, location = None, file = None):
        self.request.sendall(bytearray(statusCode,'utf-8'))
        if location != None:
            self.request.sendall(bytearray(location,'utf-8'))
        if file != None:
            f = open(file, 'rb')
            data = f.read()
            f.close()
            contentLen = "Content-Length: " + str(len(data)) + "\r\n"
            mimeType = mimetypes.guess_type(file)[0]
            contentType = "Content-Type: " + mimeType + "\r\n"
            newLineChar = "\r\n"
            header = contentLen + contentType + newLineChar
            self.request.sendall(bytearray(header,'utf-8'))
            self.request.sendall(data)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
    