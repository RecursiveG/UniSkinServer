## 根地址
根地址是每个URL请求的开始部分，每个请求的URL均由
根地址与Endpoint连接而成，根地址也唯一地标识了一台服务器
所有请求都是不带参数的GET请求
假设一个服务器的根地址是

    http://127.0.0.1:8000/skinserver/

获取玩家Profile的Endpoint是

    /{玩家名}.json

那么，从该服务器获取玩家`XiaoMing`的皮肤的请求即为

    http://127.0.0.1:8000/skinserver/XiaoMing.json

一个实现了UniSkinAPI的服务端应当实现所有Endpoint

## 材质文件链接
Endpoint:

    /textures/{材质文件唯一标识符}

返回值:

- 200: 返回材质文件
- 404: 材质未找到

唯一标识符应当与文件一一对应
我推荐使用文件的SHA-256作为唯一标识符

## 获得玩家信息:
Endpoint:

    /{玩家名}.json

该处玩家名大小写可随意
如果玩家名包含非ASCII字符，请使用UTF-8编码的[URL编码](https://en.wikipedia.org/wiki/Percent-encoding)
例如：`%E5%B0%8F%E6%98%8E.json`

返回值:

- 200: 返回玩家信息(UserProfile)
- 400: 不可接受的字符编码
- 404: 该玩家不存在

## UserProfile:
UserProfile代表了一个玩家的信息

    {
      "player_name": {字符串，大小写正确的玩家名},
      "last_update": {整数，玩家最后一次修改个人信息的时间，UNIX时间戳, 秒},
      "model_preference": {字符串数组，按顺序存储玩家需要加载的模型名称},
      "skins": {模型名称到对应材质UID的字典}
      "cape": {披风的UID} (已弃用)
    }

一个完整的样例是:

    {
      "player_name": "XiaoMing",
      "last_update": 1416300800,
      "model_preference": ["slim","default","cape","default_dynamic"],
      "skins": {
        "slim": "67cbc70720c4666e9a12384d041313c7bb9154630d7647eb1e8fba0c461275c6",
        "default": "6d342582972c5465b5771033ccc19f847a340b76d6131129666299eb2d6ce66e",
        "cape": "970a71c6a4fc81e83ae22c181703558d9346e0566390f06fb93d09fcc9783799"
        "default_dynamic": "1000,67cbc70720c4666e9a12384d041313c7bb9154630d7647eb1e8fba0c461275c6,6d342582972c5465b5771033ccc19f847a340b76d6131129666299eb2d6ce66e"
      }
      "cape": "970a71c6a4fc81e83ae22c181703558d9346e0566390f06fb93d09fcc9783799"
    }

所有的成员都是可选的，一个支持UniSkinAPI的皮肤mod不应因缺少任何部分而崩溃。

## 模型名称约定

模型名称是大小写敏感的

- `slim`: 细手臂/女性玩家模型
- `default`: 经典玩家模型
- `cape`: 为披风材质使用
- `elytron`: 为滑翔翅材质使用

## 加载顺序约定

- 对于`slim`和`default`，在前的皮肤被加载
- 对于`cape`和`elytron`，若存在则加载
- 对于不支持`slim`/`cape`/`elytron`模型的客户端，对应材质被忽略
- 当存在两个`cape`字段时，以`skins`字典中的为准

## UniSkinMod 扩展模型

UniSkinMod正考虑加入动态皮肤功能，占用以下四个模型：

- slim_dynamic
- default_dynamic
- cape_dynamic
- elytron_dynamic

依然是在前面的被加载，若不存在或不支持则忽略。
texture字符串为由`,`分隔的多个代表每帧图片的UID，第一项是例外。是一个正整数，表示多长时间循环一遍，单位millisecond。
所有图片等间隔播放。

## 错误回应:
当某个请求出错时(返回值不为200时)，服务器可以返回空，也可以返回如下JSON

    {
      "errno": {整数，错误代号},
      "msg": {字符串，人类可读的信息}
    }

目前定义的错误代号有:
- 0: 没有错误发生
- 1: 玩家不存在
