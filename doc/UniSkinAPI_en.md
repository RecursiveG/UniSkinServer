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
Endpoints:

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

Response:

- 200: Return the UserProfile json
- 404: PlayerName not registered

## UserProfile:
UserProfile is a JSON string, the format is:

    {
      "player_name": {string, Case-Corrected player name},
      "last_update": {int, the time the player made the last change, in unix timestamp},
      "model_preference": {array of string, the name of the models are listed in order of preference},
      "skins": {Map<String,String>, map of model name to texture hash}
      "cape": {hash of cape texture}
    }

And An Example Could Be:

    {
      "player_name": "John",
      "last_update": 1416300800,
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
- 1: User not registered
     No such player in the database at all.
