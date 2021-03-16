'''
Script para automatizacao do Xfoil
'''

import codecs
import json
import os

import numpy as np

# Genese 32 [Done]
# Genese 34 [Done]
# GOE 398 [Done]
# LS 417 mod [Done]
# Eppler 1230 [Done]
# NACA 4415 [Done]
# AH 93-W-145 [Done]
# AH 94-145  [Done]
# AH 95-160 [Done]
# Genese 36 [Done]
# Eppler 657 [Done]
# GOE 527 [Done]
# GOE 449 [Done]
# N-24 [Done]
# Clark Y [Done]
# GOE 693 [Done]
# N-22 [Done]
# LA 5055
# LA203A [Done]
# GOE 498 [Done]
# FX 76 MP-160 [Done]
# GOE 624 [Done]

# 's1210' [Problematic]

# configs
airfoilList = ['ah95156', 'ah94w145', 'ah94145', 'naca4415',
               'e1230', 'ls417mod',  'goe398', 'rhodesg34',
               'rhodesg32', 'n22', 'goe693', 'clarky', 'n24', 'goe449',
               'goe527', 'e657', 'rhodesg36', 'fx76mp160',
               'goe498', 'la203a', 'la5055',
               'ls417', 'naca23018', 'e548', 'e420', 'ls421mod', 'naca0012']
flapOn = True

# -------------------------------------------------------------------------------
npans = 200
Mach = 0.03

takeOffSpeed = 14
cruiseSpeed = 28

meanChord = 0.5
mu = 1.42*10**-5
ReList = [takeOffSpeed*meanChord/mu, cruiseSpeed*meanChord/mu]

a_min = -5.0
a_max = 18.0
a_step = 0.5

if flapOn:
    flap_angle = 20.0  # angulo do flap (positivo eh p baixo)
else:
    flap_angle = 0.0  # angulo do flap (positivo eh p baixo)

x_fl = 0.7  # posicao como perc. da corda
t_fl = 0.5  # posicao como perc. da espessura

dirPath = os.getcwd()
if flapOn:
    folderPath = f"{dirPath}\\xfoilDataFlap"
    ReList.pop()
    numTimes = 1
else:
    folderPath = f"{dirPath}\\xfoilData"
    numTimes = 2

savedAirfoils = [filename.split('_')[0] for filename in os.listdir(folderPath)]

airfoilToSave = [airfoil for airfoil in airfoilList if not savedAirfoils.count(airfoil) == numTimes]
print(airfoilToSave)
if not airfoilToSave: print("All airfoils from list are saved")

for Re in ReList:
    for airfoil in airfoilToSave:
        # comandos
        coms = []

        coms.append(['load'])
        coms.append([airfoil + '.dat'])

        # flap
        coms.append(['gdes'])
        coms.append(['flap'])
        coms.append([str(x_fl)])
        coms.append(['999'])  # especifica selecao como perc. da corda
        coms.append([str(t_fl)])
        coms.append([str(flap_angle)])

        coms.append([' '])
        coms.append(['pcop'])

        # discretizacao

        coms.append(['ppar'])
        coms.append(['n'])
        coms.append([str(npans)])
        coms.append([' ']);
        coms.append([' '])

        # operacao
        coms.append(['oper'])

        coms.append(['visc'])
        coms.append([str(Re)])

        coms.append(['Mach'])
        coms.append([str(Mach)])

        # parametros de camada limite (transicoes forcadas)
        coms.append(['vpar'])

        xtr_top = 0.1  # transicao no extradorso (pode acontecer no
        # max nessa posicao)
        xtr_bot = 0.1  # transicao no intradorso (idem)

        coms.append(['xtr'])

        coms.append([str(xtr_top)])
        coms.append([str(xtr_bot)])

        coms.append([' '])

        # it. maximas
        maxiter = 800
        coms.append(['iter'])
        coms.append([str(maxiter)])

        # arquivo
        coms.append(['pacc'])

        filename = '%s_%.0f.dat' % (airfoil, round(Re/1000, 0))
        if os.path.exists(filename):
            # remove previous results
            os.remove(filename)

        coms.append([filename])
        coms.append([' '])

        # angulos de ataque
        coms.append(['aseq'])

        coms.append([str(a_min)])
        coms.append([str(a_max)])
        coms.append([str(a_step)])

        # agora sair
        coms.append([' '])
        coms.append(['quit'])

        # agora criar script
        myscript = open('temp_script.txt', 'w')

        for line in coms:
            myscript.write(' '.join(line) + '\n')

        myscript.close()

        errcode = os.system('xfoil.exe < %s' % ('temp_script.txt',))

        print('Xfoil closed with exit code', errcode)

        # read and plot
        try:
            data = np.loadtxt(filename, skiprows=12)
            alphas = data[:, 0]
            CLs = data[:, 1]
            CDs = data[:, 2]
            Cms = data[:, 4]

            dataJson = {
                "alphas": alphas.tolist(),
                "CLs": CLs.tolist(),
                "CDs": CDs.tolist(),
                "Cms": Cms.tolist(),
                "airfoil": airfoil,
                "Re": round(Re, 0)
            }
            dirPath = os.getcwd()
            filePath = f"{folderPath}\\{filename}"
            json.dump(dataJson, codecs.open(filePath, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True,
                      indent=4)

            os.remove(filename)
        except OSError:
            print(filename)
            pass



