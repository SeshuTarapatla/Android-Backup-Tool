# importing scripts
from scripts import *




# program
if __name__ == '__main__':
    # start the tool
    initialize()
    device,id = ADB.get_device()
    config = parse_config(device)
    
    # stages
    stage1().run()
    stage2().run()
    stage3(config).run()
    
    # exit the tool
    safe_exit()