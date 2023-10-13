# importing libraries

from msvcrt import getch
from os import environ, getcwd, path, system
from subprocess import run
from sys import exit




# defined variables and lambda functions

exec = lambda cmd: run(cmd,capture_output=True).stdout




# defined classes and functions

def initialize():
    # function that initializes tool
    system('title Android Device Backup')
    print('Loading . . . ',end='',flush=True)
    ADB.add_path()
    ADB.start()
    system('cls')

def safe_exit():
    # ADB.stop()
    print('\nPress any key to exit . . . ',end='',flush=True)
    getch()
    exit()


class ADB:
    # class for ADB functions
    
    def add_path(dir='adb'):
        # function that add ADB to path
        adb_dir = path.join(getcwd(),dir)
        if adb_dir not in environ['PATH']:
            environ['PATH'] += f'{adb_dir};'
    
    def start():
        # starts ADB server
        exec('adb start-server')
    
    def stop():
        # stops ADB server
        exec('adb kill-server')
    
    def get_device():
        # function the get connected device details
        resp = exec('adb devices').decode().splitlines()
        if len(resp) < 3:
            print(f'No device is connected. Please refer readme.')
            safe_exit()
        else:
            id = resp[1].split('\t')[0]
            device = exec(f'adb -s {id} shell getprop ro.product.product.name').decode()[:-2]
            print(f'Device connected: {device} | ID: {id}')
            return (device,id)