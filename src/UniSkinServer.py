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
            wrapped_func(handler, argument_dict)
        return new_func
    return real_wrapper

def check_token(orig_func):
    def new_func(handler, args):
        if "token" in args:
            name = sessionManager.get_name(args["token"])
            if name is not None:
                args["name_by_token"] = name
                return orig_func(handler, args)
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
    def post(self, args):
        if not cfg["allow-reg"]:
            self.write('{"errno":7,"msg":"reg not allowed"}')
            return
        name = args["login"]
        passwd = args["passwd"]
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
    def post(self, args):
        name=self.get_argument("login")
        passwd=self.get_argument("passwd")
        if not db.is_passwd_match(name,passwd):
            self.write('{"errno":1,"msg":"invalid login"}')
        else:
            token=sessionManager.login(name)
            self.write('{"errno":0,"msg":"%s"}'%token)

class WebLogoutHandler(RequestHandler):
    @capture_post("token")
    @check_token
    def post(self, args):
        sessionManager.logout(args["token"])
        self.write('{"errno":0,"msg":""}')

class WebDataAccessHandler(RequestHandler):
    @capture_post("token")
    @check_token
    def post(self, args):
        self.write(db.get_formatted(args["name_by_token"], uss_runtime.WebDataFormatter))

class WebAccountDelHandler(RequestHandler):
    @capture_post("token","current_passwd","login")
    @check_token
    def post(self, args):
        if not args["name_by_token"]==args["login"]:
            self.write('{"errno":6,"msg":"login not match"}')
            return
        if not db.is_passwd_match(args["name_by_token"], args["current_passwd"]):
            self.write('{"errno":1,"msg":"bad password"}')
            return
        db.scan_user_hash(args["name_by_token"], (lambda x: texture_cache.dec_hash(x)))
        db.delete_user(args["name_by_token"])
        self.write('{"errno":0,"msg":""}')

class WebChangePasswordHandler(RequestHandler):
    @capture_post("token","current_passwd","login","new_passwd")
    @check_token
    def post(self, args):
        if not args["name_by_token"]==args["login"]:
            self.write('{"errno":6,"msg":"login not match"}')
            return
        if not db.is_passwd_match(args["name_by_token"], args["current_passwd"]):
            self.write('{"errno":1,"msg":"bad password"}')
            return
        if len(args["new_passwd"])<4:
            self.write('{"errno":2,"msg":"invalid pwd"}')
            return
        db.change_pwd(args["name_by_token"], args["new_passwd"])
        self.write('{"errno":0,"msg":""}')

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
              #(r"/model_preference", WebModelPreferenceHandler),
              #(r"/type_preference",  WebTypePreferenceHandler),
              #(r"/dynamic_interval", WebSetDynamicIntervalHandler),
              #(r"/upload_texture",   WebSkinModificationHandler),
              #(r"/delete_texture",   WebSkinDeleteHandler),
              #(r"/adm_action",       WebAdministrationHandler),

              (r".*",                tornado.web.ErrorHandler,{"status_code":404})]
    try:
        import signal
        tornado.options.parse_command_line()
        on_signal=(lambda sig, frame: tornado.ioloop.IOLoop.instance().add_callback_from_signal(stop_server))
        signal.signal(signal.SIGINT, on_signal)
        signal.signal(signal.SIGTERM, on_signal)
        application=tornado.web.Application(handlers,debug=True)
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
