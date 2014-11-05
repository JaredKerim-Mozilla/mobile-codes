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
    'net',
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
        towers.append(Tower(*tower_row))

    return towers


def get_training_row(tower):
    return map(float, (tower.mcc, tower.net, tower.lat, tower.lon))


def build_tower_array(towers):
    towers_train = [get_training_row(tower) for tower in towers]
    return numpy.ndarray(
        shape=(len(towers_train), 4),
        dtype=float,
        buffer=numpy.array(towers_train)
    )


def cluster_towers(towers, n_clusters=100):
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
        bounding_boxes[str(label)] = {
            'min_lat': min([tower.lat for tower in towers]),
            'min_lon': min([tower.lon for tower in towers]),
            'max_lat': max([tower.lat for tower in towers]),
            'max_lon': max([tower.lon for tower in towers]),
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
                'mnc': tower.net
            }
        ) for tower in towers_labeled]
    )


def write_geojson(geojson):
    with open('towers.geojson', 'wb') as tower_geojson_file:
        tower_geojson_file.write(geojson.dumps(feature_collection))


def write_json(tower_cluster_json):
    with open('tower_clusters.json', 'wb') as json_file:
        json_file.write(json.dumps(tower_cluster_json))


def main():
    towers_csv = load_towers_csv()
    towers = parse_towers(towers_csv)
    towers_labeled = cluster_towers(towers)
    bounding_boxes = find_bounding_boxes(towers_labeled)
    write_json(bounding_boxes)
