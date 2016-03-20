import tornado.web
import tornado.options
import tornado.ioloop
from tornado.web import RequestHandler
import logging

def capture_post(*args, **args_with_default):
    def real_wrapper(wrapped_func):
        def new_func(handler):
            argument_dict=dict()
            for arg in args:
                try:
                    x = handler.get_argument(arg)
                    argument_dict[arg]=x
                except tornado.web.MissingArgumentError:
                    handler.write('{"errno": 6, "msg":"Missing argument: %s"}'%arg)
                    argument_dict = None
                if (argument_dict is None): return;
            for arg in args_with_default:
                try:
                    x = handler.get_argument(arg)
                    argument_dict[arg]=x
                except tornado.web.MissingArgumentError:
                    argument_dict[arg]=args_with_default[arg]
            ret = wrapped_func(handler, **argument_dict)
            if type(ret) is tuple and len(ret)==2 and type(ret[0]) is int and type(ret[1]) is str:
                handler.write('{"errno":%d,"msg":"%s"}'%ret)
            else:
                return ret
        return new_func
    return real_wrapper

def check_token(orig_func):
    def new_func(handler, **args):
        if "token" in args:
            name = sessionManager.get_name(args["token"])
            if name is not None:
                args["name_by_token"] = name
                return orig_func(handler, **args)
        handler.write('{"errno":1,"msg":"Bad token"}')
    return new_func


class TexturesHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self,path):
        self.set_header("Content-Type", "image/png")

class UserProfileHandler(RequestHandler):
    def get(self, player_name):
        if (not db.has_user(player_name)):
            self.set_status(404)
            return
        self.write(db.get_formatted(player_name, uss_runtime.UniSkinAPIFormatter))

class WebRegisterHandler(RequestHandler):
    @capture_post("login","passwd")
    def post(self, login, passwd):
        if not cfg["allow-reg"]:
            self.write('{"errno":7,"msg":"reg not allowed"}')
            return
        name = login
        if db.has_user(name):
            self.write('{"errno":5,"msg":"already registered"}')
            return
        if len(name)<=0:
            self.write('{"errno":3,"msg":"invalid name"}')
            return
        if len(passwd)<4:
            self.write('{"errno":2,"msg":"invalid pwd"}')
            return
        db.create_user(name,passwd)
        self.write('{"errno":0,"msg":""}')

class WebLoginHandler(RequestHandler):
    @capture_post("login","passwd")
    def post(self, login, passwd):
        if not db.is_passwd_match(login,passwd):
            self.write('{"errno":1,"msg":"invalid login"}')
        else:
            token=sessionManager.login(login)
            self.write('{"errno":0,"msg":"%s"}'%token)

class WebLogoutHandler(RequestHandler):
    @capture_post("token")
    @check_token
    def post(self, token, name_by_token):
        sessionManager.logout(token)
        self.write('{"errno":0,"msg":""}')

class WebDataAccessHandler(RequestHandler):
    @capture_post("token")
    @check_token
    def post(self, token, name_by_token):
        self.write(db.get_formatted(name_by_token, uss_runtime.WebDataFormatter))

class WebAccountDelHandler(RequestHandler):
    @capture_post("token","current_passwd","login")
    @check_token
    def post(self, token, current_passwd, login, name_by_token):
        if not name_by_token==login:
            return 6, "login not match"
        if not db.is_passwd_match(name_by_token, current_passwd):
            return 1, "bad password"
        db.scan_user_hash(name_by_token, (lambda x: texture_cache.dec_hash(x)))
        db.delete_user(name_by_token)
        return 0,""

class WebChangePasswordHandler(RequestHandler):
    @capture_post("token","current_passwd","login","new_passwd")
    @check_token
    def post(self, token, current_passwd, login, new_passwd, name_by_token):
        if not name_by_token==login:
            return 6, "login not match"
        if not db.is_passwd_match(name_by_token, current_passwd):
            return 1, "bad password"
        if len(new_passwd)<4:
            return 2, "invalid pwd"
        db.change_pwd(name_by_token, new_passwd)
        return 0,""

class WebModelPreferenceHandler(RequestHandler):
    @capture_post("token","prefered_model")
    @check_token
    def post(self, token, name_by_token, prefered_model):
        if prefered_model!='slim' and prefered_model!="default":
            return 6,"invalid model"
        else:
            db.set_skin_model_preference(name_by_token, prefered_model)
        return 0,""

class WebTypePreferenceHandler(RequestHandler):
    @capture_post("token","type","preference")
    @check_token
    def post(self, token, name_by_token, type, preference):
        if type!="skin" and type!="cape" and type!="elytra":
            return 6, "invalid type"
        if preference!="dynamic" and preference!="static" and preference!="off":
            return 6, "invalid preference"
        db.set_type_preference(name_by_token, type, preference)
        return 0,""

class WebSetDynamicIntervalHandler(RequestHandler):
    @capture_post("token","type","interval")
    @check_token
    def post(self, token, name_by_token, type, interval):
        if type!="skin_slim" and type!="skin_default" and type!="cape" and type!="elytra":
            return 6, "invalid type"
        i=None
        try:
            i=int(interval)
        except:
            pass
        if i is None or i<=0:
            return 6, "invalid interval"
        db.set_dynamic_interval(name_by_token, type, i)
        return 0,""

class WebSkinModificationHandler(RequestHandler):
    @capture_post("token","model","type")
    @check_token
    def post(self,token,name_by_token,model,type):
        if model!="skin_slim" and model!="skin_default" and model!="cape" and model!="elytra":
            return 6, "invalid model"
        if type!="static" and type!="dynamic":
            return 6, "invalid type"
        import hashlib
        skin_file=self.request.files.get('file')[0]
        file_bin=skin_file['body']
        if len(file_bin) > cfg["max-file-size"]:
            return 9, "file too large"
        m=hashlib.sha256()
        m.update(file_bin)
        hex_name=m.hexdigest()
        texture_cache.inc_hash(hex_name)
        open(cfg["texture-folder"]+hex_name,'wb').write(file_bin)
        db.set_texture_hash(name_by_token, model, type=="dynamic", hex_name)
        return 0,""

class WebSkinDeleteHandler(RequestHandler):
    @capture_post("token","model","type")
    @check_token
    def post(self,token,name_by_token,model,type):
        if model!="skin_slim" and model!="skin_default" and model!="cape" and model!="elytra":
            return 6, "invalid model"
        if type!="static" and type!="dynamic":
            return 6, "invalid type"
        db.del_texture_hash(name_by_token, model, type=="dynamic", (lambda x: texture_cache.dec_hash(x)))
        return 0,""

def stop_server():
    db.close()
    tornado.ioloop.IOLoop.instance().stop()
    logging.info('exit success')

def run_server():
    handlers=[(r"/textures/(.*)",    TexturesHandler,{"path":cfg["texture-folder"]}),
              (r"/(.*).json",        UserProfileHandler),

              (r"/",                 tornado.web.RedirectHandler,  {"url" :"/index.html"}),
              (r"/(index\.html)",    tornado.web.StaticFileHandler,{"path":"static"}),
              (r"/(favicon\.png)",   tornado.web.StaticFileHandler,{"path":"static"}),
              (r"/static/(.*)",      tornado.web.StaticFileHandler,{"path":"static"}),

              (r"/register",         WebRegisterHandler),
              (r"/login",            WebLoginHandler),
              (r"/logout",           WebLogoutHandler),
              (r"/userdata",         WebDataAccessHandler),
              (r"/delete_account",   WebAccountDelHandler),
              (r"/chpwd",            WebChangePasswordHandler),
              (r"/model_preference", WebModelPreferenceHandler),
              (r"/type_preference",  WebTypePreferenceHandler),
              (r"/dynamic_interval", WebSetDynamicIntervalHandler),
              (r"/upload_texture",   WebSkinModificationHandler),
              (r"/delete_texture",   WebSkinDeleteHandler),
              #(r"/adm_action",       WebAdministrationHandler),

              (r".*",                tornado.web.ErrorHandler,{"status_code":404})]
    try:
        import signal
        tornado.options.parse_command_line()
        on_signal=(lambda sig, frame: tornado.ioloop.IOLoop.instance().add_callback_from_signal(stop_server))
        signal.signal(signal.SIGINT, on_signal)
        signal.signal(signal.SIGTERM, on_signal)
        application=tornado.web.Application(handlers,debug=True,compress_response=True)
        application.listen(cfg["port"])
        print("Starting UniSkinServer on port:",cfg["port"])
        tornado.ioloop.IOLoop.instance().start()
    except Exception as e:
        print(e)
        print("Now server quit.")

import uss_config
from uss_database import uss_database
import uss_runtime

if __name__=="__main__":
    global cfg, db, texture_cache, sessionManager
    cfg=uss_config.get_config()
    if cfg is None:
        print("Error Occurred, check your config please.")
    else:
        db=uss_database(cfg["database-path"])
        texture_cache=uss_runtime.TextureManager(cfg["texture-folder"])
        db.scan_hashes((lambda hash: texture_cache.inc_hash(hash)))
        texture_cache.force_clean()
        sessionManager=uss_runtime.SessionManager(cfg["session-time"])
        run_server()
