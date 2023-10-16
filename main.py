# importing scripts
from scripts import *




# program
if __name__ == '__main__':
    # start the tool
    initialize()
    device,id = ADB.get_device()
    config = parse_config(device)
    print(config)
    safe_exit()
    
    # stages
    stage1().run()
    stage2().run()
    stage3(device).run()
    
    # exit the tool
    safe_exit()