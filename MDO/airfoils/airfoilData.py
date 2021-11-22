import json


class AirfoilData:
    def __init__(self, name):
        with open("MDO/airfoils/airfoilPolar.json", "r") as file:
            self.airfoils = json.load(file)
            self.name = name.split('_')[0]
            self.cl = self.airfoils[name]["cl"]
            self.cd = self.airfoils[name]["cd"]
            self.claf = self.airfoils[name]["claf"]
            self.clmax = self.airfoils[name]["clmax"]

    def __str__(self):
        return f"{self.name}"
