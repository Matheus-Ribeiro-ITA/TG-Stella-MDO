from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.factory import get_problem
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from pymoo.core.problem import Problem
import numpy as np
import autograd.numpy as anp


# def problem_test(x):
#
#
#     return f1, f2


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

        out["F"] = anp.column_stack([f1, f2])

problem = SphereWithConstraint()

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

algorithm = NSGA2(pop_size=100)

res = minimize(problem,
               algorithm,
               ('n_gen', 200),
               seed=1,
               verbose=True)

plot = Scatter()
plot.add(problem.pareto_front(), plot_type="line", color="black", alpha=0.7)
plot.add(res.F, color="red")
plot.show()