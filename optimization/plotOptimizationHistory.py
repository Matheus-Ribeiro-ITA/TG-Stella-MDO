import pandas as pd
import  matplotlib.pyplot as plt


def plotOptimizationHistory():
    history_df = pd.read_csv("optimization/history/history.csv", index_col=0)

    scaleList = [10, 5, 1, 5, -1000]

    for i, scale in enumerate(scaleList):
        history_df[str(i)] = history_df[str(i)]*scale

    _plot_one(history_df, column=str(4))
    _plot_four(history_df, columns=['0', '1', '2', '3'])


def _plot_one(history_df, column=str(4)):
    plt.plot(history_df.index, history_df[column])
    plt.ylim([min(history_df[column])*0.95, max(history_df[column])*1.05])
    plt.xlabel("Iteration")
    plt.ylabel("Range (Km)")
    plt.show()


def _plot_four(history_df, columns=['0', '1', '2', '3']):
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].plot(history_df.index, history_df[columns[0]])
    # axs[0, 0].set_title('Wing AR')
    axs[0, 1].plot(history_df.index, history_df[columns[1]], 'tab:orange')
    # axs[0, 1].set_title('Wing Area')
    axs[1, 0].plot(history_df.index, history_df[columns[2]], 'tab:green')
    # axs[1, 0].set_title('Axis [1, 0]')
    axs[1, 1].plot(history_df.index, history_df[columns[3]], 'tab:red')
    # axs[1, 1].set_title('Axis [1, 1]')

    yLabels = ['Wing AR', 'Wing Area', 'Stab Area', 'Stab dist']

    for i, ax in enumerate(axs.flat):
        ax.set(xlabel='Iteration', ylabel=yLabels[i])

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for ax in axs.flat:
        ax.label_outer()

    plt.show()


if __name__ == '__main__':
    plotOptimizationHistory()
