import os, sys
from operator import itemgetter
import numpy as np
import pandas as pd
import pymongo
import sqlite3

from sklearn.cluster import DBSCAN

blacklist = [
    "chine",
    "shanghai",
    "travel",
    "square",
    "city",
    "china",
    "cn",
    "squareformat",
    "asia",
    "uploaded:by=instagram",
    "shanghaishi",
    "iphoneography",
    "chinese",
    "instagramapp",
    "internations",
    "street",
    u'上海',
    u'中国',
  ]

nb_dir = os.path.normpath(os.path.join(os.getcwd(), '..'))
os.listdir(nb_dir)
if nb_dir not in sys.path:
    sys.path.append(nb_dir)

f = '../data/UTSEUS-shanghai-flickr.sqlite'

if __name__ == "__main__":

    print('Loading data...')
    conn = sqlite3.connect(f)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT * FROM photos
    ''')
    photos = pd.DataFrame(cursor.fetchall())

    print('Unsupervised learning...')

    # Don't forget to remove "sample" to get full dataset
    data_dbscan = photos[[1, 2, 10]].sample(500)
    data_dbscan.columns = ['latitude', 'longitude', 'tags']
    data_dbscan.head()
    X = data_dbscan[['latitude', 'longitude']].values

    kms_per_radian = 6371.0088

    def compute_dbscan(meters):
        epsilon = (meters * 0.001) / kms_per_radian
        db = DBSCAN(eps=epsilon, algorithm='ball_tree', metric='haversine').fit(np.radians(X))
        return db.labels_

    computings = map(compute_dbscan, range(100, 300))
    n_computings = map(lambda x: (len(set(x)), x), computings)
    labels = max(n_computings, key=itemgetter(0))[1]

    for label in set(labels):
        df = data_dbscan[(labels == label)]
        data_dbscan.loc[df.index, 'cluster_num'] = int(label)

    def compute_middle_point(df):
        tags = df['tags'].str.cat(sep=' ')
        return df.assign(tags=tags)[:1]

    final_data = data_dbscan.groupby('cluster_num').apply(lambda df: compute_middle_point(df))

    print('Removing black list words...')
    for word in blacklist:
        final_data['tags'] = final_data['tags'].apply(lambda tags: tags.replace(word, ''))

    documents = final_data.to_dict('records')
    for document in documents:
        document['tags'] = document['tags'].split(' ')
        document['tags'] = list(filter(None, document['tags']))

    print('Saving into database...')
    import pymongo
    client = pymongo.MongoClient('localhost', 27017)
    db = client.explorify
    flickr = db.flickr

    flickr.insert_many(documents)
