import numpy as np
import matplotlib.pyplot as plt
import matplotlib

#plot com streamplot
x = np.arange(0,2.2,0.1)
y = np.arange(0,2.2,0.1)

X, Y = np.meshgrid(x, y)
u = np.cos(X)*Y
v = np.sin(y)*Y

norm = np.sqrt(u*u + v*v)

plt.streamplot(X,Y,u,v, density = 1,color=u, cmap=plt.cm.inferno)

ax = plt.gca()

for art in ax.get_children():
    if not isinstance(art, matplotlib.patches.FancyArrowPatch):
        continue
    art.remove()        # Method 1
    # art.set_alpha(0)  # Method 2

plt.colorbar()
plt.show()


#plot com quiver
n = -2
color_array = np.sqrt(((v-n)/2)**2 + ((u-n)/2)**2)

quiveropts = dict(color='white', headlength=0, pivot='middle', units='xy', headwidth=1) # common options

plt.quiver(X,Y,u,v, color_array, alpha=0.8, **quiveropts, cmap=plt.cm.inferno)
plt.colorbar()

plt.show()