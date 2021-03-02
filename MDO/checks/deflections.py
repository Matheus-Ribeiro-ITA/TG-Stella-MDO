
class Deflections:
    def __init__(self, results):
        self.ailerons = []
        self.elevators = []
        self.rudders = []
        self.max = {
            "aileron": 0,
            "elevator": 0,
            "rudder": 0
        }
        for k, v in results.items():
            self._compare(k, v, "aileron")
            self._compare(k, v, "elevator")
            self._compare(k, v, "rudder")

    def _compare(self, k, v, surface):
        self.ailerons.append({k: v["Totals"][surface]})
        if abs(v["Totals"][surface]) > abs(self.max[surface]): self.max[surface] = v["Totals"][surface]