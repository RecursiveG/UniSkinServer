## "The Root"
"The Root" is the start part of every request.
Every Request URL is by connecting The Root and the Endpoint
For example, The Root of a server is

    http://127.0.0.1:8000/skinserver/

and the Endpoint for getting the profile is

    /{PlayerName}.json

if a client want the profile for player `John`, the request will be

    http://127.0.0.1:8000/skinserver/John.json

A compatible server should implements all the endpoints.

## Texture Files Link:
Endpoint:

    /textures/{unique identifier to the file}

Response:

- 200: Return the texture
- 404: Not found

UID should be always different for different file
Even they belongs to the same player or even in different servers
I recommend using SHA-256 of the file as the UID

## Get user profile:
Endpoint:

    /{PlayerName}.json

The `{PlayerName}` here is not case-sensitive
If non-ASCII character is needed. They should be encoded as UTF-8 and use [Precent-Encoding](https://en.wikipedia.org/wiki/Percent-encoding) notation.
e.g. `%E5%B0%8F%E6%98%8E.json`

Response:

- 200: Return the UserProfile json
- 400: If the encoding is not acceptable
- 404: PlayerName not registered

## UserProfile:
UserProfile is a JSON string, the format is:

    {
      "player_name": {string, Case-Corrected player name},
      "last_update": {int, the time the player made the last change, in unix timestamp, seconds},
      "model_preference": {array of string, the name of the models are listed in order of preference},
      "skins": {Map<String,String>, map of model name to texture hash}
      "cape": {hash of cape texture}(Deprecated)
    }

And An Example Could Be:

    {
      "player_name": "John",
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

All the fields are optional, and a compatible client should automatically skip
any missing information

## Model Name Convention

Model names are case-sensitive.

- `slim`: The slim-arm or female player model
- `default`: The triditional player model
- `cape`: Reserved for cape texture use
- `elytron`: Reserved for elytron texture use

## Model load order

- For `slim` and default, the front one is used
- For `cape` and elytron, if exists then use
- For clients which not support `slim`/`cape`/`elytron`, they are ignored
- When `cape` exists both inside and outside, the one *in* the `skins` dictonary is used.

## Entended Model for UniSkinMod

UniSkinMod may support dynamic skins in the future.
So these four model names are reserved.

- slim_dynamic
- default_dynamic
- cape_dynamic
- elytron_dynamic

Still, the ones in front are loaded. If not supported then ignore.
The `texture` string for dynamic skins is a comma-seperated string consists of all UID of every frame.
Except the first one, which is a positive integer represents how many milliseconds it plays for one time.
All the frames are played in equal time interval.

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
- 1: User not registered
     No such player in the database at all.
