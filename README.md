# TG-Stella-MDO
Welcome to the Multi Disciplinary Optimization (MDO) software built for Stella Aviation as an ITA undergraduate final theses.

# Overview

Inside this program there is:
- Integration of Xfoil with Python, on subfolder: MDO/airfoils.
- Integration of AVL (Athena Vortex Lattice by Drela MIT) with Python, on subfolder: MDO/avl and avl. Forked from https://github.com/jbussemaker/AVLWrapper
- Takeoff calculation with integral of forces, on subfolder: MDO/performance/takeOff.py
- Cruise, climb and descent equations.
- Mass estimation.
- Stall estimation with Critical section method.
- Otimization with deterministic and stochastic algorithms.


# Getting started

1) Install requirements

```pip install -r requirements.txt```

2) Change outputs config on outputsConfig.cfg
3) Run main.py

# Tutorial in portuguese

https://youtu.be/YhGX458KBaI


## We Love Standards
#### Variables Units
[S.I units](https://en.wikipedia.org/wiki/International_System_of_Unitsuote
    ) are always used unless explicit on the variable name. Ex: aoaDeg.
#### Naming Convention
 - <b>Variables, Functions:</b>  lowerCamelCase. Ex: numberOfSecs
 - <b>Classes (instances):</b> UpperCamelCase. Ex: Aircraft()
 - <b>Dict Keys:</b> camel_Snake_Case. Ex: chord_Wing_Root
## Dependencies
 - Python 3.7+
 - AvlWrapper
 
## Contributing, Versioning, and Other Details
We loosely use [semantic versioning](https://semver.org/). 
Please be aware that this version is still under construction and has not been released yet, 
for this reason theres is no versioning yet.

If you can helps the program in any way feel free to contact us.

## Authors

Matheus Ribeiro Sampaio  <br>
matheus.ribeiro.aer@gmail.com

Prof. Dr. Ney Secco
