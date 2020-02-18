import os
import sys

import requests
from PyQt5.QtCore import Qt as core
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QInputDialog, QLineEdit, QPushButton

SCREEN_SIZE = [600, 500]
api_server = "http://static-maps.yandex.ru/1.x/"
unch_coor = []

# 37.530887 55.703118
# 54.195105 37.620373
# 55.755241 37.617779


class Map(QWidget):
    def __init__(self):
        super().__init__()
        self.ptlon, self.ptlat = '0.0', '0.0'
        self.is_pt = False
        self.coordinate = self.get_coord()
        self.level = 'map'
        self.delta = "0.002"
        self.REQUEST = {"ll": ",".join([self.coordinate[0], self.coordinate[1]]),
                        "spn": ",".join([self.delta, self.delta]),
                        "l": self.level}
        self.getImage(self.REQUEST)
        self.initUI()

    def get_coord(self):
        coor, okBtnPressed = QInputDialog.getText(self, "Координаты",
                                                  "Введите координаты через пробел")
        if okBtnPressed:
            if __name__ == '__main__':
                coor = coor.split()
                return coor

    def keyPressEvent(self, e):
        global unch_coor
        if e.key() == core.Key_Down:
            self.coordinate[1] = str(float(self.coordinate[1]) - 0.0003)

        if e.key() == core.Key_Up:
            self.coordinate[1] = str(float(self.coordinate[1]) + 0.0003)

        if e.key() == core.Key_Left:
            self.coordinate[0] = str(float(self.coordinate[0]) - 0.0003)

        if e.key() == core.Key_Right:
            self.coordinate[0] = str(float(self.coordinate[0]) + 0.0003)

        if e.key() == core.Key_PageDown:
            if float(self.delta) <= 90.0:
                self.delta = str(float(self.delta) + 0.002)

        if e.key() == core.Key_PageUp:
            if float(self.delta) > 0.0:
                self.delta = str(float(self.delta) - 0.002)

        if unch_coor != []:
            self.getImage({"ll": ",".join([self.coordinate[0], self.coordinate[1]]),
                           "spn": ",".join([self.delta, self.delta]),
                           "l": "map",
                           "pt": ",".join([unch_coor[0], unch_coor[1]]) + ",pm2rdm1"})
        else:
            self.getImage({"ll": ",".join([self.coordinate[0], self.coordinate[1]]),
                           "spn": ",".join([self.delta, self.delta]),
                           "l": "map"})

        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def getImage(self, req):
        response = requests.get(api_server, params=req)
        if not response:
            pass

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Карта')

        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

        self.name_label = QLabel(self)
        self.name_label.setText("Поиск:")
        self.name_label.move(320, 472)

        self.btn = QPushButton(self)
        self.btn.setText("Найти")
        self.btn.move(490, 469)

        self.btn_sput = QPushButton(self)
        self.btn_sput.setText("Спутник")
        self.btn_sput.move(10, 469)

        self.btn_map = QPushButton(self)
        self.btn_map.setText(" Схема ")
        self.btn_map.move(110, 469)

        self.btn_gib = QPushButton(self)
        self.btn_gib.setText("Гибрид")
        self.btn_gib.move(210, 469)

        self.name_input = QLineEdit(self)
        self.name_input.move(350, 470)

        self.btn.clicked.connect(self.find)
        self.btn_sput.clicked.connect(self.level_change)
        self.btn_map.clicked.connect(self.level_change)
        self.btn_gib.clicked.connect(self.level_change)

    def closeEvent(self, event):
        os.remove(self.map_file)

    def find(self):
        global unch_coor
        toponym_to_find = str(self.name_input.text())
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)

        if not response:
            pass

        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        unch_coor = [toponym_longitude, toponym_lattitude]

        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "spn": ",".join([self.delta, self.delta]),
            "l": "map",
            "pt": ",".join([toponym_longitude, toponym_lattitude]) + ",pm2rdm1"
        }
        self.getImage(map_params)
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def level_change(self):
        if self.btn_sput:
            self.level = 'sat'
        if self.btn_map:
            self.level = 'map'
        if self.btn_gib:
            self.level = 'sat,skl'

        if self.is_pt:
            map_params = {
                "ll": ",".join([self.coordinate[0], self.coordinate[1]]),
                "spn": ",".join([self.delta, self.delta]),
                "l": self.level,
                "pt": ",".join([self.ptlon, self.ptlat]) + ",pm2rdm1"

            }
        else:
            map_params = {
                "ll": ",".join([self.coordinate[0], self.coordinate[1]]),
                "spn": ",".join([self.delta, self.delta]),
                "l": self.level
            }
        self.getImage(map_params)
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())
