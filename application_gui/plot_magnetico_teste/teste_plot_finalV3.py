import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv

#plot com streamplot

x=[]
x_tamanho, y_tamanho = 0, 0
flag_norm = True

with open('eixoX.csv', 'r') as file:
    reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
    for row in reader: # each row is a list
        y_tamanho = y_tamanho + 1
        for celula in row:
            x_tamanho = x_tamanho + 1
            if(flag_norm):
                celula = pow(10, celula/20)
            x.append(celula)
x_tamanho = int(x_tamanho/y_tamanho)

y=[]
with open('eixoY.csv', 'r') as file:
    reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
    for row in reader: # each row is a list
        for celula in row:
            if(flag_norm):
                celula = pow(10, celula/20)
            y.append(celula)  


X = []
for i in range(y_tamanho):
    for j in range(x_tamanho):
        X.append(j)

Y = []
for i in reversed(range(y_tamanho)):
    for j in range(x_tamanho):
        Y.append(i)

print(Y)
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
    if(flag_norm):
        aux =  float(20*np.log10(np.sqrt(pow(x[j],2)+pow(y[j],2))))
    if not(flag_norm):
        aux = -np.sqrt(pow(int(x[j]),2)+pow(y[j],2))
    norm.append(aux)

quiveropts = dict( headlength=0, pivot='middle', headwidth=1) # common options

plt.quiver(X,Y,x,y, norm, alpha=0.8, **quiveropts, cmap=plt.cm.inferno)
plt.colorbar()

plt.show()