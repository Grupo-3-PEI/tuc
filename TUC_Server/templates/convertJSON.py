import json

def convert(jsonfile):
    return json.dumps({ "type": "FeatureCollection",
                        "features": [
                                        {"type": "Feature",
                                         "geometry": { "type": "Point",
                                                       "coordinates": [ feature['lon'],
                                                                        feature['lat']]},
                                         "properties": { key: value
                                                         for key, value in feature.jsonfile()
                                                         if key not in ('lat', 'lon') }
                                        }
                                    for feature in json.loads(jsonfile)
                                    ]
                    })