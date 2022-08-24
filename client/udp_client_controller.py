# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 15:22:37 2022

@author: Lorenzo
"""

from client import Client

main_client = Client('localhost', 10000)
options = '\nAvailable options:\r\n\r\n1. Show files in current directory.\r\n2. Show files on server.\r\n3. Upload a file.\r\n4. Download a file.\r\n5. Exit.\r\n'

option = ''

while option != '5':
    print('\n\n\n' + options)
    option = input('\nType an option:' )
    
    # list in current directory command
    if option == '1':
        files = main_client.show_available_files()
        print('\nList of files in current directory: ')
        for i in files:
            print('\n\t' + i)
    
    # execute 'list' command
    if option == '2':
        (code, data, message) = main_client.show_files_from_server()
        
        if code != 0:
            print(message)
        else:
            print('\nList of files in current directory: ')
            for i in data.split():
                print('\n\t' + i)
        
    # execute 'put' command
    if option == '3':
        file_name = input('Type the name of the file to upload: ')
        (code, message) = main_client.upload(file_name)
        if code != 0:
            print(message)
        else:
            print('Success')

    # execute 'get' command
    if option == '4':
        file_name = input('Type the name of the file to download: ')
        (code, message) = main_client.download(file_name)
        if code != 0:
            print(message)
        else:
            print('Success')

    # exit
    if option == '5':
        main_client.close()
