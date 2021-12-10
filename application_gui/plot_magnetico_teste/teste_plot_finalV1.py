import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv
from tkinter import filedialog

#plot com streamplot

x=[]
x_tamanho, y_tamanho = 0, 0

with open('teste_mag_X_08-12-2021_20-38.csv', 'r') as file:
    reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
    for row in reader: # each row is a list
        y_tamanho = y_tamanho + 1
        for celula in row:
            x_tamanho = x_tamanho + 1
            x.append(celula)
x_tamanho = int(x_tamanho/y_tamanho)

y=[]
with open('teste_mag_Y_08-12-2021_20-38.csv', 'r') as file:
    reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
    for row in reader: # each row is a list
        for celula in row:
            y.append(celula)  
print(x)
print(y)

X = []
for i in range(y_tamanho):
    for j in range(x_tamanho):
        X.append(j)
print(X)
print(len(X))

Y = []
for i in range(y_tamanho):
    for j in range(x_tamanho):
        Y.append(i)
print(Y)
print(len(Y))

#plot streamline
try:
    plt.streamplot(X,Y,x,y, density = 1,color=x, cmap=plt.cm.inferno)
    plt.colorbar()
    plt.show()
except:
    pass

#plot com quiver
norm = []
for j in range(len(x)):
    norm.append(-np.sqrt(pow(int(x[j]),2)+pow(y[j],2)))
    
quiveropts = dict(color='white', headlength=0, pivot='middle', units='xy', headwidth=1) # common options

plt.quiver(X,Y,x,y, norm, alpha=0.8, **quiveropts, cmap=plt.cm.inferno)
plt.colorbar()

plt.show()
