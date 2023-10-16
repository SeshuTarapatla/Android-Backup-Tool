# importing libraries
from .modules import *




class stage2:
    def __init__(self):
        print('\nStage 2: Refining device data into dataframes')
        self.dir_db = DataFrame(columns=['Folder','Count','Size'])
        self.file_db = DataFrame(columns=['File','FID','Type','Category','Size','Date'])
        self.categories = categories()
        with open('data\\ignore.txt') as file:
            self.ignore = file.read().splitlines()
    
    def run(self):
        # subtasks
        self.read_db()
        self.parse_db()
        self.categorize()
        self.refine_db()
        self.save_dbs()
        pass
    
    def read_db(self):
        subtask('Reading device data',2)
        with open('cache\\file_data.bin','r',encoding=ENC) as file:
            self.bin_data = file.read().split('\n'*2)
        subtask()
    
    def parse_db(self):
        subtask('Parsing device data',2)
        list(map(self.parse_dir,self.bin_data))
        subtask()
    
    def parse_dir(self,dir):
        # function that parses directory db
        data = dir.splitlines()
        dir = 'sdcard' + data[0][1:-1]
        files = data[2:]
        count,size = self.parse_files(files)
        if count:
            part = DataFrame([[dir,count,size]],columns=['Folder','Count','Size'])
            self.dir_db = concat([self.dir_db,part],ignore_index=True)
    
    def parse_files(self,files):
        # function that parses files db
        files = list(map(self.parse_row,files))
        files = list(filter(lambda x:x,files))
        if files:
            part = DataFrame(files,columns=['File','Type','Size','Date'])
            part['FID'] = len(self.dir_db)
            self.file_db = concat([self.file_db,part],ignore_index=True)
            count = len(part)
            size = sum(part['Size'])
            return (count,size)
        return (0,0)
    
    def parse_row(self,row):
        # function that parses one row (file)
        data = row.split()
        name = ' '.join(data[6:])
        type = path.splitext(name)[1][1:].lower()
        if type:
            name = f'{data[6]}{data[6].join(row.split(data[6])[1:])}'
            size = int(data[3])
            date = ' '.join(data[4:6])
            return (name,type,size,date)
        return None
    
    def save_dbs(self):
        subtask('Saving parsed dataframes')
        self.dir_db.to_csv('cache\\dir_db.csv',index=False,encoding=ENC)
        self.file_db.to_csv('cache\\file_db.csv',index=False,encoding=ENC)
        subtask()
    
    def categorize(self):
        subtask('Categorizing files',2)
        types = set(self.file_db['Type'])
        new_types = types - self.categories.alltypes
        if new_types:
            print(f'\tFailed\n')
            with open('data\\new_types.txt','w') as file:
                file.write('\n'.join(sorted(new_types)))
            print(f'There are unrecognized file types. Add them to category database. Please refer readme.')
            safe_exit()
        req_types = types.intersection(self.categories.filetypes)
        for type in req_types:
            part = self.file_db[self.file_db['Type'] == type]
            self.file_db.loc[part.index,'Category'] = self.categories.get_category(type)
        subtask()
    
    def refine_db(self):
        subtask('Refining dataframes',2)
        
        # removing cache files
        self.file_db['Category'].fillna('',inplace=True)
        part = self.file_db[self.file_db['FID'] == 0]
        files = part['File'].to_list()
        cache = ['file_data.sh','file_data.bin']
        for file in cache:
            if file in files:
                index = part[part['File'] == file].index
                self.file_db.loc[index,'Category'] = ''
        
        # removing thumbnail files
        dirs = self.dir_db[self.dir_db['Folder'].apply(lambda x: x.endswith('.thumbnails'))]
        for fid in dirs.index:
            part = self.file_db['FID'] == fid
            self.file_db.loc[part,'Category'] = ''
        
        # removing ignore files:
        for dir in self.ignore:
            fid = self.dir_db[self.dir_db['Folder'] == dir]
            if len(fid):
                part = self.file_db['FID'] == fid.index[0]
                self.file_db.loc[part,'Category'] = ''
        
        # new dataframes
        db1 = DataFrame(columns=self.dir_db.columns)
        db2 = DataFrame(columns=self.file_db.columns)
        
        # removing files that aren't categorized
        for dir in self.dir_db.itertuples():
            part = self.file_db[self.file_db['FID'] == dir.Index]
            part = part[part['Category'] != '']
            if len(part):
                part['FID'] = len(db1)
                dir = DataFrame([[dir.Folder,len(part),sum(part['Size'])]],columns=self.dir_db.columns)
                db1 = concat([db1,dir],ignore_index=True)
                db2 = concat([db2,part],ignore_index=True)
        
        # updating the new dataframes
        self.dir_db = db1
        self.file_db = db2
        subtask()
