# Universal Skin API 计划
相关描述请见MCBBS[Universal Skin API 计划](http://www.mcbbs.net/thread-366248-1-1.html)

### Universal Skin API
具体文档请见`doc`目录  
Documents under `doc` folder  
**如对API有意见，请先发Issue，尽量避免直接Pull Request**
**Open an issue if you have any concerns about the API**

### Universal Skin Server
位于`src`目录下
以GPLv2协议发布
Source under `src` folder. Licensed under GPLv2
**注意：密码现在是明文传输，你可能需要HTTPS保证安全**
**Warning: Passwords are transmitted in plain-text. You may need HTTPS to secure the connection.**

### Universal Skin Mod
请见[UniSkinMod](https://github.com/RecursiveG/UniSkinMod)

### Command Line Arguments

    python UniSkinServer.py -c [user_name] [new_password]  #force change a password, OK to execute while server is running.
