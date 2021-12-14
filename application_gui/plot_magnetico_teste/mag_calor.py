import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv

#plot com streamplot

x= [[-80 for _ in range(13)] for _ in range(13)]
contx,conty = 0,0
with open('eixoX.csv', 'r') as file:
    reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
    for row in reader: # each row is a list
        for celula in row:
            celula = pow(10, celula/20)
            x[contx][conty]=celula
            conty = conty +1
        conty = 0
        contx= contx+1
contx,conty = 0,0
y = [[-80 for _ in range(13)] for _ in range(13)]
with open('eixoY.csv', 'r') as file:
    reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
    for row in reader: # each row is a list
        for celula in row:
            celula = pow(10, celula/20)
            y[contx][conty]=(celula) 
            conty = conty +1
        conty = 0
        contx= contx+1
#plot com quiver
norm = [[-80 for _ in range(13)] for _ in range(13)]
for i in range(len(x)):
    for j in range(len(x)):
        aux = (np.sqrt(pow(x[i][j],2)+pow(y[i][j],2)))
        norm[i][j] =  20*np.log10(aux)

file = open('normalizada.csv', 'w', newline ='')
with file:
    write = csv.writer(file, delimiter=';') 
    write.writerows(norm) 
print('FIM')
