# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 22:57:38 2022

@author: Lorenzo
"""
import socket, os

class Client:
    
    def __init__(self, server_address, server_port):
        self.server_address = (server_address, server_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(3)
        self.path = os.getcwd()
        self.is_closed = False
    
    # close the socket, once called,the entire Client object must not be used anymore
    def close(self):
        self.is_closed = True
        self.socket.close()

    
    # returns a list of the names of the files in the current directory
    def show_available_files(self):
        if self.is_closed:
            raise ValueError
        return [f for f in os.listdir(self.path) if os.path.isfile(f)]

    # sends a list command to the server 
    # returns a tuple: first element is a code, 0 if successful, 1 if an error occurred 
    #         second element is a list of the names of files on the server
    #         third element is a message regarding the outcome of the operation  
    def show_files_from_server(self):
        if self.is_closed:
            raise ValueError
        try:
            self.socket.sendto('0'.encode(), self.server_address)
            server_thread, server = self.socket.recvfrom(4096)
            self.socket.sendto('1'.encode(), server)
            data, server = self.socket.recvfrom(4096)
        except socket.timeout:
            #   timeout error
            return (-1 , '', 'Error: timeout occurred')
        except ConnectionResetError:
            return (-1 , '', 'Error: server unreachable')
        return (0 , data.decode(), 'OK')
    
    # sends a put command to the server
    # returns 0 if the operation is succesful
    #         -1 if an error occurred (server unreachable)
    #         1 if file not found
    #         second element is a message regarding the outcome of the operation
    def upload(self, file_name):
        if self.is_closed:
            raise ValueError
        try:
            file = open(file_name, 'r')
            fileData = file.read()
            file.close()
            self.socket.sendto('0'.encode(), self.server_address)
            server_thread, server = self.socket.recvfrom(4096)
            self.socket.sendto(('2;' + file_name).encode(), server)
            while fileData:
                self.socket.sendto(fileData[:4096].encode(), server)
                fileData = fileData[4096:]
        except socket.timeout:
             return (-1 , 'Error: timeout occurred')
        except ConnectionResetError:
             return (-1 , 'Error: server unreachable')
        except IOError:    
            return (1, 'Error: file not found.')
        return (0 , 'OK')

    # sends a get command to the server
    # returns 0 if the operation is succesful
    #         1 if an error related to the file occurred
    #         -1 if an error related to the connection occurred
    #         second element is a message regarding the outcome of the operation
    def download(self, file_name):
        if self.is_closed:
            raise ValueError
            return (1,)
        try:
            self.socket.sendto('0'.encode(), self.server_address)
            server_thread, server = self.socket.recvfrom(4096)
            self.socket.sendto(('3;' + file_name).encode(), server)
        except socket.timeout:
            return (-1 , 'Error: timeout occurred')
        data = ' '
        fileData = ''
        try:
            while data:
                data, server = self.socket.recvfrom(4096)
                fileData = fileData + data.decode()
        except socket.timeout:
            print()
        except ConnectionResetError :
            return (-1 , 'Error: server unreachable')
        if fileData[0] == '1':
            # server couldn't find the specified file
            print('not success')
            return (1, 'Error: file not found.')
        try:
            newFile = open(file_name, 'w')
            newFile.write(fileData[2:])
            newFile.close()
        except IOError:
            return (1, 'Error: could not create file.')
        return (0 , 'OK')

