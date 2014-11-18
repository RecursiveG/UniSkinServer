# -*- coding : utf-8 -*-

DEFAULT_CONFIG='''{
    "bind-ip": "0.0.0.0",
    "port": "10086",
    "admin-phrase": "badabada",
    "uuid-bind": false,
    "allow-reg": true,
    "allow-cape": true
}
'''
URL_PREFIX='http://localhost:10086'

def getUUID():
    import uuid
    return str(uuid.uuid4()).replace('-','')
        
from time import time
class SessionManager():
    def __init__(self):
        self.__sessions=dict()
    def valid(self,token):
        return token in self.__sessions and self.__sessions[token]['time']<time()
    def get_name(self,token):
        return self.__sessions[token]['name'] if self.valid(token) else None
    def login(self,name):
        uid=getUUID()
        i={'name':name,'time':time()}
        self.__sessions[uid]=i
        return uid
        
import hashlib,json
class UserInfo():
    def __hash_pwd(self,pwd):
        m1=hashlib.sha1()
        m2=hashlib.sha1()
        m3=hashlib.sha512()
        m1.update(self.name.encode("utf8"))
        m2.update(pwd.encode("utf8"))
        m3.update(m1.digest())
        m3.update(m2.digest())
        return m3.hexdigest()
    def __init__(self,name,pwd):
        self.name=name;
        self.pwd=self.__hash_pwd(pwd)
        self.preference=["steve","alex"]
        self.models=dict(steve="",alex="",cape="")
        self.uid=getUUID()
    def getLegacySkin(self):
        if self.models['steve']=="":
            return ""
        else:
            return "%s/textures/%s.png"%(URL_PREFIX,self.models['steve'])
    def getLegacyCape(self):
        if self.models['cape']=="":
            return ""
        else:
            return "%s/textures/%s.png"%(URL_PREFIX,self.models['cape'])
    def uuid_match(self,uid):
        return self.uid.lower()==uid.lower()
    def passwd_match(self,pwd):
        return self.pwd==self.__hash_pwd(pwd)
        
    def toJson(self):
        l=dict()
        for key in self.models:
            if(self.models[key]!=""):
                l[key]="%s/textures/%s.png"%(URL_PREFIX,self.models[key])
        d=dict(player_name=self.name,last_update=time(),uuid=self.uid,model_preference=self.preference,models=l)
        return json.dumps(d)
    def get_web_data(self):
        return self.toJson()
        
    def update_uuid(self,uuid):
        uid=uuid.replace('-','').lower()
        if len(uid)!=32:
            raise Exception("UUID Length not match")
        self.uid=uid
    def update_prefer(self,p):
        prefer=p.split('|')
        default_prefer=['steve','alex']
        fin=[x for x in prefer if x in default_prefer]
        for x in default_prefer:
            if not x in fin:
                fin.append(x)
        self.preference=fin
    def chpwd(self,login,cur,pwd):
        if self.name==login and self.passwd_match(cur):
            self.pwd=self.__hash_pwd(pwd)
            return True
        else:
            return False
    def update_model(self,model,hash_name):
        if model in self.models:
            self.models[model]=hash_name
            
import pickle
class user_data:
    def __init__(self,data_file_path):
        self.__data=pickle.load(open(data_file_path,"rb"))
        self.__data_path=data_file_path
        
    def exists(self,player_name):
        return player_name in self.__data
        
    def get(self,name):
        return self.__data[name]

    def new_user(self,name,pwd):
        self.__data[name]=UserInfo(name,pwd)
        
    def sync(self):
        pickle.dump(self.__data,open(self.__data_path,'wb'))
        
class server_config:
    def __init__(self,file_path):
        f=open(file_path)
        config=json.loads(f.read())
        self.ip=config["bind-ip"]
        if self.ip=="":
            self.ip="0.0.0.0"
        self.port=int(config["port"])
        self.admin_phrase=config["admin-phrase"]
        self.uuid_bind=config["uuid-bind"]
        self.allow_reg=config["allow-reg"]
        self.allow_cape=config["allow-cape"]
        self.texture_path=config["texture-folder"]
        self.database_path=config["database"]

        
def getConfigure(file_path="server_config.json"):
    try:
        import os
        if not os.path.exists(file_path):
            f=open(file_path,"w")
            f.write(DEFAULT_CONFIG)
            f.close()
        cfg=server_config(file_path)
        if not os.path.exists(cfg.database_path):
            pickle.dump(dict(),open(cfg.database_path,'wb'))
        cfg.user_data=user_data(cfg.database_path)
    except Exception as e:
        print(e)
        return None
    return cfg

if __name__=="__main__":
    print("Do not excute me alone!")
