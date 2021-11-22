
class Deflections:
    def __init__(self, results, controlVariables):
        self.cruise = {
            "aileron": None,
            "elevator": None,
            "rudder": None,
            "flap": None
        }
        self.max = {
            "aileron": 0,
            "elevator": 0,
            "rudder": 0,
            "flap": 0
        }
        self.maxCase = {
            "aileron": None,
            "elevator": None,
            "rudder": None,
            "flap": None
        }
        for k, v in results.items():
            for key in controlVariables.keys():
                self._compare(k, v, key)

    def _compare(self, k, v, controlSurface):
        if abs(v["Totals"][controlSurface]) > abs(self.max[controlSurface]):
            self.max[controlSurface] = v["Totals"][controlSurface]
            self.maxCase[controlSurface] = k

        if k == "trimmed":
            self.cruise[controlSurface] = v["Totals"][controlSurface]
