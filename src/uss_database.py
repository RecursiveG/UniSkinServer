from bsddb3 import dbshelve
import time as time_library
time=(lambda: int(time_library.time()))

def pwdhash(name,pwd):
    import hashlib
    m1=hashlib.sha1()
    m2=hashlib.sha1()
    m3=hashlib.sha512()
    m1.update(name.encode("utf8"))
    m2.update(pwd.encode("utf8"))
    m3.update(m1.digest())
    m3.update(m2.digest())
    return m3.hexdigest()

class uss_database:
    ''' this class will do what is instructed to do
    the caller is responsible for data validation '''
    db = None # dbshelve.DBShelf

    def __init__(self, database_path: str):
        self.db = dbshelve.open(database_path)
    def close(self):
        self.db.close()
        self.db = None

    def _get_user(self, username: str):
        try:
            return self.db[username.lower().encode("UTF-8")]
        except:
            return None
    def _set_user(self, username: str, data):
        self.db[username.lower().encode("UTF-8")] = data
        self.db.sync()

    def has_user(self, username: str):
        return self._get_user(username) is not None

    @staticmethod
    def _get_dynmic_default(): return {"interval": -1, "hashes": []}
    def create_user(self, username: str, passwd: str):
        hashed_passwd=pwdhash(username, passwd)
        if (self.has_user(username)): return
        gdd=self._get_dynmic_default
        data = dict(username=username, password=hashed_passwd, last_update=time(),
                    type_preference=dict(skin="off", cape="off", elytra="off"),
                    model_preference="default",
                    textures=dict(skin_default_static="", skin_default_dynamic=gdd(),
                                     skin_slim_static="",    skin_slim_dynamic=gdd(),
                                          cape_static="",         cape_dynamic=gdd(),
                                        elytra_static="",       elytra_dynamic=gdd()))
        self._set_user(username, data)

    def delete_user(self, username:str):
        if (not self.has_user(username)): return
        del db[username.encode("UTF-8")]
        db.sync();

    def change_pwd(self, username: str, passwd: str):
        hashed_passwd=pwdhash(username, passwd)
        data = self._get_user(username)
        if data is None: return
        data["password"]=hashed_passwd
        self._set_user(username, data)

    def is_passwd_match(self, username: str, passwd: str):
        data = self._get_user(username)
        if data is None: return False
        hashed_passwd=pwdhash(username, passwd)
        return data["password"]==hashed_passwd

    def set_skin_model_preference(self, username: str, model: str):
        data = self._get_user(username)
        if data is None: return
        data["model_preference"]=model
        self._set_user(username, data)

    def set_type_preference(self, username: str, type: str, preference: str):
        data = self._get_user(username)
        if data is None: return
        data["type_preference"][type]=perference
        self._set_user(username, data)

    def set_texture_hash(self, username: str, type: str, is_slim: bool, is_dynamic: bool, hash: str):
        data = self._get_user(username)
        if data is None: return
        key=type
        if type=="skin":
            key+="_slim" if is_slim else "_default"
        key+="_dynamic" if is_dynamic else "_static"
        if is_dynamic:
            data['textures'][key]['hashes'].append(hash)
        else:
            data['textures'][key]=hash
        self._set_user(username, data)

    def del_texture_hash(self, username: str, type: str, is_slim: bool, is_dynamic: bool):
        data = self._get_user(username)
        if data is None: return
        key=type
        if type=="skin":
            key+="_slim" if is_slim else "_default"
        key+="_dynamic" if is_dynamic else "_static"
        if is_dynamic:
            data['textures'][key]['hashes']=[]
            data['textures'][key]['interval']=-1
        else:
            data['textures'][key]=""
        self._set_user(username, data)

    def scan_hashes(self, hash_callback):
        '''used for TextureManager on startup'''
        for key in self.db:
            rec = self.db[key]
            hash_callback(rec["textures"]["skin_default_static"])
            hash_callback(rec["textures"]["skin_slim_static"])
            hash_callback(rec["textures"]["cape_static"])
            hash_callback(rec["textures"]["elytra_static"])
            for hash in rec["textures"]["skin_default_dynamic"]["hashes"]: hash_callback(hash)
            for hash in rec["textures"]["skin_slim_dynamic"]["hashes"]: hash_callback(hash)
            for hash in rec["textures"]["cape_dynamic"]["hashes"]: hash_callback(hash)
            for hash in rec["textures"]["elytra_dynamic"]["hashes"]: hash_callback(hash)

    def scan_user_hash(self, username: str, hash_callback):
        rec = self._get_user(username)
        if record is None: return
        hash_callback(rec["textures"]["skin_default_static"])
        hash_callback(rec["textures"]["skin_slim_static"])
        hash_callback(rec["textures"]["cape_static"])
        hash_callback(rec["textures"]["elytra_static"])
        for hash in rec["textures"]["skin_default_dynamic"]["hashes"]: hash_callback(hash)
        for hash in rec["textures"]["skin_slim_dynamic"]["hashes"]: hash_callback(hash)
        for hash in rec["textures"]["cape_dynamic"]["hashes"]: hash_callback(hash)
        for hash in rec["textures"]["elytra_dynamic"]["hashes"]: hash_callback(hash)
        
    def get_formatted(self, username, formatter):
        return formatter(self._get_user(username))
