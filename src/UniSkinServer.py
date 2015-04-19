#!/bin/python3
# -*- coding: utf-8 -*-
import server_config
import tornado.web
import tornado.options
from tornado.web import RequestHandler

def ArgHelper (handler,arg,default=None):
  try:
    x=handler.get_argument(arg)
  except tornado.web.MissingArgumentError:
    x=default
  return x

class TexturesHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self,path):
        self.set_header("Content-Type","image/png")

class UserProfileHandler(RequestHandler):
    def get(self,player_name):
        name=player_name.lower()
        if not db.user_exists(name):
            self.set_status(404)
            return
        self.write(db.user_json(name));

class WebRegisterHandler(RequestHandler):
    def post(self):
        if not cfg.allow_reg:
            self.write('{"errno":4,"msg":"reg not allowed"}')
            return
        name=self.get_argument("login")
        passwd=self.get_argument("passwd")
        if db.user_exists(name):
            self.write('{"errno":1,"msg":"already registered"}')
            return
        if len(name)<=0 or len(passwd)<4:
            self.write('{"errno":2,"msg":"invalid name/pwd"}')
            return
        try:
            db.new_user(name,passwd)
        except Exception as e:
            print(e)
            self.write('{"errno":3,"msg":"Internal Server Error"}')
            return
        self.write('{"errno":0,"msg":""}')

class WebAccountDelHandler(RequestHandler):
    def post(self):
        token=self.get_argument("token")
        if not sessionManager.valid(token):
            self.write('{"errno":-1,"msg":"invalid token"}')
        else:
            pwd=ArgHelper(self,"pwd")
            name=sessionManager.get_name(token)
            if db.isValid(name,pwd):
                db.rm_account(name,texture_cache)
                self.write('{"errno":0,"msg":""}')
            else:
                self.write('{"errno":2,"msg":"password change verification fail"}')

class WebLoginHandler(RequestHandler):
    def post(self):
        name=self.get_argument("login")
        passwd=self.get_argument("passwd")
        if not db.isValid(name,passwd):
            self.write('{"errno":1,"msg":"invalid login"}')
        else:
            token=sessionManager.login(name)
            self.write('{"errno":0,"msg":"%s"}'%token)

class WebLogoutHandler(RequestHandler):
    def post(self):
        token=self.get_argument("token")
        success=sessionManager.logout(token)
        if not success:
            self.write('{"errno":1,"msg":"logout fail"}')
        else:
            self.write('{"errno":0,"msg":""}')

class WebDataAccessHandler(RequestHandler):
    def post(self):
        token=self.get_argument("token")
        if not sessionManager.valid(token):
            self.write('{"errno":-1,"msg":"invalid token"}')
        else:
            name=sessionManager.get_name(token)
            self.write(db.user_json_web(name))

class WebProfileUpdateHandler(RequestHandler):
    def post(self):
        token=self.get_argument("token")
        if not sessionManager.valid(token):
            self.write('{"errno":-1,"msg":"invalid token"}')
        else:
            name=sessionManager.get_name(token)
            updated_item=list()
            uuid=ArgHelper(self,"uuid")
            preference=ArgHelper(self,"preference")
            new_pass=ArgHelper(self,"new_passwd")
            if new_pass!=None:
                cur=ArgHelper(self,"current_passwd")
                if cur==None:
                    self.write('{"errno":1,"msg":"change password need current password"}')
                    return
                if db.isValid(name,cur):
                    if(len(new_pass)<4):
                        self.write('{"errno":3,"msg":"New pwd too short"}')
                        return
                    db.change_pwd(name,new_pass)
                    updated_item.append("password")
                else:
                    self.write('{"errno":2,"msg":"password change verification fail"}')
            if uuid!=None:
                db.update_uuid(name,uuid)
                updated_item.append("uuid")
            if preference!=None:
                db.update_preference(name,preference)
                updated_item.append("perference")
            if len(updated_item)!=0:
                self.write('{"errno":0,"msg":"successfully updated %s"}'%(','.join(updated_item)))

class WebSkinDelHandle(RequestHandler):
    def post(self):
        token=self.get_argument("token")
        if not sessionManager.valid(token):
            self.write('{"errno":-1,"msg":"invalid token"}')
        else:
            name=sessionManager.get_name(token)
            h=db.remove_skin(name,self.get_argument("type"))
            texture_cache.minus1(h)

class WebSkinModificationHandle(RequestHandler):
    def post(self):
        import hashlib
        token=self.get_argument("token")
        if not sessionManager.valid(token):
            self.set_status(403)
            self.write('{"errno":-1,"msg":"invalid token"}')
        else:
            name=sessionManager.get_name(token)
            skin_file=self.request.files.get('file')[0]
            file_bin=skin_file['body']
            if len(file_bin) > 1024*1024:
                self.write('{"errno":1,"msg":"file too large"}')
                return
            m=hashlib.sha256()
            m.update(file_bin)
            hex_name=m.hexdigest()
            texture_cache.plus1(hex_name)
            open(cfg.texture_path+hex_name,'wb').write(file_bin)
            db.update_model(name,self.get_argument("type"),hex_name)
            self.write('{"errno":0,"msg":"success"}')

def run_server(cfg):
    global sessionManager
    handlers=[(r"/textures/(.*)",  TexturesHandler,{"path":"textures"}),
              (r"/(.*).json",      UserProfileHandler),

              (r"/",               tornado.web.RedirectHandler,{"url": "/index.html"}),
              (r"/(index\.html)",  tornado.web.StaticFileHandler,{"path":"static"}),
              (r"/(favicon\.png)", tornado.web.StaticFileHandler,{"path":"static"}),
              (r"/static/(.*)",    tornado.web.StaticFileHandler,{"path":"static"}),

              (r"/reg",   WebRegisterHandler),
              (r"/delacc",WebAccountDelHandler),
              (r"/delski",WebSkinDelHandle),
              (r"/login", WebLoginHandler),
              (r"/logout",WebLogoutHandler),
              (r"/update",WebProfileUpdateHandler),
              (r"/data",  WebDataAccessHandler),
              (r"/upload",WebSkinModificationHandle),

              (r".*", tornado.web.ErrorHandler,{"status_code":404})]

    try:
        tornado.options.parse_command_line()
        application=tornado.web.Application(handlers,debug=True)
        application.listen(cfg.port)
        print("Starting UniSkinServer on port:",cfg.port)
        sessionManager=server_config.SessionManager()
        tornado.ioloop.IOLoop.instance().start()
    except Exception as e:
        print(e)
        print("Now server quit.")

if __name__=="__main__":
    global cfg,db,texture_cache
    cfg=server_config.getConfigure()
    if cfg==None:
        print("Error Occured, check your config please.")
    else:
        db=server_config.DatabaseProvider(cfg.database_path)
        texture_cache=server_config.TextureManager(db.get_cursor(),cfg.texture_path)
        run_server(cfg)
