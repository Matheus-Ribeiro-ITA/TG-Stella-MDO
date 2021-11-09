import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def plotOptimizationHistory(filename='history', scaleList=None, folder_name=None):
    if folder_name is not None:
        history_df = pd.read_csv(f"optimization/history/{folder_name}/{filename}.csv", index_col=0)
    else:
        history_df = pd.read_csv(f"optimization/history/{filename}.csv", index_col=0)

    for i, scale in enumerate(scaleList):
        history_df[str(i)] = history_df[str(i)]*scale

    _plot_one(history_df, column=-1, filename=filename)
    _plot_four(history_df, columns=['0', '2', '6', '8'], filename=filename)
    _plot_together(column=-1, folder_name=folder_name, scaleList=scaleList, filename=filename)


def _plot_one(history_df, column=-1, filename=None):
    values = history_df.iloc[:, column]
    plt.plot(history_df.index, values)
    plt.ylim([min(values)*0.95, max(values)*1.05])
    plt.xlabel("Iteration")
    plt.ylabel("Range (Km)")
    plt.savefig(f"optimization/images/outputHistory_{filename}.png")
    plt.show()



def _plot_four(history_df, columns=None, filename=None):
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].plot(history_df.index, history_df[columns[0]])
    # axs[0, 0].set_title('Wing AR')
    axs[0, 1].plot(history_df.index, history_df[columns[1]], 'tab:orange')
    # axs[0, 1].set_title('Wing Area')
    axs[1, 0].plot(history_df.index, history_df[columns[2]], 'tab:green')
    # axs[1, 0].set_title('Axis [1, 0]')
    axs[1, 1].plot(history_df.index, history_df[columns[3]], 'tab:red')
    # axs[1, 1].set_title('Axis [1, 1]')

    yLabels = ['Alongamento', 'Área da asa ($m^2$)', 'Área Empenagem ($m^2$)', 'Distância da empenagem (m)']

    for i, ax in enumerate(axs.flat):
        ax.set(xlabel='Iterações', ylabel=yLabels[i])
        ax.grid()


    # # Hide x labels and tick labels for top plots and y ticks for right plots.
    # for ax in axs.flat:
    #     ax.label_outer()

    plt.tight_layout()  # Or equivalently,  "plt.tight_layout()"
    plt.savefig(f"optimization/images/statesHistory_{filename}.png")
    plt.show()


def _plot_together(column=-1, folder_name=None, scaleList=None, filename=None):

    if 'alcance' in filename:
        history_df_slsqp = pd.read_csv(f"optimization/history/{folder_name}/history_10_SLSQP_alcance.csv", index_col=0)
        history_df_diff_evo = pd.read_csv(f"optimization/history/{folder_name}/history_10_diff_evo_alcance.csv", index_col=0)
    elif 'pista' in filename:
        history_df_slsqp = pd.read_csv(f"optimization/history/{folder_name}/history_10_SLSQP_pista.csv", index_col=0)
        history_df_diff_evo = pd.read_csv(f"optimization/history/{folder_name}/history_10_diff_evo_pista.csv", index_col=0)

    for i in range(len(history_df_slsqp.index)):
        if history_df_slsqp.loc[i, '10'] == -0.0010:
            history_df_slsqp.loc[i, '10'] = (history_df_slsqp.loc[i+1, '10'] + history_df_slsqp.loc[i-1, '10'])/2
    # history_df_slsqp.loc[history_df_slsqp['10'] == -0.0010, '10'] = None

    for i, scale in enumerate(scaleList):
        history_df_slsqp[str(i)] = history_df_slsqp[str(i)]*scale
        history_df_diff_evo[str(i)] = history_df_diff_evo[str(i)] * scale


    values_01 = history_df_slsqp.iloc[:, column]
    values_02 = history_df_diff_evo.iloc[:, column]

    max_index = max((max(history_df_diff_evo.index), max(history_df_slsqp.index)))
    if 'alcance' in filename:
        max_value = max((max(values_01), max(values_02)))
    elif 'pista' in filename:
        max_value = min((min(values_01), min(values_02)))

    plt.plot(history_df_slsqp.index, values_01, '--.', label='SLSQP')
    plt.plot(history_df_diff_evo.index, values_02, '--+', label='Differential Evolution')
    plt.plot([0, max_index], [max_value, max_value], '--', label='Maior Valor', color='red')
    plt.ylim([min((min(values_01), min(values_02)))*0.95, max((max(values_01), max(values_02)))*1.05])
    plt.xlabel("Iterações")

    if 'alcance' in filename:
        plt.ylabel("Alcance (Km)")
    elif 'pista' in filename:
        plt.ylabel("Tamanho de pista (m)")

    plt.legend()
    plt.grid()
    plt.savefig(f"optimization/images/outputHistory_together_alcance.png")
    plt.show()


if __name__ == '__main__':
    vars_num = '10'
    method = 'SLSQP_alcance'  # 'SLSQP_alcance', 'SLSQP_pista', 'diff_evo_alcance', 'diff_evo_pista'
    folder_name = 'rodada_final'
    scaleFactors = np.array([10, 1, 5, 1, 1,
                             5, 1, 1, 5, 5,
                             -1000])
    plotOptimizationHistory(filename=f'historyFun_{vars_num}_{method}', scaleList=scaleFactors, folder_name=folder_name)
    plotOptimizationHistory(filename=f'history_{vars_num}_{method}', scaleList=scaleFactors, folder_name=folder_name)
