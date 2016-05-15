import datetime
import json
import logging
import random

import requests
from xlrd import open_workbook

logger = logging.getLogger(__name__)

YANDEX_KEY = 'AGMxNlcBAAAA0yj5PgIAPvJB1n78DFuaVj8vMTdfl9XH0rkAAAAAAAAAAAD00qkNa3lj-mshcwiMbdL0PINy9Q=='


class Matrix(object):
    matrix = []
    drivers = []

    def __init__(self, filename, driver_cells, point_by_driver_rows, sheet_index):
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
            if len(cell_title) > 1:
                lng = float(cell_title[1].split(',')[0].strip())
                lat = float(cell_title[1].split(',')[1].strip())
            else:
                lng = random.randint(5545, 5565) / 100
                lat = random.randint(3605, 3625) / 100

            value_cell = self.sheet.cell(row, col + 1).value
            if not point_title:
                continue

            points.append({
                'point_title': point_title,
                'point_coordinates': {
                    'lng': lng,
                    'lat': lat,
                },
                'shortest_path': None,
                'point_value': float(value_cell) if value_cell else 0,
            })

        # for i, point in enumerate(points[:]):
        #     other_points = list(filter(lambda p: p != point, points))
        #     points[i]['shortest_path'] = self.get_shortest_path(point, other_points)

        return points

    def get_shortest_path(self, point, points):
        min_path = 0
        for dest_point in points:
            import pdb; pdb.set_trace()
            router_url = 'https://router.project-osrm.org/viaroute?instructions=false&alt=false&z=15&loc={lat_s},{lng_s}&loc={lat_d},{lng_d}'.format(
                lat_s=point['point_coordinates']['lat'], lng_s=point['point_coordinates']['lng'],
                lat_d=dest_point['point_coordinates']['lat'], lng_d=dest_point['point_coordinates']['lng'],
            )
            response = requests.get(router_url)

    def print_drivers(self):
        for driver in self.drivers:
            print(driver)

    def create_matrix(self):
        raise NotImplementedError

    def get_maps(self):
        api_url = 'https://static-maps.yandex.ru/1.x/?'
        url_parts = [
        'l=map',
        'pt=37.620070,55.753630,pmwtm1~37.64,55.76363,pmwtm99'
        ]
        url = api_url + '&'.join(url_parts)
        print(url)
        request = requests.get(url)
        with open('test.png', 'w') as output:
            output.write(request.content)

    def save_data_to_json(self):
        with open('data.json', 'w') as output:
            output.write(json.dumps(self.drivers))


matrix = Matrix(
    filename='sample.xlsx',
    driver_cells=[[0, 1], [0, 3], [0, 5], [0, 6], [0, 8]],
    point_by_driver_rows=[[3, 28], [3, 14], [0, 0], [3, 6], [3, 8]],
    sheet_index=1)

matrix.read_drivers()
matrix.save_data_to_json()
