# importing libraries
from .modules import *




class stage3:
    def __init__(self,device):
        self.device = device
        self.logs = []
        print('\nStage 3: Downloading files from the device')
    
    def run(self):
        # subtasks
        self.load_dbs()
        self.add_percentage()
        self.download_files()
        self.save_logs()
    
    def load_dbs(self):
        subtask('Loading dataframes',2)
        self.dir_db = read_csv('cache\\dir_db.csv',encoding=ENC)
        self.file_db = read_csv('cache\\file_db.csv',encoding=ENC)
        subtask()
    
    def add_percentage(self):
        # function to add percentages to each file progress
        subtask('Pre-calculating percentages')
        subtask()
        total = sum(self.file_db['Size'])
        self.length = len(self.file_db)
        coeff = 0.8
        p1 = cumsum(self.file_db['Size'])*coeff*100/total
        p2 = linspace(0,((1-coeff)*100),self.length)
        p3 = list(map(lambda x: round(x[0]+x[1],2),zip(p1,p2)))
        self.file_db['Percentage'] = list(map(self.percent_format,p3))
        self.file_db['Increment'] = list(map(lambda x: round(x,2),diff(p3,prepend=0)))
        self.file_db.to_csv('cache\\file_db.csv',index=False,encoding=ENC)
    
    def percent_format(self,value):
        # function that formats percentages into proper indented strings
        value = str(value)
        prefix,suffix = value.split('.')
        prefix = ' '*(2-len(prefix))+prefix
        suffix = suffix+' '*(2-len(suffix))
        value = '.'.join([prefix,suffix])
        return value
    
    def pbar_update(self,row):
        # function that updates the download progress bar
        self.pbar.set_description_str(row.Percentage)
        self.pbar.update(row.Increment)
        iter = str(row.Index+1)
        iter = ' '*(self.post_spacing-len(iter))+iter
        self.pbar.set_postfix_str(iter)
    
    def out_dir(self,dir):
        # function that gives the output dir for ADB pull
        dir = dir.split('/')
        dir[0] = self.device
        return '\\'.join(dir)
    
    def download_files(self):
        subtask('Downloading files',2)
        print('\tRunning\n')
        self.post_spacing = len(str(self.length))
        format = '   Progress: {desc}%'+' |{bar}| {postfix}/'+f'{self.length}'+' [{elapsed}<{remaining}]'
        self.pbar = tqdm(total=sum(self.file_db['Increment']),bar_format=format)
        for i in self.dir_db.itertuples():
            dir = self.out_dir(i.Folder)
            makedir(dir)
            part = self.file_db[self.file_db['FID'] == i.Index]
            for j in part.itertuples():
                src_file = '/'.join((i.Folder,j.File))
                dst_file = '\\'.join((dir,j.File))
                op = ADB.pull(src_file,dst_file)
                if op.returncode != 0: self.logs.append(src_file+'\n')
                self.pbar_update(j)
        self.pbar.close()
    
    def save_logs(self):
        if len(self.logs):
            print('There are some failed files. Please check the logs.txt')
            with open('logs.txt','w',encoding=ENC) as file:
                file.writelines(self.logs)
        print(f'\n\nBackup complete!')