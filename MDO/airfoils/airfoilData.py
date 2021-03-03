import json


class AirfoilData:
    def __init__(self, name):
        with open("MDO/airfoils/airfoilPolar.json", "r") as file:
            self.airfoils = json.load(file)
            self.name = name
            self.cl = self.airfoils[name]["cl"]
            self.cd = self.airfoils[name]["cd"]
            self.claf = self.airfoils[name]["claf"]

    def __str__(self):
        return f"{self.name}"
