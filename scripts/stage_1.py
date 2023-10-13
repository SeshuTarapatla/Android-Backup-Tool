# importing libraries
from .modules import *




class stage1:
    def __init__(self):
        print(f'\nStage 1: Fetching file data from android device')
        makedir('cache')
        self.make_script()
    
    def run(self):
        # subtasks
        self.push_script()
        self.exec_script()
        self.pull_data()
        self.clear_cache()
    
    def make_script(self):
        commands = [
            "cd /sdcard\n",
            "ls -R -alg | grep -v '^d' > file_data.bin\n"
        ]
        with open('cache\\file_data.sh','w',newline='\n') as file:
            file.writelines(commands)
    
    def push_script(self):
        subtask('Pushing script to device')
        ADB.push('cache\\file_data.sh','sdcard/')
        subtask()
    
    def exec_script(self):
        subtask('Executing script in device')
        exec('adb shell sh sdcard/file_data.sh')
        subtask()
    
    def pull_data(self):
        subtask('Pulling device data',2)
        ADB.pull('sdcard/file_data.bin','cache')
        subtask()
    
    def clear_cache(self):
        subtask('Clear device cache',2)
        cache = ['sdcard/file_data.sh','sdcard/file_data.bin']
        list(map(ADB.remove,cache))
        subtask()