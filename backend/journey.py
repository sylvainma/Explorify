def compute_journey(keywords, price):
    '''Core algorithm to choose points of interests.'''

    return {
        'summary': {
            'total_time': 2.1, # hours
            'total_price': 352, # kuai
        },
        'departure': { # should be geojson point
            'latitude': 121.478,
            'longitude': 31.27,
            'time': 0.0 # hours from the beginning
        },
        'arrival': { # should be geojson point
            'latitude': 121.480,
            'longitude': 31.27,
            'time': 2.1 # hours from the beginning
        },
        'pois': [
            {
                'n': 1, # nth step
                'name': 'TTH restaurant',
                'latitude': 121.478,
                'longitude': 31.27
            },
            {
                'n': 2, # nth step
                'name': 'Chalam restaurant',
                'latitude': 121.480,
                'longitude': 31.27
            },
        ]
    }
