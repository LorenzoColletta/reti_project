# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 18:17:46 2022

@author: Lorenzo
"""
import socket
import threading, sys, signal
from server import Server

# setup socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 10000))
server_socket.settimeout(3)
threads = list()

def signal_handler(signal, frame):
    try:
        if server_socket :
            server_socket.close()
        for i in threads:
            print('killing')
            threading.pthread_sigkill(i.ident, signal.SIGINT)
    finally:
        print('\r\n Interrupt: server shutdown\r\n')
        sys.exit(0)

video_mutex = threading.Lock()
signal.signal(signal.SIGINT, signal_handler)

while(True):
    try:
        data, client = server_socket.recvfrom(1024)
        threads.insert(0, Server(client, video_mutex).start())
    except socket.timeout:
        print('')

