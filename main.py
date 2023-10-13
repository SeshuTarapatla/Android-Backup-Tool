# importing scripts
from scripts import *




# program
if __name__ == '__main__':
    
    # start the tool
    initialize()
    device,id = ADB.get_device()
    
    
    # exit the tool
    safe_exit()