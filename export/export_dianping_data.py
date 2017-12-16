import os, sys

import pandas as pd
import pymongo
import sqlite3

nb_dir = os.path.normpath(os.path.join(os.getcwd(), '..'))
os.listdir(nb_dir)
if nb_dir not in sys.path:
    sys.path.append(nb_dir)


def _get_dianping_data(f):
    conn = sqlite3.connect(f)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT tag, longitude, latitude, c.category, avg_rating, avg_price, v.business_id, name, city
    FROM venues v
    LEFT OUTER JOIN venue_categories vc ON (v.business_id = vc.business_id)
        LEFT OUTER JOIN categories c ON (vc.category = c.category)
            LEFT OUTER JOIN venues_tags vt ON (v.business_id = vt.business_id)
    """)
    venues = pd.DataFrame(cursor.fetchall())
    venues.columns = ['cn_tag', 'longitude', 'latitude', 'category', 'avg_rating', 'avg_price', 'business_id', 'name',
                      'city']

    return venues


def _get_venues_dict(venues):
    venues_tags = venues.groupby('business_id')['cn_tag'].apply(list)
    venues_list = venues.drop_duplicates(subset=list(venues)[1:]).drop('cn_tag', axis=1)
    result = pd.merge(venues_list, venues_tags.reset_index(), on='business_id')

    return result.to_dict(orient='records')


def _import_venues(venues_dict):
    client = pymongo.MongoClient('localhost', 27017)
    db = client.explorify
    dianping = db.dianping
    dianping.insert_many(venues_dict)


if __name__ == "__main__":
    venues = _get_dianping_data(f='../data/UTSEUS-shanghai-dianping.db')
    venues_dict = _get_venues_dict(venues)
    _import_venues(venues_dict)
