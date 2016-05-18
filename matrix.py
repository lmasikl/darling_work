import asyncio
import datetime
import json
import logging

import requests
from xlrd import open_workbook

logger = logging.getLogger(__name__)


class Matrix(object):
    matrix = []
    drivers = []

    def __init__(self, filename, driver_cells, point_by_driver_rows, sheet_index):
        self.data_file = '{0}.js'.format(filename.split('.')[0])
        self.sheet = open_workbook(filename=filename).sheet_by_index(sheet_index)
        self.driver_cells = driver_cells
        self.point_by_driver_rows = point_by_driver_rows

    def read_drivers(self):
        for i, cell in enumerate(self.driver_cells):
            row, col = cell
            self.drivers.append({
                'last_name': self.sheet.cell(row, col).value,
                'car': self.sheet.cell(row + 1, col).value,
                'points': list(self.read_driver_points(i, col))
            })

    def read_driver_points(self, driver_index, col):
        begin, end = self.point_by_driver_rows[driver_index]
        if begin == end:
            return []

        points = []
        for row in range(begin, end + 1):
            cell_title = self.sheet.cell(row, col).value.split('|')
            point_title = cell_title[0]
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
        if dest_point['point_title'] == point['point_title']:
            point['distances'].append({
                'distance': 0.0,
                'point_title': dest_point['point_title'],
            })
            return

        router_url = 'https://router.project-osrm.org/viaroute?instructions=false&alt=false&z=15&loc={lng_s},{lat_s}&loc={lng_d},{lat_d}'.format(
            lat_s=point['point_coordinates']['lat'], lng_s=point['point_coordinates']['lng'],
            lat_d=dest_point['point_coordinates']['lat'], lng_d=dest_point['point_coordinates']['lng'],
        )
        response = requests.get(router_url)
        result = json.loads(response.text)
        point['distances'].append({
            'distance': result['route_summary']['total_distance'] / 1000.0,
            'point_title': dest_point['point_title'],
        })

    def create_matrix(self):
        raise NotImplementedError

    def save_data_to_json(self):
        with open(self.data_file, 'w') as output:
            var = 'var drivers = {0};'.format(json.dumps(self.drivers))
            output.write(var)


def get_matrixes():
    return [
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


for matrix in get_matrixes():
    matrix.read_drivers()
    matrix.save_data_to_json()
