import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from DOE.utils.aux_tools import corrdot


def plot_doe(plot_type=0, filename='results'):
    # ------------------------------------------------------------------------------------------------------------------
    # Read and treat data

    doe_df = pd.read_csv(f'DOE/database/{filename}.csv')

    doe_df = _filterDoe(doe_df, type=filename)
    print("Df shape: ", doe_df.shape)

    filename_to_save = filename + f'_{doe_df.shape[0]}_por_{doe_df.shape[1]}'
    # ------------------------------------------------------------------------------------------------------------------
    # Plot the correlation matrix
    sns.set(style='white', font_scale=1.4)

    if plot_type == 0:

        # Simple plot
        fig = sns.pairplot(doe_df, kind="reg", corner=True, plot_kws={'line_kws': {'color': 'red'}})
        for ax in fig.axes.flatten():
            if ax is not None:
                # rotate x axis labels
                ax.set_xlabel(ax.get_xlabel(), rotation=45)
                # rotate y axis labels
                ax.set_ylabel(ax.get_ylabel(), rotation=45)
                # set y labels alignment
                ax.yaxis.get_label().set_horizontalalignment('right')

        # for axes in fig.axes.flat:
        #     if axes is not None:
        #         axes.set_ylabel(axes.get_ylabel(), rotation=0, horizontalalignment='right')

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


def _filterDoe(doe_df, type='resultsAll'):

    default_to_drop = ['deflection_cruise_aileron', 'deflection_cruise_rudder',
                           'deflection_cruise_flap',
                           'descentTime', 'timeClimb', 'neutral_point', 'cDRunAvl', 'alphaRun',
                           'timeTakeOff', 'fuelTakeOff',
                           'cd0', 'cd1', 'cd2', 'cDRun',
                           'cgPostionable', 'mtow', 'static_margin',
                           'fuelDescent', 'fuelClimb', 'cruiseRange',
                       'allElseCgPercentFuselage', 'speedTakeOff',
                       'deflection_cruise_elevator', 'fuelTotal']

    if type == 'resultsAll':
        outputs_to_drop = default_to_drop
    elif type == 'resultsWing':
        outputs_to_drop = default_to_drop + ['aspectRatioV', 'areaV', 'taperV', 'posXV', 'fuselageLength']
    elif type == 'resultsStab':
        outputs_to_drop = default_to_drop + ['aspectRatio', 'wingSecPercentage', 'wingArea', 'taperRatio1',
                                             'taperRatio2', 'fuselageLength']
    elif type == 'resultsFuselage':
        outputs_to_drop = default_to_drop + ['aspectRatio', 'wingSecPercentage', 'wingArea', 'taperRatio1',
                                             'taperRatio2', 'aspectRatioV', 'areaV', 'taperV', 'posXV']


    doe_df = doe_df.drop(columns=outputs_to_drop)

    renameColumns = {
        'aspectRatio': 'Alongamento',
        'wingSecPercentage': 'Divisão painel',
        'wingArea': 'Área Asa ($m^2$)',
        'taperRatio1': 'Afilamento primeira seção',
        'taperRatio2': 'Afilamento segunda seção',
        'aspectRatioV': 'Alongamento empenagem',
        'areaV': 'Área Empenagem ($m^2$)',
        'taperV': 'Afilamento empenagem',
        'posXV': 'Distância empenagem (m)',
        'fuselageLength': 'Comprimento fuselagem (m)',
        'deflection_cruise_elevator': 'Deflexão profundor (º)',
        'alphaStallWing': 'Ângulo de estol (º)',
        'stallPositionWing': 'Posição de estol da asa (%)',
        'weightEmpty': 'Peso vazio (kg)',
        'fuelTotal': 'Peso combustível (kg)',
        'runway': 'Pista de decolagem (m)',
        'speedTakeOff': 'Velocidade decolagem (m/s)',
        'range_all': 'Alcance (km)',
    }

    # -----------------------------------------
    # numRows = doe_df.shape[0]
    # doe_df = doe_df[doe_df['cruiseRange'] < 1200]
    # print(f"Cutted {numRows - doe_df.shape[0]}, range < 200")
    # -----------------------------------------
    numRows = doe_df.shape[0]
    doe_df = doe_df[doe_df['range_all'] > 0]
    print(f"Cutted {numRows - doe_df.shape[0]}, range > 0")

    # -----------------------------------------
    numRows = doe_df.shape[0]
    doe_df = doe_df[doe_df['range_all'] < 650]
    print(f"Cutted {numRows - doe_df.shape[0]}, range < 650")
    # -----------------------------------------
    # numRows = doe_df.shape[0]
    # doe_df = doe_df[doe_df['deflection_cruise_elevator'] < 0]
    # print(f"Cutted {numRows - doe_df.shape[0]}, elevator < 0")
    # -----------------------------------------
    numRows = doe_df.shape[0]
    doe_df = doe_df[doe_df['runway'] < 1200]
    print(f"Cutted {numRows - doe_df.shape[0]}, runaway < 1200")

    # -----------------------------------------
    numRows = doe_df.shape[0]
    doe_df = doe_df[doe_df['alphaStallWing'] > 0]
    print(f"Cutted {numRows - doe_df.shape[0]}, alphaStallWing > 0")

    # -----------------------------------------
    numRows = doe_df.shape[0]
    doe_df = doe_df[doe_df['stallPositionWing'] > 0]
    print(f"Cutted {numRows - doe_df.shape[0]}, stallPositionWing > 0")

    # -----------------------------------------
    # numRows = doe_df.shape[0]
    # doe_df = doe_df[doe_df['staticMargin'] > 0]
    # print(f"Cutted {numRows - doe_df.shape[0]}, staticMargin > 0")

    doe_df = doe_df.rename(columns=renameColumns)  # TODO:

    return doe_df


if __name__ == '__main__':
    plot_doe(filename='resultsAll')
    plot_doe(filename='resultsWing')
    plot_doe(filename='resultsStab')
    plot_doe(filename='resultsFuselage')