import csv
import json
from collections import defaultdict, namedtuple

import geojson
import numpy
from geojson import Feature, FeatureCollection, Point
from sklearn import cluster


TOWER_LABELS = [
    'radio',
    'mcc',
    'mnc',
    'area',
    'cell',
    'unit',
    'lon',
    'lat',
    'range',
    'samples',
    'changeable',
    'created',
    'updated',
    'averageSignal'
]

Tower = namedtuple('Tower', TOWER_LABELS)


def load_towers_csv():
    with open('invalid.csv', 'rb') as csvfile:
        return list(csv.reader(csvfile))


def parse_towers(towers_csv):
    towers = []

    for tower_row in towers_csv:
        if len(tower_row) == 13:
            tower_row = tower_row + [0,]
        for i in range(len(tower_row)):
            try:
                tower_row[i] = float(tower_row[i])
            except:
                pass
        towers.append(Tower(*tower_row))

    return towers


def get_training_row(tower):
    return (tower.lat, tower.lon, tower.mcc, tower.mnc)


def build_tower_array(towers):
    towers_train = [get_training_row(tower) for tower in towers]
    return numpy.ndarray(
        shape=(len(towers_train), len(towers_train[0])),
        dtype=float,
        buffer=numpy.array(towers_train)
    )


def get_mcc_mncs(towers):
    mcc_mncs = set([(tower.mcc, tower.mnc) for tower in towers])
    clustered = defaultdict(list)
    for tower in towers:
        clustered[(tower.mcc, tower.mnc)].append(tower)
    return clustered


def cluster_towers(towers, n_clusters=2000):
    towers_array = build_tower_array(towers)

    kmeans = cluster.KMeans(n_clusters=n_clusters)
    kmeans.fit(towers_array)

    towers_labeled = defaultdict(list)
    for tower, label in zip(towers, kmeans.labels_):
        towers_labeled[label].append(tower)

    return towers_labeled


def find_bounding_boxes(towers_labeled):
    bounding_boxes = {}
    for label, towers in towers_labeled.items():
        min_lat = min([tower.lat for tower in towers])
        min_lon = min([tower.lon for tower in towers])
        max_lat = max([tower.lat for tower in towers])
        max_lon = max([tower.lon for tower in towers])
        area = abs(max_lat - min_lat) * abs(max_lon - min_lon)
        bounding_boxes[str(label)] = {
            'min_lat': min_lat,
            'min_lon': min_lon,
            'max_lat': max_lat,
            'max_lon': max_lon,
            'area': area,
            'networks': list(set([(tower.mcc, tower.mnc) for tower in towers])),
        }

    return bounding_boxes


def export_geojson_points(towers_labeled):
    feature_collection = FeatureCollection(
        [Feature(
            geometry=Point((
                float(tower.lat),
                float(tower.lon)
            )),
            properties={
                'mcc': tower.mcc,
                'mnc': tower.mnc
            }
        ) for tower in towers_labeled]
    )


def write_geojson(geojson):
    with open('towers.geojson', 'wb') as tower_geojson_file:
        tower_geojson_file.write(geojson.dumps(feature_collection))


def write_json(tower_cluster_json):
    with open('tower_clusters.json', 'wb') as json_file:
        json_file.write(json.dumps(tower_cluster_json))


def write_js(tower_cluster_json):
    with open('tower_clusters_data.js', 'wb') as js_file:
        js_file.write('TOWERS_DATA = {data};'.format(data=json.dumps(tower_cluster_json)))


def main():
    towers_csv = load_towers_csv()
    towers = parse_towers(towers_csv)
    towers_labeled = cluster_towers(towers)
    bounding_boxes = find_bounding_boxes(towers_labeled)
    write_js(bounding_boxes)
    return towers, towers_labeled, bounding_boxes


if __name__ == '__main__':
    main()
