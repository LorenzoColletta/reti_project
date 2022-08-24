import socket, os, signal, sys
import threading

class Server(threading.Thread):
    def __init__(self, client_address, video_mutex):
        # setup socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_mutex = video_mutex
        self.socket.settimeout(3)
        self.client_address = client_address
        self.path = os.getcwd()
        signal.signal(signal.SIGINT, self.__signal_handler)
        threading.Thread.__init__(self)        

    def __signal_handler(self, signal, frame):
        try:
          if self.socket :
            self.socket.close()
        finally:
            self.video_mutex.acquire()
            print('\r\n Interrupt: server shutdown\r\n')
            self.video_mutex.release()
            sys.exit(0)

    def run(self):
        self.socket.sendto('0'.encode(), self.client_address)
        try:
            # waiting for command
            (data, client) = self.socket.recvfrom(4096)
        except socket.timeout:
            self.socket.close()
            sys.exit(0)
        except ConnectionResetError:    
            self.socket.close()
            sys.exit(0)
            
        # execute 'list' command
        if data.decode()[0] == '1':
            log = 'List: list command received'
            files = [f for f in os.listdir(self.path) if os.path.isfile(f)]
            self.socket.sendto(' '.join(files).encode(), client)
        
        # execute 'put' command
        if data.decode()[0] == '2':
            file_name = data.decode()[2:]
            log = 'Put: receiving '  + file_name
            try:
                fileData = ''
                dataReceived = ' '
                while dataReceived:
                    dataReceived, server = self.socket.recvfrom(4096)
                    fileData = fileData + dataReceived.decode()
            except socket.timeout:
                #   timeout error
                log = log + '\nError: timeout occurred'
            except ConnectionResetError :
                log = log + '\nError: server unreachable'
            success = True
            try:
                newFile = open(file_name, 'w')
                newFile.write(fileData)
                newFile.close()
            except IOError:
                success = False
                log = log +'\nError: could not create file.'
            if success:
                log = log + '\nSuccess: file downloaded'


        # execute 'get' command
        if data.decode()[0] == '3':
            file_name = data.decode()[2:]
            log = 'Put: sending ' + file_name
            success = True
            try:
                file = open(file_name, 'r')
                fileData = '0;'
                fileData = fileData + file.read()
                file.close()
                while fileData:
                    self.socket.sendto(fileData[:4096].encode(), client)
                    fileData = fileData[4096:]
            except socket.timeout:
                #   timeout error
                # self.is_server_reachable = False
                success = False
                log = log + '\nError: timeout occurred'
            except ConnectionResetError:
                # self.is_server_reachable = False
                success = False
                log = log + '\nError: server unreachable'
            except IOError:
                success = False
                log = log + '\nError: file not found.'
                self.socket.sendto('1;'.encode(), client)
            if success:
                log = log + '\nSuccess: file uploaded'
            
        self.socket.close()
        self.video_mutex.acquire()
        print(log)
        self.video_mutex.release()
