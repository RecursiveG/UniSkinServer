DEFAULT_CONFIG='''{
    "port": "12345",
    "allow-reg": true,
    "texture-folder": "textures/",
    "database": "data.db",
    "admin-passphrase": ""
}
'''

def get_config(file_path="server_config.json"):
    try:
        import os
        import json
        if not os.path.exists(file_path):
            f=open(file_path,"w")
            f.write(DEFAULT_CONFIG)
            f.close()

        f=open(file_path)
        config=json.loads(f.read())
        if not os.path.exists(config["texture_path"]):
            os.mkdir(config["texture_path"])
    except Exception as e:
        print(e)
        return None
    return config
