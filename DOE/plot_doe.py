import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pymoo.factory import get_sampling
from pymoo.interface import sample
from DOE.utils.aux_tools import corrdot


def plot_doe(plot_type=0, filename='results'):
    # ------------------------------------------------------------------------------------------------------------------
    # Read and treat data

    doe_df = pd.read_csv(f'DOE/database/{filename}.csv')

    doe_df = _filterDoe(doe_df)
    print("Df shape: ", doe_df.shape)

    filename_to_save = filename + f'_{doe_df.shape[0]}_por_{doe_df.shape[1]}'
    # ------------------------------------------------------------------------------------------------------------------
    # Plot the correlation matrix
    sns.set(style='white', font_scale=1.4)

    if plot_type == 0:

        # Simple plot
        fig = sns.pairplot(doe_df, corner=True)

    elif plot_type == 1:

        # Complete plot
        # based on: https://stackoverflow.com/questions/48139899/correlation-matrix-plot-with-coefficients-on-one-side-scatterplots-on-another
        fig = sns.PairGrid(doe_df, diag_sharey=False)
        fig.map_lower(sns.regplot, lowess=True, line_kws={'color': 'black'})
        fig.map_diag(sns.histplot)
        fig.map_upper(corrdot)

    # Plot window
    plt.tight_layout()
    plt.show()

    fig.savefig(f'DOE/images/{filename_to_save}.png')


def _filterDoe(doe_df):

    outputs_to_drop = ['deflection_cruise_aileron', 'deflection_cruise_rudder',
                       'deflection_cruise_flap',
                       'descentTime', 'timeClimb', 'neutral_point', 'cDRunAvl', 'alphaRun',
                       'timeTakeOff', 'fuelTakeOff',
                       'cd0', 'cd1', 'cd2', 'cDRun',
                       'cgPostionable', 'mtow']

    doe_df = doe_df.drop(columns=outputs_to_drop)

    # -----------------------------------------
    # numRows = doe_df.shape[0]
    # doe_df = doe_df[doe_df['cruiseRange'] < 1200]
    # print(f"Cutted {numRows - doe_df.shape[0]}, range < 200")
    # -----------------------------------------
    numRows = doe_df.shape[0]
    doe_df = doe_df[doe_df['cruiseRange'] > 0]
    print(f"Cutted {numRows - doe_df.shape[0]}, range > 0")
    # -----------------------------------------
    # numRows = doe_df.shape[0]
    # doe_df = doe_df[doe_df['deflection_cruise_elevator'] < 0]
    # print(f"Cutted {numRows - doe_df.shape[0]}, elevator < 0")
    # -----------------------------------------
    numRows = doe_df.shape[0]
    doe_df = doe_df[doe_df['runway'] < 3000]
    print(f"Cutted {numRows - doe_df.shape[0]}, runaway < 3000")

    # -----------------------------------------
    numRows = doe_df.shape[0]
    doe_df = doe_df[doe_df['alphaStallWing'] > 0]
    print(f"Cutted {numRows - doe_df.shape[0]}, alphaStallWing > 0")

    # -----------------------------------------
    numRows = doe_df.shape[0]
    doe_df = doe_df[doe_df['stallPositionWing'] > 0]
    print(f"Cutted {numRows - doe_df.shape[0]}, stallPositionWing > 0")

    # -----------------------------------------
    numRows = doe_df.shape[0]
    doe_df = doe_df[doe_df['staticMargin'] > 0]
    print(f"Cutted {numRows - doe_df.shape[0]}, staticMargin > 0")

    return doe_df


if __name__ == '__main__':
    plot_doe(filename='resultsAll')
    plot_doe(filename='resultsWing')
    plot_doe(filename='resultsStab')
    plot_doe(filename='resultsFuselage')
