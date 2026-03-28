# GDDL API Research
Taken from https://gdladder.com/api/docs#/
## Base API Information
### Base Response
All endpoints may return `500 Internal Server Error` if the request fails. The API will also return `400 Bad Request` if the request is malformed.

If any error (4xx and 5xx) occurs, the API will return JSON with the following schema:
```
{
    statusCode: number,
    message: string | string[],
    error?: string
}
```
The `statusCode` field will contain the HTTP status code of the error. The `message` field will contain a human-readable error message. The `error` field will contain the name of the error.
### Rate Limiting
The entire API has a base rate limit of 100 requests per minute.
### API Key
You can authenticate using an API key. Send your key in the Authorization header as a Bearer token. If an API key is provided, it will take precedence over the session cookie. This means that if you provide an invalid API key, you may still be authenticated with a valid session cookie. If you provide a valid API key, the session cookie will be ignored.

**NOTE:** Some endpoints don't require authentication, but will return extra information if you are authenticated. Some features are only available to authenticated users. However, it seems like the information we care about doesn't seem to require one.
## Endpoints We Care About
### `/api/level/search`
This endpoint returns a list of levels (by default sorted by ID ascending). This endpoint will most likely be how we retrieve all the levels for syncing. **NOTE:** `limit` has a maximum of 25!

`Curl Command`:
```
curl -X 'GET' \
  'https://gdladder.com/api/level/search?limit=10&page=0&sort=ID&sortDirection=asc' \
  -H 'accept: application/json'
```
`Response Body`:
```
{
  "total": 10315,
  "limit": 10,
  "page": 0,
  "levels": [
    {
      "ID": 1,
      "Rating": 2.821279025504378,
      "Enjoyment": 6.592677345537758,
      "Deviation": 0.8853618813534533,
      "RatingCount": 10650,
      "EnjoymentCount": 10488,
      "SubmissionCount": 11008,
      "TwoPlayerRating": null,
      "TwoPlayerEnjoyment": null,
      "TwoPlayerDeviation": 0,
      "DefaultRating": null,
      "Showcase": "gok5ShDXxg4",
      "Popularity": 15.330445628779444,
      "Completed": 0,
      "InPack": 1,
      "Meta": {
        "ID": 1,
        "Name": "Clubstep",
        "Description": null,
        "SongID": -14,
        "Length": 4,
        "IsTwoPlayer": false,
        "Difficulty": "Official",
        "Rarity": 0,
        "PublisherID": 1,
        "UploadedAt": null,
        "addedAt": "2025-11-29T20:38:00.000Z",
        "Song": {
          "ID": -14,
          "Name": "Clubstep",
          "Author": "DJ-Nate",
          "Size": "0MB"
        },
        "Publisher": {
          "name": "RobTop"
        }
      }
    },
    {
      "ID": 2,
      "Rating": 3.033055128486712,
      "Enjoyment": 7.0811199645861,
      "Deviation": 0.8757484532070116,
      "RatingCount": 9247,
      "EnjoymentCount": 9036,
      "SubmissionCount": 9485,
      "TwoPlayerRating": null,
      "TwoPlayerEnjoyment": null,
      "TwoPlayerDeviation": 0,
      "DefaultRating": null,
      "Showcase": "1YI4oUUiV80",
      "Popularity": 15.732721943142177,
      "Completed": 0,
      "InPack": 1,
      "Meta": {
        "ID": 2,
        "Name": "Theory of Everything 2",
        "Description": null,
        "SongID": -18,
        "Length": 4,
        "IsTwoPlayer": false,
        "Difficulty": "Official",
        "Rarity": 0,
        "PublisherID": 1,
        "UploadedAt": null,
        "addedAt": "2025-11-29T20:38:00.000Z",
        "Song": {
          "ID": -18,
          "Name": "Theory of Everything 2",
          "Author": "DJ-Nate",
          "Size": "0MB"
        },
        "Publisher": {
          "name": "RobTop"
        }
      }
    },
    {
      "ID": 3,
      "Rating": 4.709340427602724,
      "Enjoyment": 7.295954125517681,
      "Deviation": 1.095104542309041,
      "RatingCount": 9642,
      "EnjoymentCount": 9417,
      "SubmissionCount": 9895,
      "TwoPlayerRating": null,
      "TwoPlayerEnjoyment": null,
      "TwoPlayerDeviation": 0,
      "DefaultRating": null,
      "Showcase": "reZj2Xbt05Q",
      "Popularity": 15.845019298015938,
      "Completed": 1,
      "InPack": 1,
      "Meta": {
        "ID": 3,
        "Name": "Deadlocked",
        "Description": null,
        "SongID": -20,
        "Length": 4,
        "IsTwoPlayer": false,
        "Difficulty": "Official",
        "Rarity": 0,
        "PublisherID": 1,
        "UploadedAt": null,
        "addedAt": "2025-11-29T20:38:00.000Z",
        "Song": {
          "ID": -20,
          "Name": "Deadlocked",
          "Author": "F-777",
          "Size": "0MB"
        },
        "Publisher": {
          "name": "RobTop"
        }
      }
    },
    {
      "ID": 10109,
      "Rating": 2.803788903924222,
      "Enjoyment": 5.624365482233503,
      "Deviation": 0.7941613586416911,
      "RatingCount": 2976,
      "EnjoymentCount": 2758,
      "SubmissionCount": 3036,
      "TwoPlayerRating": null,
      "TwoPlayerEnjoyment": null,
      "TwoPlayerDeviation": 0,
      "DefaultRating": null,
      "Showcase": "gUlOgbJmOpI",
      "Popularity": 13.202789599823738,
      "Completed": 0,
      "InPack": 1,
      "Meta": {
        "ID": 10109,
        "Name": "demon park",
        "Description": "Bug fixed!  N plz love Psychic Escape too!",
        "SongID": -8,
        "Length": 4,
        "IsTwoPlayer": false,
        "Difficulty": "Easy",
        "Rarity": 1,
        "PublisherID": 2,
        "UploadedAt": null,
        "addedAt": "2025-11-29T20:38:00.000Z",
        "Song": {
          "ID": -8,
          "Name": "Time Machine",
          "Author": "Waterflame",
          "Size": "0MB"
        },
        "Publisher": {
          "name": "M2coL"
        }
      }
    },
    {
      "ID": 12556,
      "Rating": 3.8642533936651584,
      "Enjoyment": 5.3131955484896665,
      "Deviation": 0.9374499461639628,
      "RatingCount": 678,
      "EnjoymentCount": 629,
      "SubmissionCount": 691,
      "TwoPlayerRating": null,
      "TwoPlayerEnjoyment": null,
      "TwoPlayerDeviation": 0,
      "DefaultRating": null,
      "Showcase": "6TkE9DzbhV0",
      "Popularity": 11.418591287939803,
      "Completed": 0,
      "InPack": 1,
      "Meta": {
        "ID": 12556,
        "Name": "To the Grave",
        "Description": "Inspired by Demon Park comes a near impossible level! Also see if you can find the secret area!",
        "SongID": -8,
        "Length": 4,
        "IsTwoPlayer": false,
        "Difficulty": "Easy",
        "Rarity": 1,
        "PublisherID": null,
        "UploadedAt": "2013-10-19T19:38:25.513Z",
        "addedAt": "2025-11-29T20:38:00.000Z",
        "Song": {
          "ID": -8,
          "Name": "Time Machine",
          "Author": "Waterflame",
          "Size": "0MB"
        },
        "Publisher": null
      }
    },
    {
      "ID": 13519,
      "Rating": 1.0350770302028027,
      "Enjoyment": 5.813460850911691,
      "Deviation": 0.2856366862674704,
      "RatingCount": 11556,
      "EnjoymentCount": 11188,
      "SubmissionCount": 11829,
      "TwoPlayerRating": null,
      "TwoPlayerEnjoyment": null,
      "TwoPlayerDeviation": 0,
      "DefaultRating": null,
      "Showcase": "Xl4stg-bsxk",
      "Popularity": 14.65743831588871,
      "Completed": 0,
      "InPack": 1,
      "Meta": {
        "ID": 13519,
        "Name": "The Nightmare",
        "Description": "Hard map by Jax. 7813",
        "SongID": -3,
        "Length": 4,
        "IsTwoPlayer": false,
        "Difficulty": "Easy",
        "Rarity": 1,
        "PublisherID": 3,
        "UploadedAt": null,
        "addedAt": "2025-11-29T20:38:00.000Z",
        "Song": {
          "ID": -3,
          "Name": "Polargeist",
          "Author": "Step",
          "Size": "0MB"
        },
        "Publisher": {
          "name": "Jax"
        }
      }
    },
    {
      "ID": 55520,
      "Rating": 1.0469973890339426,
      "Enjoyment": 4.796683645822044,
      "Deviation": 0.278648872896181,
      "RatingCount": 9616,
      "EnjoymentCount": 9227,
      "SubmissionCount": 9817,
      "TwoPlayerRating": 1,
      "TwoPlayerEnjoyment": null,
      "TwoPlayerDeviation": 0,
      "DefaultRating": null,
      "Showcase": "6403P2-763E",
      "Popularity": 13.49888743518823,
      "Completed": 0,
      "InPack": 1,
      "Meta": {
        "ID": 55520,
        "Name": "THE LIGHTNING ROAD",
        "Description": "Removed Coins, ~ Timeless Real / Reduloc",
        "SongID": -4,
        "Length": 4,
        "IsTwoPlayer": false,
        "Difficulty": "Easy",
        "Rarity": 1,
        "PublisherID": 4,
        "UploadedAt": null,
        "addedAt": "2025-11-29T20:38:00.000Z",
        "Song": {
          "ID": -4,
          "Name": "Dry Out",
          "Author": "DJVI",
          "Size": "0MB"
        },
        "Publisher": {
          "name": "timeless real"
        }
      }
    },
    {
      "ID": 56287,
      "Rating": 6.845935280189421,
      "Enjoyment": 6.57315233785822,
      "Deviation": 1.5837510369179784,
      "RatingCount": 701,
      "EnjoymentCount": 663,
      "SubmissionCount": 711,
      "TwoPlayerRating": null,
      "TwoPlayerEnjoyment": null,
      "TwoPlayerDeviation": 0,
      "DefaultRating": null,
      "Showcase": "y3-wvQVHuQM",
      "Popularity": 12.832449941404645,
      "Completed": 0,
      "InPack": 0,
      "Meta": {
        "ID": 56287,
        "Name": "Extreme Park",
        "Description": "This is extremely hard level. Practice makes perfect!!! Next time I will make easier level.",
        "SongID": -7,
        "Length": 4,
        "IsTwoPlayer": false,
        "Difficulty": "Medium",
        "Rarity": 0,
        "PublisherID": 5,
        "UploadedAt": null,
        "addedAt": "2025-11-29T20:38:00.000Z",
        "Song": {
          "ID": -7,
          "Name": "Jumper",
          "Author": "Waterflame",
          "Size": "0MB"
        },
        "Publisher": {
          "name": "Rabbitical"
        }
      }
    },
    {
      "ID": 57730,
      "Rating": 1.9324074074074074,
      "Enjoyment": 5.214471629359709,
      "Deviation": 0.6006325452720724,
      "RatingCount": 2163,
      "EnjoymentCount": 1921,
      "SubmissionCount": 2197,
      "TwoPlayerRating": null,
      "TwoPlayerEnjoyment": null,
      "TwoPlayerDeviation": 0,
      "DefaultRating": null,
      "Showcase": "OBvDoG4MK0Q",
      "Popularity": 12.47074013676324,
      "Completed": 0,
      "InPack": 1,
      "Meta": {
        "ID": 57730,
        "Name": "Super Cycles",
        "Description": "Jax! 3781",
        "SongID": -9,
        "Length": 4,
        "IsTwoPlayer": false,
        "Difficulty": "Easy",
        "Rarity": 1,
        "PublisherID": 6,
        "UploadedAt": null,
        "addedAt": "2025-11-29T20:38:00.000Z",
        "Song": {
          "ID": -9,
          "Name": "Cycles",
          "Author": "DJVI",
          "Size": "0MB"
        },
        "Publisher": {
          "name": "Jax"
        }
      }
    },
    {
      "ID": 70059,
      "Rating": 1.8029321513808387,
      "Enjoyment": 5.305670296657905,
      "Deviation": 0.58112361860049,
      "RatingCount": 2942,
      "EnjoymentCount": 2663,
      "SubmissionCount": 2994,
      "TwoPlayerRating": null,
      "TwoPlayerEnjoyment": null,
      "TwoPlayerDeviation": 0,
      "DefaultRating": null,
      "Showcase": "xO2j6OMTiLo",
      "Popularity": 12.801298628315509,
      "Completed": 0,
      "InPack": 1,
      "Meta": {
        "ID": 70059,
        "Name": "yStep",
        "Description": "Extremely hard and extremely awesome! uses a healthy dose of new blocks!",
        "SongID": -10,
        "Length": 4,
        "IsTwoPlayer": false,
        "Difficulty": "Easy",
        "Rarity": 1,
        "PublisherID": 7,
        "UploadedAt": null,
        "addedAt": "2025-11-29T20:38:00.000Z",
        "Song": {
          "ID": -10,
          "Name": "xStep",
          "Author": "DJVI",
          "Size": "0MB"
        },
        "Publisher": {
          "name": "TheRealDarnoc"
        }
      }
    }
  ]
}
```
### `/api/level/{levelID}/tags`
This endpoint returns the tags for a level that are voted on by the community via `ReactCount`. This is how we determine what skillsets the level stresses the most. A higher `ReactCount` means that skillset is more present/required in the level.
`Curl Command`:
```
curl -X 'GET' \
  'https://gdladder.com/api/level/1/tags' \
  -H 'accept: application/json'
```
`Response Body`:
```
[
  {
    "TagID": 2,
    "ReactCount": 1351,
    "HasVoted": 0,
    "Tag": {
      "ID": 2,
      "Name": "Ship",
      "Description": "This level has ship sections that make up a large portion of its difficulty.",
      "Ordering": 2
    }
  },
  {
    "TagID": 8,
    "ReactCount": 686,
    "HasVoted": 0,
    "Tag": {
      "ID": 8,
      "Name": "Nerve Control",
      "Description": "This level tests your consistency and ability to handle stress near the end of the level.",
      "Ordering": 9
    }
  },
  {
    "TagID": 4,
    "ReactCount": 587,
    "HasVoted": 0,
    "Tag": {
      "ID": 4,
      "Name": "UFO",
      "Description": "This level has UFO sections that make up a large portion of its difficulty.",
      "Ordering": 4
    }
  },
  {
    "TagID": 12,
    "ReactCount": 437,
    "HasVoted": 0,
    "Tag": {
      "ID": 12,
      "Name": "Chokepoints",
      "Description": "This level contains parts with very condensed difficulty in relation to the rest of the level.",
      "Ordering": 13
    }
  },
  {
    "TagID": 9,
    "ReactCount": 275,
    "HasVoted": 0,
    "Tag": {
      "ID": 9,
      "Name": "Memory",
      "Description": "This level requires remembering a complex path to complete, usually with several fakes, potential routes, and/or visual obscurity.",
      "Ordering": 10
    }
  },
  {
    "TagID": 10,
    "ReactCount": 216,
    "HasVoted": 0,
    "Tag": {
      "ID": 10,
      "Name": "Learny",
      "Description": "This level needs a significant time investment in order to understand its complex/unintuitive gameplay.",
      "Ordering": 11
    }
  },
  {
    "TagID": 16,
    "ReactCount": 91,
    "HasVoted": 0,
    "Tag": {
      "ID": 16,
      "Name": "Overall",
      "Description": "This level has no specific skillset it tests, instead drawing on multiple skillsets in smaller proportion for its difficulty.",
      "Ordering": 17
    }
  },
  {
    "TagID": 14,
    "ReactCount": 65,
    "HasVoted": 0,
    "Tag": {
      "ID": 14,
      "Name": "Timings",
      "Description": "This level tests your ability to perform many very precise inputs.",
      "Ordering": 15
    }
  },
  {
    "TagID": 1,
    "ReactCount": 53,
    "HasVoted": 0,
    "Tag": {
      "ID": 1,
      "Name": "Cube",
      "Description": "This level has cube sections that make up a large portion of its difficulty.",
      "Ordering": 1
    }
  },
  {
    "TagID": 19,
    "ReactCount": 31,
    "HasVoted": 0,
    "Tag": {
      "ID": 19,
      "Name": "Slow-Paced",
      "Description": "This level has slower-moving sections (0.5x) for a large part of the level.",
      "Ordering": 20
    }
  },
  {
    "TagID": 3,
    "ReactCount": 18,
    "HasVoted": 0,
    "Tag": {
      "ID": 3,
      "Name": "Ball",
      "Description": "This level has ball sections that make up a large portion of its difficulty.",
      "Ordering": 3
    }
  },
  {
    "TagID": 13,
    "ReactCount": 18,
    "HasVoted": 0,
    "Tag": {
      "ID": 13,
      "Name": "High CPS",
      "Description": "This level has several sections that require very fast (usually controlled) inputs.",
      "Ordering": 14
    }
  },
  {
    "TagID": 15,
    "ReactCount": 10,
    "HasVoted": 0,
    "Tag": {
      "ID": 15,
      "Name": "Flow",
      "Description": "This level has many dynamic gameplay transitions throughout the level, forming a \"smooth\" and \"flowy\" type of gameplay.",
      "Ordering": 16
    }
  },
  {
    "TagID": 17,
    "ReactCount": 9,
    "HasVoted": 0,
    "Tag": {
      "ID": 17,
      "Name": "Gimmicky",
      "Description": "This level primarily focuses on developing an experimental, unorthodox gameplay type.",
      "Ordering": 18
    }
  },
  {
    "TagID": 18,
    "ReactCount": 9,
    "HasVoted": 0,
    "Tag": {
      "ID": 18,
      "Name": "Fast-Paced",
      "Description": "This level has fast-moving sections (3x or 4x speed) for the majority of the level.",
      "Ordering": 19
    }
  }
]
```
### `/api/user/{userID}/submissions`
This endpoint is particularly useful because we can get all the levels a person has submitted a rating for and use that to build a profile of their skillset from that list. Of course, this assumes that a person only submits a rating for a level after completing the level. The GDDL does allow users to submit ratings for levels that haven't completed, but it's rarely ever the case that happens. **NOTE:** I actually used my own userID for the Curl command.
`Curl Command`:
```
curl -X 'GET' \
  'https://gdladder.com/api/user/13876/submissions?limit=25&page=0' \
  -H 'accept: application/json'
```
`Response Body`:
```
{
  "total": 67,
  "limit": 25,
  "page": 0,
  "submissions": [
    {
      "ID": 1223513,
      "Rating": 3,
      "Enjoyment": 7,
      "Proof": null,
      "DateAdded": "2026-03-26T03:10:39.743Z",
      "Level": {
        "ID": 3,
        "Rating": 4.709340427602724,
        "Enjoyment": 7.295954125517681,
        "Meta": {
          "Name": "Deadlocked",
          "Difficulty": "Official",
          "Length": 4,
          "Rarity": 0,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Deadlocked"
          },
          "Publisher": {
            "name": "RobTop"
          }
        }
      }
    },
    {
      "ID": 1223622,
      "Rating": 1,
      "Enjoyment": 5,
      "Proof": null,
      "DateAdded": "2026-03-26T02:54:53.359Z",
      "Level": {
        "ID": 897342,
        "Rating": 5.640897755610972,
        "Enjoyment": 4.871794871794871,
        "Meta": {
          "Name": "electro ufo mix",
          "Difficulty": "Medium",
          "Length": 4,
          "Rarity": 0,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Electrodynamix"
          },
          "Publisher": null
        }
      }
    },
    {
      "ID": 1223565,
      "Rating": 3,
      "Enjoyment": 7,
      "Proof": null,
      "DateAdded": "2026-03-26T03:44:37.534Z",
      "Level": {
        "ID": 2997354,
        "Rating": 4.12888198757764,
        "Enjoyment": 7.053116857085588,
        "Meta": {
          "Name": "DeCode",
          "Difficulty": "Easy",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "-Endgame-"
          },
          "Publisher": {
            "name": "Rek3dge"
          }
        }
      }
    },
    {
      "ID": 1220785,
      "Rating": 10,
      "Enjoyment": 8,
      "Proof": null,
      "DateAdded": "2026-03-25T04:12:16.105Z",
      "Level": {
        "ID": 3264805,
        "Rating": 7.087696335078534,
        "Enjoyment": 5.959016393442623,
        "Meta": {
          "Name": "Theory of SkriLLex",
          "Difficulty": "Medium",
          "Length": 4,
          "Rarity": 0,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Skrillex GD Remix2"
          },
          "Publisher": {
            "name": "noobas"
          }
        }
      }
    },
    {
      "ID": 1220716,
      "Rating": 12,
      "Enjoyment": 5,
      "Proof": null,
      "DateAdded": "2026-03-25T03:36:48.386Z",
      "Level": {
        "ID": 4284013,
        "Rating": 11.166031054208663,
        "Enjoyment": 6.705294435440303,
        "Meta": {
          "Name": "Nine Circles",
          "Difficulty": "Hard",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "NK - Nine Circles"
          },
          "Publisher": {
            "name": "Zobros"
          }
        }
      }
    },
    {
      "ID": 1220674,
      "Rating": 16,
      "Enjoyment": 8,
      "Proof": null,
      "DateAdded": "2026-03-25T03:12:47.593Z",
      "Level": {
        "ID": 4957691,
        "Rating": 15.746180384425825,
        "Enjoyment": 7.350623929532665,
        "Meta": {
          "Name": "Windy Landscape",
          "Difficulty": "Insane",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "TheFatRat - Windfall"
          },
          "Publisher": {
            "name": "WOOGI1411"
          }
        }
      }
    },
    {
      "ID": 1220697,
      "Rating": 16,
      "Enjoyment": 4,
      "Proof": null,
      "DateAdded": "2026-03-25T03:20:11.319Z",
      "Level": {
        "ID": 5310094,
        "Rating": 13.776223776223775,
        "Enjoyment": 5.921539230384807,
        "Meta": {
          "Name": "Fairydust",
          "Difficulty": "Hard",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "NK - Fairydust"
          },
          "Publisher": {
            "name": "mkComic"
          }
        }
      }
    },
    {
      "ID": 1220722,
      "Rating": 12,
      "Enjoyment": 8,
      "Proof": null,
      "DateAdded": "2026-03-25T03:39:37.081Z",
      "Level": {
        "ID": 6939821,
        "Rating": 11.13617606602476,
        "Enjoyment": 6.705868919844713,
        "Meta": {
          "Name": "Jawbreaker",
          "Difficulty": "Hard",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "NK - Jawbreaker"
          },
          "Publisher": {
            "name": "ZenthicAlpha"
          }
        }
      }
    },
    {
      "ID": 1223675,
      "Rating": 2,
      "Enjoyment": 8,
      "Proof": null,
      "DateAdded": "2026-03-26T04:25:53.726Z",
      "Level": {
        "ID": 7116121,
        "Rating": 3.1370146678170836,
        "Enjoyment": 6.3323170731707314,
        "Meta": {
          "Name": "Problematic",
          "Difficulty": "Easy",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "~NK~ Problematic"
          },
          "Publisher": {
            "name": "Dhafin"
          }
        }
      }
    },
    {
      "ID": 1220673,
      "Rating": 16,
      "Enjoyment": 9,
      "Proof": null,
      "DateAdded": "2026-03-25T03:11:29.831Z",
      "Level": {
        "ID": 8304817,
        "Rating": 15.65625,
        "Enjoyment": 7.157894736842105,
        "Meta": {
          "Name": "Melody of Violins",
          "Difficulty": "Insane",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Dance Of The Violins"
          },
          "Publisher": {
            "name": "WOOGI1411"
          }
        }
      }
    },
    {
      "ID": 1223667,
      "Rating": 4,
      "Enjoyment": 6,
      "Proof": null,
      "DateAdded": "2026-03-26T04:23:21.099Z",
      "Level": {
        "ID": 11202046,
        "Rating": 3.7066246056782335,
        "Enjoyment": 4.914529914529915,
        "Meta": {
          "Name": "The Robotic Rush",
          "Difficulty": "Easy",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Flirt Flirt Oh It Hurts"
          },
          "Publisher": {
            "name": "Andromeda GMD"
          }
        }
      }
    },
    {
      "ID": 1223742,
      "Rating": 2,
      "Enjoyment": 6,
      "Proof": null,
      "DateAdded": "2026-03-26T04:56:48.578Z",
      "Level": {
        "ID": 14850167,
        "Rating": 2.9030898876404496,
        "Enjoyment": 5.927357032457496,
        "Meta": {
          "Name": "Horizon",
          "Difficulty": "Easy",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "This Game RmX Off Vocal"
          },
          "Publisher": {
            "name": "Mylon"
          }
        }
      }
    },
    {
      "ID": 1223634,
      "Rating": 1,
      "Enjoyment": 8,
      "Proof": null,
      "DateAdded": "2026-03-26T04:01:50.511Z",
      "Level": {
        "ID": 15619194,
        "Rating": 3.759005580923389,
        "Enjoyment": 7.228051391862955,
        "Meta": {
          "Name": "Motion",
          "Difficulty": "Easy",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Pursuit"
          },
          "Publisher": {
            "name": "TamaN"
          }
        }
      }
    },
    {
      "ID": 1220727,
      "Rating": 7,
      "Enjoyment": 8,
      "Proof": null,
      "DateAdded": "2026-03-25T03:41:35.655Z",
      "Level": {
        "ID": 17238943,
        "Rating": 8.157894736842104,
        "Enjoyment": 4.25,
        "Meta": {
          "Name": "Quadcore",
          "Difficulty": "Medium",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Space Battle"
          },
          "Publisher": {
            "name": "Dudex"
          }
        }
      }
    },
    {
      "ID": 1223671,
      "Rating": 4,
      "Enjoyment": 7,
      "Proof": null,
      "DateAdded": "2026-03-26T04:24:40.615Z",
      "Level": {
        "ID": 18735780,
        "Rating": 3.161500815660685,
        "Enjoyment": 6.884631758194977,
        "Meta": {
          "Name": "Dear Nostalgists",
          "Difficulty": "Easy",
          "Length": 5,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Bossfight - Okiba Crackdown"
          },
          "Publisher": {
            "name": "TriAxis"
          }
        }
      }
    },
    {
      "ID": 1220711,
      "Rating": 14,
      "Enjoyment": 3,
      "Proof": null,
      "DateAdded": "2026-03-25T03:30:27.261Z",
      "Level": {
        "ID": 38445559,
        "Rating": 12.08125,
        "Enjoyment": 6.773960216998192,
        "Meta": {
          "Name": "ThermoDynamix",
          "Difficulty": "Hard",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "{dj-N} Thermodynamix"
          },
          "Publisher": {
            "name": "flash"
          }
        }
      }
    },
    {
      "ID": 1220771,
      "Rating": 6,
      "Enjoyment": 9,
      "Proof": null,
      "DateAdded": "2026-03-25T04:21:32.224Z",
      "Level": {
        "ID": 58939191,
        "Rating": 6.874708729162933,
        "Enjoyment": 7.829670329670329,
        "Meta": {
          "Name": "Red Haze",
          "Difficulty": "Medium",
          "Length": 4,
          "Rarity": 2,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Creo - Red Haze"
          },
          "Publisher": {
            "name": "ToastLord"
          }
        }
      }
    },
    {
      "ID": 1223623,
      "Rating": 9,
      "Enjoyment": 10,
      "Proof": null,
      "DateAdded": "2026-03-26T03:00:17.847Z",
      "Level": {
        "ID": 60858722,
        "Rating": 5.789223454833597,
        "Enjoyment": 7.69672131147541,
        "Meta": {
          "Name": "Ascent",
          "Difficulty": "Medium",
          "Length": 4,
          "Rarity": 2,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Creo - Crazy"
          },
          "Publisher": {
            "name": "JustBasic"
          }
        }
      }
    },
    {
      "ID": 1220766,
      "Rating": 7,
      "Enjoyment": 10,
      "Proof": null,
      "DateAdded": "2026-03-25T04:15:03.059Z",
      "Level": {
        "ID": 60887211,
        "Rating": 7.162310030395137,
        "Enjoyment": 8.058929645219482,
        "Meta": {
          "Name": "Ultra violence",
          "Difficulty": "Medium",
          "Length": 4,
          "Rarity": 2,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "ELEPS - POWERSOUND (DUBSTEP)"
          },
          "Publisher": {
            "name": "Xender Game"
          }
        }
      }
    },
    {
      "ID": 1220698,
      "Rating": 19,
      "Enjoyment": 10,
      "Proof": null,
      "DateAdded": "2026-03-25T02:59:01.279Z",
      "Level": {
        "ID": 61137742,
        "Rating": 18.147217861503574,
        "Enjoyment": 8.130849220103986,
        "Meta": {
          "Name": "Leyak",
          "Difficulty": "Insane",
          "Length": 4,
          "Rarity": 2,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Helvetican - Bufu"
          },
          "Publisher": {
            "name": "EnZore"
          }
        }
      }
    },
    {
      "ID": 1220751,
      "Rating": 7,
      "Enjoyment": 10,
      "Proof": null,
      "DateAdded": "2026-03-25T04:01:29.342Z",
      "Level": {
        "ID": 67113181,
        "Rating": 7.923076923076923,
        "Enjoyment": 7.8110964332893,
        "Meta": {
          "Name": "Scarlet Smog",
          "Difficulty": "Medium",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Creo - Red Haze"
          },
          "Publisher": {
            "name": "ToastLord"
          }
        }
      }
    },
    {
      "ID": 1220712,
      "Rating": 14,
      "Enjoyment": 4,
      "Proof": null,
      "DateAdded": "2026-03-25T03:31:26.073Z",
      "Level": {
        "ID": 67461519,
        "Rating": 12.137559808612439,
        "Enjoyment": 5.518072289156627,
        "Meta": {
          "Name": "Pain Elemental",
          "Difficulty": "Hard",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "-Pain Engine-"
          },
          "Publisher": {
            "name": "loogiah"
          }
        }
      }
    },
    {
      "ID": 1220708,
      "Rating": 13,
      "Enjoyment": 8,
      "Proof": null,
      "DateAdded": "2026-03-25T03:27:58.954Z",
      "Level": {
        "ID": 71144442,
        "Rating": 13.646048109965635,
        "Enjoyment": 7.5,
        "Meta": {
          "Name": "Luminescent",
          "Difficulty": "Hard",
          "Length": 4,
          "Rarity": 0,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Creo - Atmosphere"
          },
          "Publisher": {
            "name": "SouljaBoyCrankD"
          }
        }
      }
    },
    {
      "ID": 1220787,
      "Rating": 6,
      "Enjoyment": 9,
      "Proof": null,
      "DateAdded": "2026-03-25T04:25:37.490Z",
      "Level": {
        "ID": 77614559,
        "Rating": 6.998322147651007,
        "Enjoyment": 7.044255319148936,
        "Meta": {
          "Name": "red dart",
          "Difficulty": "Medium",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "CursedOS"
          },
          "Publisher": {
            "name": "4chairs"
          }
        }
      }
    },
    {
      "ID": 1223567,
      "Rating": 5,
      "Enjoyment": 6,
      "Proof": null,
      "DateAdded": "2026-03-26T03:45:18.315Z",
      "Level": {
        "ID": 77660587,
        "Rating": 4.280701754385965,
        "Enjoyment": 6.994202898550725,
        "Meta": {
          "Name": "Neon Castle",
          "Difficulty": "Easy",
          "Length": 4,
          "Rarity": 1,
          "IsTwoPlayer": false,
          "Song": {
            "Name": "Slam"
          },
          "Publisher": {
            "name": "PotatoBaby"
          }
        }
      }
    }
  ]
}
```
### `/api/tags`
We likely don't need to hit this endpoint at all. It's likely the tags won't change often. But the information returned by this endpoint does provide useful information about all the tags currently stored in the GDDL, which we want to use in our embedding.
`Curl Command`:
```
curl -X 'GET' \
  'https://gdladder.com/api/tags' \
  -H 'accept: */*'
```
`Response Body`:
```
[
  {
    "ID": 1,
    "Name": "Cube",
    "Description": "This level has cube sections that make up a large portion of its difficulty.",
    "Ordering": 1
  },
  {
    "ID": 2,
    "Name": "Ship",
    "Description": "This level has ship sections that make up a large portion of its difficulty.",
    "Ordering": 2
  },
  {
    "ID": 3,
    "Name": "Ball",
    "Description": "This level has ball sections that make up a large portion of its difficulty.",
    "Ordering": 3
  },
  {
    "ID": 4,
    "Name": "UFO",
    "Description": "This level has UFO sections that make up a large portion of its difficulty.",
    "Ordering": 4
  },
  {
    "ID": 5,
    "Name": "Wave",
    "Description": "This level has wave sections that make up a large portion of its difficulty.",
    "Ordering": 5
  },
  {
    "ID": 6,
    "Name": "Robot",
    "Description": "This level has robot sections that make up a large portion of its difficulty.",
    "Ordering": 6
  },
  {
    "ID": 7,
    "Name": "Spider",
    "Description": "This level has spider sections that make up a large portion of its difficulty.",
    "Ordering": 7
  },
  {
    "ID": 20,
    "Name": "Swing",
    "Description": "This level has swing sections that make up a large portion of its difficulty.",
    "Ordering": 8
  },
  {
    "ID": 8,
    "Name": "Nerve Control",
    "Description": "This level tests your consistency and ability to handle stress near the end of the level.",
    "Ordering": 9
  },
  {
    "ID": 9,
    "Name": "Memory",
    "Description": "This level requires remembering a complex path to complete, usually with several fakes, potential routes, and/or visual obscurity.",
    "Ordering": 10
  },
  {
    "ID": 10,
    "Name": "Learny",
    "Description": "This level needs a significant time investment in order to understand its complex/unintuitive gameplay.",
    "Ordering": 11
  },
  {
    "ID": 11,
    "Name": "Duals",
    "Description": "This level has duals that make up a large portion of its difficulty. Generally refers to asymmetrical duals.",
    "Ordering": 12
  },
  {
    "ID": 12,
    "Name": "Chokepoints",
    "Description": "This level contains parts with very condensed difficulty in relation to the rest of the level.",
    "Ordering": 13
  },
  {
    "ID": 13,
    "Name": "High CPS",
    "Description": "This level has several sections that require very fast (usually controlled) inputs.",
    "Ordering": 14
  },
  {
    "ID": 14,
    "Name": "Timings",
    "Description": "This level tests your ability to perform many very precise inputs.",
    "Ordering": 15
  },
  {
    "ID": 15,
    "Name": "Flow",
    "Description": "This level has many dynamic gameplay transitions throughout the level, forming a \"smooth\" and \"flowy\" type of gameplay.",
    "Ordering": 16
  },
  {
    "ID": 16,
    "Name": "Overall",
    "Description": "This level has no specific skillset it tests, instead drawing on multiple skillsets in smaller proportion for its difficulty.",
    "Ordering": 17
  },
  {
    "ID": 17,
    "Name": "Gimmicky",
    "Description": "This level primarily focuses on developing an experimental, unorthodox gameplay type.",
    "Ordering": 18
  },
  {
    "ID": 18,
    "Name": "Fast-Paced",
    "Description": "This level has fast-moving sections (3x or 4x speed) for the majority of the level.",
    "Ordering": 19
  },
  {
    "ID": 19,
    "Name": "Slow-Paced",
    "Description": "This level has slower-moving sections (0.5x) for a large part of the level.",
    "Ordering": 20
  }
]
```