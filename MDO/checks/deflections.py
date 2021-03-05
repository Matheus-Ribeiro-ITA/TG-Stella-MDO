
class Deflections:
    def __init__(self, results):
        self.cruise ={
            "aileron": None,
            "elevator": None,
            "rudder": None
        }
        self.max = {
            "aileron": 0,
            "elevator": 0,
            "rudder": 0
        }
        self.maxCase = {
            "aileron": None,
            "elevator": None,
            "rudder": None
        }
        for k, v in results.items():
            self._compare(k, v, "aileron")
            self._compare(k, v, "elevator")
            self._compare(k, v, "rudder")

    def _compare(self, k, v, controlSurface):
        # self.ailerons.append({k: v["Totals"][surface]})
        if abs(v["Totals"][controlSurface]) > abs(self.max[controlSurface]):
            self.max[controlSurface] = v["Totals"][controlSurface]
            self.maxCase[controlSurface] = k

        if k == "trimmed":
            self.cruise[controlSurface] = v["Totals"][controlSurface]
