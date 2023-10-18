# importing libraries
from .modules import *




class stage3:
    def __init__(self,config):
        self.mode = config['mode']
        self.outdir = path.join(config['output'],config['device'])
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
        order = [['FID'],['Category'],['Category','Type']][self.mode]
        self.file_db.sort_values(by=order,inplace=True,ignore_index=True)
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
    
    def download_files(self):
        subtask('Downloading files',2)
        print('\tRunning')
        # self.make_outdirs()
        self.set_pbar()
        download = [self.mode_0,self.mode_1,self.mode_2][self.mode]
        download()
        self.pbar.close()
    
    def make_outdirs(self):
        # function that creates output folders based on mode
        if self.mode == 0:
            create_dir = lambda x:  makedir('\\'.join([self.outdir]+x.split('/')[1:]))
            self.dir_db['Folder'].apply(create_dir)
        elif self.mode == 1:
            create_dir = lambda x: makedir('\\'.join([self.outdir,x]))
            list(map(create_dir,self.file_db['Category'].unique()))
        elif self.mode == 2:
            create_dir = lambda x,y: makedir('\\'.join([self.outdir,x,y]))
            for category in self.file_db['Category'].unique():
                types = self.file_db[self.file_db['Category'] == category]['Type'].unique()
                list(map(lambda x: create_dir(category,x),types))
    
    def set_pbar(self):
        # function that creats a progress bar for download task
        self.post_spacing = len(str(self.length))
        format = '   Progress: {desc}%'+' |{bar}| {postfix}/'+f'{self.length}'+' [{elapsed}<{remaining}]'
        self.pbar = tqdm(total=sum(self.file_db['Increment']),bar_format=format)
    
    def update_pbar(self,row):
        # function that updates the download progress bar
        self.pbar.set_description_str(row.Percentage)
        self.pbar.update(row.Increment)
        iter = str(row.Index+1)
        iter = ' '*(self.post_spacing-len(iter))+iter
        self.pbar.set_postfix_str(iter)
    
    def mode_0(self):
        for dir in self.dir_db.itertuples():
            dst_dir = '\\'.join([self.outdir]+dir.Folder.split('/')[1:])
            makedir(dst_dir)
            part = self.file_db[self.file_db['FID'] == dir.Index]
            for file in part.itertuples():
                src_file = '/'.join([dir.Folder,file.File])
                dst_file = '\\'.join([dst_dir,file.File])
                self.safe_download(src_file,dst_file,file)
    
    def mode_1(self):
        for category in self.file_db['Category'].unique():
            dst_dir = '\\'.join([self.outdir,category])
            makedir(dst_dir)
            part = self.file_db[self.file_db['Category'] == category]
            for file in part.itertuples():
                src_dir = self.dir_db.iloc[file.FID].Folder
                src_file = '/'.join([src_dir,file.File])
                dst_file = '\\'.join([dst_dir,file.File])
                self.safe_download(src_file,dst_file,file)

    def mode_2(self):
        for category in self.file_db['Category'].unique():
            part1 = self.file_db[self.file_db['Category'] == category]
            for type in part1['Type'].unique():
                dst_dir = '\\'.join([self.outdir,category,type])
                makedir(dst_dir)
                part = part1[part1['Type'] == type]
                for file in part.itertuples():
                    src_dir = self.dir_db.iloc[file.FID].Folder
                    src_file = '/'.join([src_dir,file.File])
                    dst_file = '\\'.join([dst_dir,file.File])
                    self.safe_download(src_file,dst_file,file)
    
    def safe_download(self,src,dst,file):
        # function to safely downloades files checking with exisiting files
        if path.isfile(dst):
            resp = self.safe_copy(src,dst,file)
        else:
            resp = ADB.pull(src,dst).returncode
        if resp != 0: self.logs.append(f'{src}\n')
        self.update_pbar(file)
    
    def safe_copy(self,src,dst,file):
        # function to safely copy files with same names
        if path.getsize(dst) == file.Size:
            return 0
        else:
            ADB.pull(src,'Cache')
            dst = filename(dst)
            while True:
                dst.suffix += 1
                out = dst.filename()
                if path.isfile(out):
                    if path.getsize(out) == file.Size:
                        return 0
                else:
                    move(f'Cache\\{file.File}',out)
                    return 0
    
    def save_logs(self):
        subtask('Saving database logs',2)
        self.dir_db.to_excel(f'{self.outdir}\\dir_db.xlsx',index=False)
        self.file_db.to_excel(f'{self.outdir}\\file_db.xlsx',index=False)
        if len(self.logs):
            with open(f'{self.outdir}\\logs.txt','w',encoding=ENC) as file:
                file.writelines(self.logs)
            subtask()
            print('\nThere are some failed files. Please check logs.txt in Backup directory.\n\nBackup complete!')
            return
        subtask()
        print('\n\nBackup complete!')
        