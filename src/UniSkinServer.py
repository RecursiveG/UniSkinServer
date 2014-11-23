#!/bin/python3
# -*- coding: utf-8 -*-
import server_config
import tornado.web
from tornado.web import RequestHandler

class LegacySkinHandler(RequestHandler):
    def get(self,player_name):
        if not db.user_exists(player_name):
            self.set_status(404)
        else:
            h=db.getLegacySkin(player_name)
            if h==None:
                self.set_status(404)
            else:
                self.redirect("/textures/"+h)

class LegacyCapeHandler(RequestHandler):
    def get(self,player_name):
        if not db.user_exists(player_name):
            self.set_status(404)
        else:
            h=db.getLegacyCape(player_name)
            if h==None:
                self.set_status(404)
            else:
                self.redirect("/textures/"+h)

class TexturesHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self,path):
        self.set_header("Content_Type","image/png")

class UserProfileHandler(RequestHandler):
    def get(self,player_name):
        arr=player_name.split(".")
        name=arr[0]
        if not db.user_exists(name):
            self.set_status(404)
            return
        if len(arr)==1: #Type A
            if cfg.uuid_bind:
                self.set_status(400)
                self.write('{"errno":1,"msg":"UUID verfication required"}')
                return
            self.write(db.user_json(name));
        else:
            self.write(db.user_json(name));

class WebRegisterHandler(RequestHandler):
    def post(self):
        name=self.get_argument("login")
        passwd=self.get_argument("passwd")
        if db.user_exists(name):
            self.write('{"errno":1,"msg":"already registered"}')
            return
        if len(name)<=3 or len(name)>20 or len(passwd)<4:
            self.write('{"errno":2,"msg":"invalid name/pwd"}')
            return
        try:
            db.new_user(name,passwd)
        except Exception as e:
            print(e)
            self.write('{"errno":3,"msg":"Internal Server Error"}')
            return
        self.write('{"errno":0,"msg":""}')

class WebLoginHandler(RequestHandler):
    def post(self):
        name=self.get_argument("login")
        passwd=self.get_argument("passwd")
        if not db.isValid(name,passwd):
            self.write('{"errno":1,"msg":"invalid login"}')
        else:
            token=sessionManager.login(name)
            self.write('{"errno":0,"msg":"%s"}'%token)

class WebDataAccessHandler(RequestHandler):
    def post(self):
        token=self.get_argument("token")
        if not sessionManager.valid(token):
            self.set_status(403)
            self.write('{"errno":-1,"msg":"invalid token"}')
        else:
            name=sessionManager.get_name(token)
            self.write(db.user_json_web(name))
def ArgHelper (handler,arg,default=None):
    try:
        x=handler.get_argument(arg)
    except tornado.web.MissingArgumentError:
        x=default
    return x

class WebProfileUpdateHandler(RequestHandler):
    def post(self):
        token=self.get_argument("token")
        if not sessionManager.valid(token):
            self.set_status(403)
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
                    db.change_pwd(name,pwd)
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

class WebSkinModificationHandle(RequestHandler):
    def delete(self):
        token=self.get_argument("token")
        if not sessionManager.valid(token):
            self.set_status(403)
            self.write('{"errno":-1,"msg":"invalid token"}')
        else:
            name=sessionManager.get_name(token)
            db.remove_skin(name,self.get_argument("type"))
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
            open(cfg.texture_path+hex_name,'wb').write(file_bin)
            db.update_model(name,self.get_argument("type"),hex_name)
            self.write('{"errno":0,"msg":"success"}')

def run_server(cfg):
    global sessionManager
    handlers=[(r"/MinecraftSkins/(.*).png",  LegacySkinHandler),
              (r"/MinecraftCloaks/(.*).png", LegacyCapeHandler),
              (r"/textures/(.*).png",        TexturesHandler),
              (r"/textures/(.*)",            TexturesHandler),
              (r"/(.*).json",                UserProfileHandler),

              (r"/",               tornado.web.RedirectHandler,{"url": "/index.html"}),
              (r"/(index\.html)",  tornado.web.StaticFileHandler,{"path":"static"}),
              (r"/(favicon\.png)", tornado.web.StaticFileHandler,{"path":"static"}),
              (r"/static/(.*)",    tornado.web.StaticFileHandler,{"path":"static"}),

              (r"/reg",   WebRegisterHandler),
              (r"/login", WebLoginHandler),
              (r"/update",WebProfileUpdateHandler),
              (r"/data",  WebDataAccessHandler),
              (r"/upload",WebSkinModificationHandle),

              (r".*", tornado.web.ErrorHandler,{"status_code":404})]

    try:
        application=tornado.web.Application(handlers,debug=True)
        application.listen(cfg.port)
        print("Starting UniSkinServer on port:",cfg.port)
        sessionManager=server_config.SessionManager()
        tornado.ioloop.IOLoop.instance().start()
    except Exception as e:
        print(e)
        print("Now server quit.")

if __name__=="__main__":
    global cfg,db
    cfg=server_config.getConfigure()
    if cfg==None:
        print("Error Occured, check your config please.")
    else:
        db=server_config.DatabaseProvider(cfg.database_path)
        run_server(cfg)
