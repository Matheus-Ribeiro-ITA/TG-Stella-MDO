import os
import numpy as np
import matplotlib.pyplot as plt
# configs

airfoil='n0012'

# comandos
coms=[]

coms.append(['load'])
coms.append([airfoil+'.dat'])

# flap
flap_angle=0.0 # angulo do flap (positivo eh p baixo)
x_fl=0.8 # posicao como perc. da corda
t_fl=0.5 # posicao como perc. da espessura

coms.append(['gdes'])
coms.append(['flap'])
coms.append([str(x_fl)])
coms.append(['999']) # especifica selecao como perc. da corda
coms.append([str(t_fl)])
coms.append([str(flap_angle)])

coms.append([' '])
coms.append(['pcop'])

# discretizacao
npans=200

coms.append(['ppar'])
coms.append(['n'])
coms.append([str(npans)])
coms.append([' ']); coms.append([' '])

# operacao
coms.append(['oper'])

Re=170000
coms.append(['visc'])
coms.append([str(Re)])

Mach=0.03
coms.append(['Mach'])
coms.append([str(Mach)])

# parametros de camada limite (transicoes forcadas)
coms.append(['vpar'])

xtr_top=0.1 # transicao no extradorso (pode acontecer no
# max nessa posicao)
xtr_bot=0.1 # transicao no intradorso (idem)

coms.append(['xtr'])

coms.append([str(xtr_top)])
coms.append([str(xtr_bot)])

coms.append([' '])

# it. maximas
maxiter=3000
coms.append(['iter'])
coms.append([str(maxiter)])

# arquivo
coms.append(['pacc'])

filename='%s_%6f.dat' % (airfoil, Re)
if os.path.exists(filename):
    # remove previous results
    os.remove(filename)

coms.append([filename])
coms.append([' '])

# angulos de ataque
coms.append(['aseq'])

a_min=-5.0
a_max=17.0
a_step=0.5

coms.append([str(a_min)])
coms.append([str(a_max)])
coms.append([str(a_step)])

# agora sair
coms.append([' '])
coms.append(['quit'])

# agora criar script
myscript=open('temp_script.txt', 'w')

for line in coms:
    myscript.write(' '.join(line)+'\n')

myscript.close()

errcode=os.system('xfoil.exe < %s' % ('temp_script.txt',))

print('Xfoil closed with exit code', errcode)

# read and plot
data=np.loadtxt(filename, skiprows=12)

alphas=data[:, 0]
CLs=data[:, 1]
CDs=data[:, 2]
Cms=data[:, 4]

#CLs
plt.plot(alphas, CLs, marker='o')

plt.grid()
plt.xlabel(r'$\alpha [^\circ]$')
plt.ylabel(r'$C_l$')
plt.title(r'$Re = %g, x_{tr,top} = %g, x_{tr,bot} = %g$' % (Re, xtr_top, xtr_bot))

plt.show()

#Cms
plt.plot(alphas, Cms, marker='o')

plt.grid()
plt.xlabel(r'$\alpha [^\circ]$')
plt.ylabel(r'$C_m$')
plt.title(r'$Re = %g, x_{tr,top} = %g, x_{tr,bot} = %g$' % (Re, xtr_top, xtr_bot))

plt.show()

#polar
plt.plot(CLs, CDs, marker='o')

plt.grid()
plt.xlabel(r'$C_l$')
plt.ylabel(r'$C_d$')
plt.title(r'$Re = %g, x_{tr,top} = %g, x_{tr,bot} = %g$' % (Re, xtr_top, xtr_bot))

plt.show()
