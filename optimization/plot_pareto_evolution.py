import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_pareto_evolution_all(n_var=10, n_obj=2):
    folder_path = 'optimization/history/GA'
    filesnames = os.listdir(folder_path)
    generation_number = [int(filename.rsplit('_')[-1].split('.')[0]) for filename in filesnames]

    for i, filename in enumerate(filesnames):
        df = pd.read_csv(folder_path + '/' + filename, index_col=0)
        df = df[df[str(n_var)] != -1/1000]
        df = df[df[str(n_var+1)] != 1/1000]
        f1 = df[str(n_var)]
        f2 = df[str(n_var+1)]
        plt.scatter(f1*-1000, f2*1000, label=f'Geração {generation_number[i]+1}')
        plt.legend()
        plt.ylabel('Tamanho de pista (m)')
        plt.xlabel('Alcance (km)')
        plt.ylim([0, 900])
        plt.xlim([150, 720])
        plt.grid()
        plt.savefig(f"optimization/images/GA/{filename.split('.')[0]}.png")
        plt.show()


def plot_pareto_evolution_together(n_var=10, genereation_list=None, color_list=None):
    folder_path = 'optimization/history/GA'
    filesnames = os.listdir(folder_path)
    generation_number = [int(filename.rsplit('_')[-1].split('.')[0]) for filename in filesnames]

    color_count = 0
    for i, filename in enumerate(filesnames):
        if generation_number[i] in genereation_list:
            df = pd.read_csv(folder_path + '/' + filename, index_col=0)
            df = df[df[str(n_var)] != -1 / 1000]
            df = df[df[str(n_var + 1)] != 1 / 1000]
            f1 = df[str(n_var)]
            f2 = df[str(n_var + 1)]
            plt.scatter(f1 * -1000, f2 * 1000, label=f'Geração {generation_number[i] + 1}',
                        color=color_list[color_count])
            color_count += 1
    plt.legend()
    plt.ylabel('Tamanho de pista (m)')
    plt.xlabel('Alcance (km)')
    plt.ylim([0, 900])
    plt.xlim([150, 720])
    plt.grid()
    plt.savefig(f"optimization/images/GA/NSGA2_together.png")
    plt.show()


if __name__ == '__main__':
    # plot_pareto_evolution_all()

    plot_pareto_evolution_together(n_var=10, genereation_list=[0, 5, 15, 19], color_list=['deepskyblue',
                                                                                          'cornflowerblue',
                                                                                          'blue',
                                                                                          'darkblue'])
