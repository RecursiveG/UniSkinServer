from bsddb3 import dbshelve
import time as time_library
time=(lambda: int(time_library.time()))

class uss_database:
    ''' this class will do what is instructed to do
    the caller is responsible for data validation '''
    db = None # dbshelve.DBShelf

    def __init__(self: usm_database, database_path: str):
        self.db = dbshelve.open(database_path)

    def _get_user(self, username: str):
        try:
            return db[username.lower().encode("UTF-8")]
        except:
            return None
    def _set_user(self, username: str, data) -> NoneType:
        db[username.lower().encode("UTF-8")] = data
        db.sync()

    def has_user(self, username: str) -> bool:
        return self._get_user(username) is not None

    @staticmethod
    def _get_dynmic_default(): return {"interval": -1, "hashes": []}
    def create_user(self, username: str, hashed_passwd: str) -> NoneType:
        if (self.has_user(username)): return
        data = dict(username=username, password=hashed_passwd, last_update=time(),
                    type_preference=dict(skin="off", cape="off", elytra="off"),
                    model_preference="default",
                    textures=dict(skin_default_static="", skin_default_dynamic=_get_dynamic_default(),
                                     skin_slim_static="",    skin_slim_dynamic=_get_dynamic_default(),
                                          cape_static="",         cape_dynamic=_get_dynamic_default(),
                                        epytra_static="",       elytra_dynamic=_get_dynamic_default()))
        self._set_user(username, data)

    def delete_user(self, username:str) -> NoneType:
        if (not self.has_user(username)): return
        del db[username.encode("UTF-8")]
        db.sync();

    def change_pwd(self, username: str, hashed_passwd: str) -> NoneType:
        data = self._get_user(username)
        if data is None: return
        data["password"]=hashed_passwd
        self._set_user(username, data)

    def is_hashed_passwd_match(self, username: str, hashed_passwd: str) -> bool:
        data = self._get_user(username)
        if data is None: return False
        return data["password"]==hashed_passwd

    def set_skin_model_preference(self, username: str, model: str) -> NoneType:
        data = self._get_user(username)
        if data is None: return
        data["model_preference"]=model
        self._set_user(username, data)

    def set_type_preference(self, username: str, type: str, preference: str) -> NoneType:
        data = self._get_user(username)
        if data is None: return
        data["type_preference"][type]=perference
        self._set_user(username, data)

    def set_hash(self, username: str, type: str, is_slim: bool, is_dynamic: bool, hash: str) -> NoneType:
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

    def del_hash(self, username: str, type: str, is_slim: bool, is_dynamic: bool) -> NoneType:
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

    def get_hash_statistics(self):
        '''used for TextureManager on startup'''
        pass
