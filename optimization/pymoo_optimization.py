from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.factory import get_problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from pymoo.core.problem import Problem
import pandas as pd
import numpy as np
import autograd.numpy as anp

import matplotlib.pyplot as plt

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.callback import Callback


class MyCallback(Callback):

    def __init__(self) -> None:
        super().__init__()
        self.data["best"] = []
        self.data["vars"] = []

    def notify(self, algorithm):
        self.data["best"].append(algorithm.pop.get("F").min())
        self.data["vars"].append(anp.column_stack([algorithm.pop.get("vars"), algorithm.pop.get("F")]))


problem = get_problem("sphere")


class SphereWithConstraint(Problem):

    def __init__(self):
        super().__init__(n_var=2, n_obj=2, n_constr=0, xl=0.0, xu=1.0)

    def _evaluate(self, x, out, *args, **kwargs):
        # out["F"] = np.sum((x - 0.5) ** 2, axis=1)
        # out["G"] = 0.1 - out["F"]

        # f1 = x[:, 0]
        # g = 1 + 9.0 / (self.n_var - 1) * anp.sum(x[:, 1:], axis=1)
        # f2 = g * (1 - anp.power((f1 / g), 0.5))
        #
        # out["F"] = anp.column_stack([f1, f2])

        f1 = x[:, 0] ** 2 + x[:, 1] ** 2
        f2 = - (x[:, 0] ** 2 + x[:, 1] ** 2)
        # f2 = 1 / (x[:, 0] ** 2 + x[:, 1] ** 2)

        out["vars"] = x
        out["F"] = anp.column_stack([f1, f2])

problem = SphereWithConstraint()

algorithm_name = 'NSGA2'
algorithm = NSGA2(pop_size=10)

res = minimize(problem,
               algorithm,
               ('n_gen', 20),
               seed=1,
               callback=MyCallback(),
               verbose=True)

# Save to csv
vars_history = res.algorithm.callback.data['vars']
generations_list = []

for i, list_vars in enumerate(vars_history):
    df_aux = pd.DataFrame(list_vars, columns=['var1', 'var2', 'f1', 'f2'])
    generations_list.append(df_aux)
    df_aux.to_csv(f'history/GA/{algorithm_name}_vars_{str(i)}')


plot = Scatter()
plot.add(problem.pareto_front(), plot_type="line", color="black", alpha=0.7)
plot.add(res.F, color="red")
plot.show()


val = res.algorithm.callback.data["best"]
plt.plot(np.arange(len(val)), val)
plt.show()



# class ZDT1(ZDT):
#
#     def _calc_paraeto_front(self, n_pareto_points=100):
#         x = anp.linspace(0, 1, n_pareto_points)
#         return anp.array([x, 1 - anp.sqrt(x)]).T
#
#     def _evaluate(self, x, out, *args, **kwargs):
#         f1 = x[:, 0]
#         g = 1 + 9.0 / (self.n_var - 1) * anp.sum(x[:, 1:], axis=1)
#         f2 = g * (1 - anp.power((f1 / g), 0.5))
#
#         out["F"] = anp.column_stack([f1, f2])
# problem = get_problem("zdt1")