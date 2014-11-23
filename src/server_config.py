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
import uuid,sqlite3,os,sys,json,time


def getUUID():
    return str(uuid.uuid4()).replace('-','')

class SessionManager():
    def __init__(self):
        self.__sessions=dict()
    def valid(self,token):
        return token in self.__sessions and self.__sessions[token]['time']<time.time()
    def get_name(self,token):
        return self.__sessions[token]['name'] if self.valid(token) else None
    def login(self,name):
        uid=getUUID()
        i={'name':name,'time':time.time()}
        self.__sessions[uid]=i
        return uid

class UserInfoFactory():
    def toPublicProfile(record):
        import json
        obj=dict(player_name=record[0],last_update=record[3],uuid=record[1])
        if record[4]!=None:
            obj["model_preference"]=record[4].split('|')
        else:
            obj["model_preference"]=list('default','slim')
        if record[7]!=None:
            obj["cape"]=record[7]
        skins=dict()
        if record[6]!=None:
            skins["default"]=record[6]
        if record[5]!=None:
            skins["slim"]=record[5]
        obj['skins']=skins
        return json.dumps(obj)
    def toWebProfile(rec):
        import json
        models=dict()
        if rec[5]!=None: models['slim']=rec[5]
        if rec[6]!=None: models['default']=rec[6]
        if rec[7]!=None: models['cape']=rec[7]
        obj=dict(player_name=rec[0],uuid=rec[1],model_preference=rec[4].split('|'),models=models)
        return json.dumps(obj)

    def pwd_hash(name,pwd):
        import hashlib
        m1=hashlib.sha1()
        m2=hashlib.sha1()
        m3=hashlib.sha512()
        m1.update(name.encode("utf8"))
        m2.update(pwd.encode("utf8"))
        m3.update(m1.digest())
        m3.update(m2.digest())
        return m3.hexdigest()

class DatabaseProvider():
    ''' sqlite3 database backend '''
    def __init__(self,file_path):
        CREATE_SQL='''CREATE TABLE IF NOT EXISTS users(
          name  TEXT NOT NULL PRIMARY KEY UNIQUE,
          uuid  TEXT NOT NULL UNIQUE,
          pwd   TEXT NOT NULL,
          last_update INT NOT NULL,
          preference TEXT,
          HASH_alex  TEXT,
          HASH_steve TEXT,
          HASH_cape  TEXT
        );'''
        if not os.path.exists(file_path):
            conn=sqlite3.connect(file_path)
            c=conn.cursor();
            conn.execute(CREATE_SQL)
            conn.commit()
            conn.close()
        self.__conn=sqlite3.connect(file_path)
        self.__cursor=self.__conn.cursor()
    def __getRecordByName(self,name):
        SQL="SELECT * FROM users WHERE name=?"
        return self.__cursor.execute(SQL,(name,)).fetchone()
    def user_exists(self,name):
        return self.__getRecordByName(name)!=None
    def getLegacySkin(self,name):
        res=self.__getRecordByName(name)
        return None if res==None else res[6]
    def getLegacyCape(self,name):
        res=self.__getRecordByName(name)
        return None if res==None else res[7]
    def user_json(self,name):
        u=self.__getRecordByName(name)
        return UserInfoFactory.toPublicProfile(u)
    def new_user(self,name,pwd):
        SQL=r'INSERT INTO users VALUES(?,?,?,?,?,NULL,NULL,NULL)'
        self.__cursor.execute(SQL,(name,getUUID(),UserInfoFactory.pwd_hash(name,pwd),int(time.time()),"default|slim"))
        self.__conn.commit()
    def isValid(self,name,pwd):
        SQL="SELECT * FROM users WHERE name=? AND pwd=?"
        res=self.__cursor.execute(SQL,(name,UserInfoFactory.pwd_hash(name,pwd),))
        return res!=None;
    def user_json_web(self,name):
        rec=self.__getRecordByName(name)
        return UserInfoFactory.toWebProfile(rec)
    def remove_skin(self,name,skin_type):
        SQL=r'UPDATE users SET %s=NULL, last_update=? WHERE name=?'
        column=""
        if skin_type=="slim": column="HASH_alex"
        if skin_type=="default": column="HASH_steve"
        if skin_type=="cape": column="HASH_cape"
        if column=="":return
        SQL=SQL%column
        self.__cursor.execute(SQL,(int(time.time()),name))
        self.__conn.commit()
    def update_model(self,name,skin_type,hex_name):
        SQL=r'UPDATE users SET %s=?, last_update=? WHERE name=?'
        column=""
        if skin_type=="slim": column="HASH_alex"
        if skin_type=="default": column="HASH_steve"
        if skin_type=="cape": column="HASH_cape"
        if column=="":return
        SQL=SQL%column
        self.__cursor.execute(SQL,(hex_name,int(time.time()),name))
        self.__conn.commit()
    def change_pwd(self,name,pwd):
        SQL="UPDATE users SET pwd=? WHERE name=?"
        self.__cursor.execute(SQL,(UserInfoFactory.pwd_hash(name,pwd),name,))
        self.__conn.commit()
    def update_uuid(self,name,u):
        SQL="UPDATE users SET uuid=?, last_update=? WHERE name=?"
        self.__cursor.execute(SQL,(u,int(time.time()),name,))
        self.__conn.commit()
    def update_preference(self,name,p):
        SQL="UPDATE users SET preference=?, last_update=? WHERE name=?"
        self.__cursor.execute(SQL,(p,int(time.time()),name,))
        self.__conn.commit()



class server_config:
    def __init__(self,file_path):
        import json
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
    except Exception as e:
        print(e)
        return None
    return cfg

if __name__=="__main__":
    print("Do not excute me alone!")
