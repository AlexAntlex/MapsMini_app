import os
import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QInputDialog, QLineEdit, QPushButton

SCREEN_SIZE = [600, 500]
api_server = "http://static-maps.yandex.ru/1.x/"
# 37.530887 55.703118
# 54.195105 37.620373
# 55.755241 37.617779


class Map(QWidget):
    def __init__(self):
        super().__init__()
        self.lon, self.lat = self.get_coord()
        self.delta = "0.002"
        self.REQUEST = {"ll": ",".join([self.lon, self.lat]),
                        "spn": ",".join([self.delta, self.delta]),
                        "l": "map"}
        self.getImage(self.REQUEST)
        self.initUI()

    def get_coord(self):
        coor, okBtnPressed = QInputDialog.getText(self, "Координаты",
                                                  "Введите координаты через пробел")
        if okBtnPressed:
            if __name__ == '__main__':
                coor = coor.split()
                return coor
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            if float(self.delta) > 0.0:
                self.delta = str(float(self.delta) - 0.002)
        if event.key() == Qt.Key_PageUp:
            if float(self.delta) <= 90.0:
                self.delta = str(float(self.delta) + 0.002)
        map_params = {
            "ll": ",".join([self.lon, self.lat]),
            "spn": ",".join([self.delta, self.delta]),
            "l": "map"
        }
        self.getImage(map_params)
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
        self.name_label.move(220, 472)

        self.btn = QPushButton(self)
        self.btn.setText("Найти")
        self.btn.move(390, 469)

        self.name_input = QLineEdit(self)
        self.name_input.move(250, 470)

        self.btn.clicked.connect(self.find)

    def closeEvent(self, event):
        os.remove(self.map_file)

    def find(self):
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

        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "spn": ",".join([self.delta, self.delta]),
            "l": "map",
            "pt": ",".join([toponym_longitude, toponym_lattitude]) + ",pm2rdm1"
        }
        self.getImage(map_params)
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())
