import time

class SessionManager():
    '''track the accessToken, no interaction with database
       session: {
         'token1': {
           'time': expire time
           'name': playername
         },
         ...
       }
    '''

    def __init__(self, expire_time: int):
        self.__sessions=dict()
        self.__lastcheck=time.time()
        self.expire=expire_time
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
        import uuid
        get_uuid=(lambda: str(uuid.uuid4()).replace('-',''))
        uid=get_uuid()
        i={'name':name,'time':time.time()+self.expire}
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

    def __init__(self, folder_path):
        self.__path=folder_path

    def inc_hash(self,h):
        if h==None or h=="": return
        if h in self.__textures:
            self.__textures[h]+=1
        else:
            self.__textures[h]=1

    def dec_hash(self,h):
        import os
        if h==None or h=="": return
        if not h in self.__textures: return
        self.__textures[h]-=1
        if self.__textures[h]==0:
            del(self.__textures[h])
            os.remove(self.__path+h)

    def force_clean(self):
        import os
        for f in os.listdir(self.__path):
            if not f in self.__textures:
                os.remove(self.__path+f)

def UniSkinAPIFormatter(record):
    import json
    data = dict(player_name=record["username"],
                last_update=record["last_update"])
    perf_list=list()
    if record["type_preference"]["skin"]=='static':
        if record["model_preference"]=="slim":
            perf_list=["slim", "default", "slim_dynamic", "default_dynamic"]
        else:
            perf_list=["default", "slim", "default_dynamic", "slim_dynamic"]
    elif record["type_preference"]["skin"]=='dynamic':
        if record["model_preference"]=="slim":
            perf_list=["slim_dynamic", "default_dynamic", "slim", "default"]
        else:
            perf_list=["default_dynamic", "slim_dynamic", "default", "slim"]
    if record["type_preference"]["cape"]=="static":
        perf_list.append("cape")
    elif record["type_preference"]["cape"]=="dynamic":
        perf_list.append("cape_dynamic")
    if record["type_preference"]["elytra"]=="static":
        perf_list.append("elytra")
    elif record["type_preference"]["elytra"]=="dynamic":
        perf_list.append("elytra_dynamic")
    data["model_preference"]=perf_list

    good = (lambda x: x is not None and x!="")
    skins = dict()
    s = record["textures"]["skin_default_static"]
    if good(s): skins["default"]=s
    s = record["textures"]["skin_slim_static"]
    if good(s): skins["slim"]=s
    s = record["textures"]["cape_static"]
    if good(s):
        skins["cape"]=s
        data["cape"]=s
    s = record["textures"]["elytra_static"]
    if good(s): skins["elytra"]=s

    good = (lambda x: len(x["hashes"])>0 and x["interval"]>0)
    join = (lambda x: str(x["interval"]+","+",".join(x["hashed"])))
    s = record["textures"]["skin_default_dynamic"]
    if good(s): skins["default_dynamic"]=join(s)
    s = record["textures"]["skin_slim_dynamic"]
    if good(s): skins["slim_dynamic"]=join(s)
    s = record["textures"]["cape_dynamic"]
    if good(s): skins["cape_dynamic"]=join(s)
    s = record["textures"]["elytra_dynamic"]
    if good(s): skins["elytra_dynamic"]=join(s)

    data["skins"] = skins
    return json.dumps(data)

def WebDataFormatter(database_record):
    del database_record["password"]
    return json.dumps(database_record)
