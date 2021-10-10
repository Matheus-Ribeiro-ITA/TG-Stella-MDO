'''
INSTITUTO TECNOLÓGICO DE AERONÁUTICA
PROGRAMA DE ESPECIALIZAÇÃO EM ENGENHARIA AERONÁUTICA
OTIMIZAÇÃO MULTIDISCIPLINAR

This script generates correlation plots

REQUIRED PACKAGES (if not using Anaconda)
pip3 install pandas
pip3 install seaborn
pip3 install statsmodels
pip3 install pymoo

Cap. Ney Sêcco 2021
'''

#IMPORTS
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pymoo.factory import get_sampling
from pymoo.interface import sample
from DOE.utils.aux_tools import corrdot

#=========================================

# SETUP

# Define design function
def des_funcs(Xinp):

    x1, x2, x3 = Xinp

    f1 = x1**2 + (x2-2)**2 - 0.0001*x3

    f2 = -x2**2

    # Returns
    return f1, f2

# Give number of input variables
n_inputs = 3

# Lower and upeer bounds of each input variable
lb = [-5.0, -5.0, -5.0]
ub = [ 5.0,  5.0,  5.0]

# Desired number of samples
n_samples = 20

# Sampling type
sampling_type = 'real_random'
#sampling_type = 'real_lhs'

# Plot type (0-simple, 1-complete)
plot_type = 0
#=========================================

# EXECUTION

# Set random seed to make results repeatable
np.random.seed(123)

# Initialize sampler
sampling = get_sampling(sampling_type)

# Draw samples
X = sample(sampling, n_samples, n_inputs)

# Samples are originally between 0 and 1,
# so we need to scale them to the desired interval
for ii in range(n_inputs):
    X[:,ii] = lb[ii] + (ub[ii] - lb[ii])*X[:,ii]

# Execute all cases and store outputs
f1_samples = []
f2_samples = []
for ii in range(n_samples):

    # Evaluate sample
    (f1,f2) = des_funcs(X[ii,:])

    # Store the relevant information
    f1_samples.append(f1)
    f2_samples.append(f2)

# Create a pandas dataframe with all the information
df = pd.DataFrame({'x1' : X[:,0],
                   'x2' : X[:,1],
                   'x3' : X[:,2],
                   'f1' : f1_samples,
                   'f2' : f2_samples})

# Plot the correlation matrix
sns.set(style='white', font_scale=1.4)

if plot_type == 0:

    # Simple plot
    fig = sns.pairplot(df,corner=True)

elif plot_type == 1:

    # Complete plot
    # based on: https://stackoverflow.com/questions/48139899/correlation-matrix-plot-with-coefficients-on-one-side-scatterplots-on-another
    fig = sns.PairGrid(df, diag_sharey=False)
    fig.map_lower(sns.regplot, lowess=True, line_kws={'color': 'black'})
    fig.map_diag(sns.histplot)
    fig.map_upper(corrdot)

# Plot window
plt.tight_layout()
plt.show()

fig.savefig('doe.png')
