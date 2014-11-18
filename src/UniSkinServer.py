#!/bin/python3
# -*- coding: utf-8 -*-
import server_config
import tornado.web
from tornado.web import RequestHandler

class LegacySkinHandler(RequestHandler):
    def get(self,player_name):
        if not users.exists(player_name):
            self.set_status(404)
        else:
            link=users.get(player_name).getLegacySkin()
            if link=="":
                self.set_status(404)
            else:
                self.redirect(link)

class LegacyCapeHandler(RequestHandler):
    def get(self,player_name):
        if not users.exists(player_name):
            self.set_status(404)
        else:
            link=users.get(player_name).getLegacyCape()
            if link=="":
                self.set_status(404)
            else:
                self.redirect(link)

class TexturesHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self,path):
        self.set_header("Content_Type","image/png")
        
class UserProfileHandler(RequestHandler):
    def get(self,player_name):
        arr=player_name.split(".")
        name=arr[0]
        if not users.exists(name):
            self.set_status(404)
            return
        if len(arr)==1: #Type A
            if cfg.uuid_bind:
                self.set_status(400)
                self.write('{"errno":1,"msg":"UUID verfication required"}')
                return
            self.write(users.get(name).toJson())
        else:
            user=users.get(name)
            if cfg.uuid_bind and (not user.uuid_match(arr[1])):
                self.set_status(400)
                self.write('{"errno":2,"msg":"UUID verfication failed"}')
            else:
                self.write(user.toJson())

class WebRegisterHandler(RequestHandler):
    def post(self):
        name=self.get_argument("login")
        passwd=self.get_argument("passwd")
        if users.exists(name):
            self.write('{"errno":1,"msg":"already registered"}')
            return
        if len(name)<=3 or len(name)>20 or len(passwd)<4:
            self.write('{"errno":2,"msg":"invalid name/pwd"}')
            return
        users.new_user(name,passwd)
        users.sync()
        self.write('{"errno":0,"msg":""}')

class WebLoginHandler(RequestHandler):
    def post(self):
        name=self.get_argument("login")
        passwd=self.get_argument("passwd")
        if not users.exists(name):
            self.write('{"errno":1,"msg":"invalid login"}')
        elif not users.get(name).passwd_match(passwd):
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
            self.write(users.get(name).get_web_data())

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
            user=users.get(sessionManager.get_name(token))
            updated_item=""
            uuid=ArgHelper(self,"uuid")
            preference=ArgHelper(self,"preference")
            new_pass=ArgHelper(self,"new_passwd")
            if uuid!=None:
                user.update_uuid(uuid)
                users.sync()
                updated_item="uuid"
            elif preference!=None:
                user.update_prefer(perference)
                users.sync()
                update_item="perference"
            elif new_pass!=None:
                login=ArgHelper(self,"login")
                cur=ArgHelper(self,"current_passwd")
                if login==None or cur==None:
                    self.write('{"errno":1,"msg":"change password need current password"}')
                success=user.chpwd(login,cur,new_pass)
                if success:
                    updated_item="password"
                else:
                    self.write('{"errno":2,"msg":"password change verification fail"}')
            if updated_item!='':
                self.write('{"errno":0,"msg":"successfully updated %s"}'%updated_item)
            
def WebSkinModificationHandle(RequestHandler):
    def delete(self):
        token=self.get_argument("token")
        if not sessionManager.valid(token):
            self.set_status(403)
            self.write('{"errno":-1,"msg":"invalid token"}')
        else:
            name=sessionManager.get_name(token)
            users.get(name).remove_model(self.get_argument("type"))
    def post(self):
        
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
            users.get(user).update_model(self.get_argument("type"),hex_name)
            self.write('{"errno":0,"msg":"success"}')
            
def run_server(cfg):
    global users,sessionManager
    handlers=[(r"/MinecraftSkins/(.*).png",  LegacySkinHandler),
              (r"/MinecraftCloaks/(.*).png", LegacyCapeHandler),
              (r"/textures/(.*).png",        TexturesHandler),
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
        users=cfg.user_data
        tornado.ioloop.IOLoop.instance().start()
    except Exception as e:
        print(e)
        print("Now server quit.")

if __name__=="__main__":
    global cfg
    cfg=server_config.getConfigure()
    if cfg==None:
        print("Error Occured, check your config please.")
    else:
        run_server(cfg)
