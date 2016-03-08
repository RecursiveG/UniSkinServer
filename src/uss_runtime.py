class SessionManager():
    '''track the accessToken, no interaction with database'''
    @staticmethod
    def getUUID():
        return str(uuid.uuid4()).replace('-','')
    def __init__(self):
        self.__sessions=dict()
        self.__lastcheck=time.time();
    def valid(self,token):
        if token in self.__sessions:
            if self.__sessions[token]['time']>time.time():
                return True
            else:
                del(self.__sessions[token])
                return False
        else:
            return False
    def get_name(self,token):
        return self.__sessions[token]['name'] if self.valid(token) else None
    def login(self,name):
        if self.__lastcheck + 3600 < time.time():
            self.__lastcheck=time.time()
            for t in [x for x in self.__sessions if self.__sessions[x]['time']<time.time()]:
                del(self.__sessions[t])
        uid=getUUID()
        i={'name':name,'time':time.time()+600}
        self.__sessions[uid]=i
        return uid
    def logout(self,token):
        if token in self.__sessions:
            del(self.__sessions[token])
            return True
        else:
            return False

class TextureManager():
    '''remove files when startup or file no more used, need info from database at startup time'''
    __textures=dict()
    __path='./textures/'
    def __init__(self,cursor,folder_path):
        import os
        self.__path=folder_path
        SQL='SELECT HASH_steve,HASH_alex,HASH_cape FROM users'
        res=cursor.execute(SQL)

        row=res.fetchone()
        while row!=None:
            self.plus1(row[0])
            self.plus1(row[1])
            self.plus1(row[2])
            row=res.fetchone()

        for f in os.listdir(self.__path):
            if not f in self.__textures:
                os.remove(self.__path+f)
    def plus1(self,h):
        if h==None: return
        if h in self.__textures:
            self.__textures[h]+=1
        else:
            self.__textures[h]=1
    def minus1(self,h):
        import os
        if h==None: return
        if not h in self.__textures: return
        self.__textures[h]-=1
        if self.__textures[h]==0:
            del(self.__textures[h])
            os.remove(self.__path+h)

def UniSkinAPIFormatter(database_record): pass

def WebDataFormatter(database_record): pass
