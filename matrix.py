import asyncio
import csv
import datetime
import json
import logging

import requests
from xlrd import open_workbook

logger = logging.getLogger(__name__)


class Matrix(object):
    matrix = []
    drivers = []
    cached_distances = None
    cache_file = 'distances_cache.csv'
    car_speed = 40

    def __init__(self, filename, driver_cells, point_by_driver_rows, sheet_index):
        self.data_file = '{0}.js'.format(filename.split('.')[0])
        self.sheet = open_workbook(filename=filename).sheet_by_index(sheet_index)
        self.driver_cells = driver_cells
        self.point_by_driver_rows = point_by_driver_rows
        self.upload_cache()

    def upload_cache(self):
        try:
            with open(self.cache_file, mode='r') as cache:
                reader = csv.reader(cache, delimiter=",")
                self.cached_distances = [{'start': row[0], 'dest': row[1], 'distance': row[2]} for row in reader]
        except FileNotFoundError:
            self.cached_distances = []

    def save_cache(self):
        with open(self.cache_file, mode='w') as cache:
            writer = csv.writer(cache, delimiter=",")
            [writer.writerow([record['start'], record['dest'], record['distance']]) for record in self.cached_distances]

    def read_drivers(self):
        for i, cell in enumerate(self.driver_cells):
            row, col = cell
            self.drivers.append({
                'last_name': self.sheet.cell(row, col).value.strip(),
                'car': self.sheet.cell(row + 1, col).value.strip(),
                'points': list(self.read_driver_points(i, col))
            })

    def read_driver_points(self, driver_index, col):
        begin, end = self.point_by_driver_rows[driver_index]
        if begin == end:
            return []

        points = []
        for row in range(begin, end + 1):
            cell_title = self.sheet.cell(row, col).value.split('|')
            point_title = cell_title[0].strip()
            lng = float(cell_title[1].split(',')[0].strip())
            lat = float(cell_title[1].split(',')[1].strip())
            value_cell = self.sheet.cell(row, col + 1).value
            if not point_title:
                continue

            points.append({
                'point_title': point_title,
                'point_coordinates': {
                    'lng': lng,
                    'lat': lat,
                },
                'distances': [],
                'point_value': float(value_cell) if value_cell else 0,
            })

        self.get_distances(points)
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.get_distances(points))
        # loop.close()

        return points

    def get_distances(self, points):
        for i, point in enumerate(points[:]):
            for dest_point in points:
                self.get_distance(point, dest_point)

    def get_distance(self, point, dest_point):
        cached_distance = self.get_from_cache(point, dest_point)
        if cached_distance is not None:
            point['distances'].append({
                'distance': cached_distance,
                'time': (60 / self.car_speed) * cached_distance,
                'point_title': dest_point['point_title']
            })

        elif dest_point['point_title'] == point['point_title']:
            point['distances'].append({
                'distance': 0.0,
                'time': 0,
                'point_title': dest_point['point_title'],
            })
        else:
            router_url = 'https://router.project-osrm.org/viaroute?'\
                        'instructions=false&alt=false&z=15&loc={lng_s},{lat_s}&loc={lng_d},{lat_d}'.format(
                            lat_s=point['point_coordinates']['lat'], lng_s=point['point_coordinates']['lng'],
                            lat_d=dest_point['point_coordinates']['lat'], lng_d=dest_point['point_coordinates']['lng'],
            )

            response = requests.get(router_url)
            result = json.loads(response.text)
            self.add_to_cache(point, dest_point, result)
            point['distances'].append({
                'distance': result['route_summary']['total_distance'] / 1000.0,
                'time': (60 / self.car_speed) * (result['route_summary']['total_distance'] / 1000.0),
                'point_title': dest_point['point_title'],
            })

    def get_from_cache(self, point, dest_point):
        def filter_function(cache_record):
            has_start_point = cache_record['start'] == point['point_title']
            has_dest_point = cache_record['dest'] == dest_point['point_title']
            return has_start_point and has_dest_point

        cache = list(filter(filter_function, self.cached_distances))
        if cache:
            return float(cache[0]['distance'])
        else:
            return None

    def add_to_cache(self, point, dest_point, data):
        self.cached_distances.append({
            'start': point['point_title'],
            'dest': dest_point['point_title'],
            'distance': data['route_summary']['total_distance'] / 1000.0,
        })

    def create_matrix(self):
        raise NotImplementedError

    def save_data_to_json(self):
        with open(self.data_file, 'w') as output:
            var = 'var drivers = {0};'.format(json.dumps(self.drivers))
            output.write(var)


def get_matrixes():
    return [
        # Matrix(
        #     filename='01_05_2016.xlsx',
        #     driver_cells=[[0, 1], [0, 3]],
        #     point_by_driver_rows=[[3, 4], [3, 4]],
        #     sheet_index=1),

        Matrix(
            filename='01_05_2016.xlsx',
            driver_cells=[[0, 1], [0, 3]],
            point_by_driver_rows=[[3, 24], [3, 8]],
            sheet_index=1),

        Matrix(
            filename='07_05_2016.xlsx',
            driver_cells=[[0, 1], [0, 3], [0, 6], [0, 8]],
            point_by_driver_rows=[[3, 22], [3, 15], [3, 6], [3, 8]],
            sheet_index=1),

        Matrix(
            filename='08_05_2016.xlsx',
            driver_cells=[[2, 1], [2, 3]],
            point_by_driver_rows=[[5, 27], [5, 12]],
            sheet_index=1),

        Matrix(
            filename='24_04_2016.xlsx',
            driver_cells=[[0, 1], [0, 3]],
            point_by_driver_rows=[[2, 22], [2, 9]],
            sheet_index=1),
    ]


begin = datetime.datetime.now()
for matrix in get_matrixes()[3:]:
    print('Process {} file'.format(matrix.data_file))
    matrix.read_drivers()
    matrix.save_data_to_json()
    matrix.save_cache()

print('Processed for {}'.format(datetime.datetime.now() - begin))
