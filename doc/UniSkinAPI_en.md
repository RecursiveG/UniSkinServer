## "The Root"
"The Root" is the start part of every request.
Every Request URL is by connecting The Root and the Endpoint
For example, The Root of a server is

    http://127.0.0.1:8000/skinserver/

and the Endpoint for getting the skin is

    /MinecraftSkins/{PlayerName}.png

if a client want the Skin for player `John`, the request will be

    http://127.0.0.1:8000/skinserver/MinecraftSkins/John.png

A compatible server should implements all the endpoints.

## Legacy Style Skin & Cape Link:
Endpoints:

    For Skins：/MinecraftSkins/{PlayerName}.png
    For Capes：/MinecraftCloaks/{PlayerName}.png

Response:

- 200: Return the image data directly
- 301: Redirect to the new style texture link
- 404: Something wrong happened.

The skin link should always return the skin for model `Steve`.
If no `Steve` model skin specified, return 404.

## New Style Texture Link:
Endpoints:

    /textures/{unique identifier to the file}
    /textures/{unique identifier to the file}.{extension}

Response:

- 200: Return the texture
- 404: Not found

UID should be always different for different file
Even they belongs to the same player or even in different servers
It's ok to have a extension (usually .png)
I recommend using SHA-256 of the file as the UID

## Get user profile:
Endpoint:

    /{PlayerName}.json

Response:

- 200: Return the UserProfile json
- 404: PlayerName not registered
- 400: need UUID verification

## Get user profile with UUID:
Endpoint:

    /{PlayerName}.{UUID}.json

Response:

- 200: Return the UserProfile json
- 404: PlayerName not registered
- 400: UUID mismatch

You can return 200 even if the UUID not match
That depends on you

## UserProfile:
UserProfile is a JSON string, the format is:

    {
      "player_name": {string, player name},
      "last_update": {int, the time the player made the last change, in unix timestamp},
      "uuid": {string, uuid of the player},
      "model_preference": {array of string, the name of the models are listed in order of preference},
      "skins": {Map<String,String>, map of model name to texture hash}
      "cape": {hash of cape texture}
    }

And An Example Could Be:

    {
      "player_name": "John",
      "last_update": 1416300800,
      "uuid": "b6e152724b02462dbafcfe1573c8d6cc",
      "model_preference": ["alex","steve"],
      "skins": {
        "alex": "67cbc70720c4666e9a12384d041313c7bb9154630d7647eb1e8fba0c461275c6",
        "steve": "6d342582972c5465b5771033ccc19f847a340b76d6131129666299eb2d6ce66e"
      }
      "cape": "970a71c6a4fc81e83ae22c181703558d9346e0566390f06fb93d09fcc9783799"
    }

All the fields are optional, and a compatible client should automatically skip
any missing information

## Response for Errors:
For any response other than 2** & 3**,
the body could be either empty or a json.
Returning an empty body would be fine in most case

    {
      "errno": {int},
      "msg": {human readable string and can be anything you like}
    }

Defined errnos are:
- 0: No Error Occurred
- 1: UUID needed
     Happened when getting user profile without UUID, requiring
     the client to make another request together with UUID
- 2: UUID verification failed
     Something wrong happened when getting profile with UUID
     Detailed info should be in `msg` field.
- 3: User not registered
     No such player in the database at all.
- 4: No suitable skin
