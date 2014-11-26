## 根地址
根地址是每个URL请求的开始部分，每个请求的URL均由  
根地址与Endpoint连接而成，根地址也唯一地标识了一台服务器  
所有请求都是不带参数的GET请求  
假设一个服务器的根地址是

    http://127.0.0.1:8000/skinserver/

获取玩家皮肤的Endpoint是

    /MinecraftSkins/{PlayerName}.png

那么，从该服务器获取玩家`XiaoMing`的皮肤的请求即为

    http://127.0.0.1:8000/skinserver/MinecraftSkins/XiaoMing.png

一个实现了UniSkinAPI的服务端应当实现所有Endpoint

## 传统形式的皮肤与披风获取
Endpoints:

    皮肤：/MinecraftSkins/{PlayerName}.png
    披风：/MinecraftCloaks/{PlayerName}.png

返回值:

- 200: 返回皮肤/披风材质
- 301: 重定向到新式连接
- 404: 发生了错误

皮肤连接应当返回符合`Steve`人物模型的皮肤
若无，则返回404

## 新式材质链接
Endpoints:

    /textures/{材质文件唯一标识符}

返回值:

- 200: 返回材质文件
- 404: 材质未找到

唯一标识符应当与文件一一对应  
我推荐使用文件的SHA-256作为唯一标识符  

## 获得玩家信息:
Endpoint:

    /{玩家名}.json

返回值:

- 200: 返回玩家信息(UserProfile)
- 404: 该玩家不存在
- 400: 需要UUID校验

## 获得玩家信息，带UUID
Endpoint:

    /{玩家名}.{UUID}.json

返回值:

- 200: 返回玩家信息(UserProfile)
- 404: 该玩家不存在
- 400: UUID校验失败

## UserProfile:
UserProfile代表了一个玩家的信息

    {
      "player_name": {字符串，玩家名},
      "last_update": {整数，玩家最后一次修改个人信息的时间，UNIX时间戳},
      "uuid": {字符串，UUID},
      "model_preference": {字符串数组，按顺序存储玩家偏好的人物模型名称},
      "skins": {人物模型到对应皮肤UID的字典}
      "cape": {披风的UID}
    }

一个完整的样例是:

    {
      "player_name": "XiaoMing",
      "last_update": 1416300800,
      "uuid": "b6e152724b02462dbafcfe1573c8d6cc",
      "model_preference": ["slim","default"],
      "skins": {
        "alim": "67cbc70720c4666e9a12384d041313c7bb9154630d7647eb1e8fba0c461275c6",
        "default": "6d342582972c5465b5771033ccc19f847a340b76d6131129666299eb2d6ce66e"
      }
      "cape": "970a71c6a4fc81e83ae22c181703558d9346e0566390f06fb93d09fcc9783799"
    }

所有的成员都是可选的，一个支持UniSkinAPI的皮肤mod不应因缺少任何部分而崩溃。

## 错误回应:
当某个请求出错时，服务器可以返回空，也可以返回如下JSON

    {
      "errno": {整数，错误代号},
      "msg": {字符串，人类可读的信息}
    }

目前定义的错误代号有:
- 0: 没有错误发生
- 1: 需要UUID验证
- 2: UUID验证失败
- 3: 玩家不存在
- 4: 没有合适的皮肤
