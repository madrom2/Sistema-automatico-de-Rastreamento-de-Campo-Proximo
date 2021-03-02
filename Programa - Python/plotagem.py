import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

class plot_2d:
    #------------------------------------------------------------       
    def anotação_label(tamanho, passo):
        anotacao=[]
        for i in range (tamanho):
            anotacao.append('%.2fmm' % float(i*passo))
            
        return anotacao
    
    #------------------------------------------------------------
    def mapa_de_calor_cleisson(data, vmax, vmin, step_x, step_y, titulo, flag_save):
        #Gera figura de plotagem 
        fig = plt.figure()
        #plt.figure(figsize=(3,10))
        ax = fig.add_axes([0.1,0.1,1.5,1.5])

        #Gera mapa de calor
        im = ax.imshow(data, interpolation='gaussian', cmap='inferno', vmax=vmax, vmin=vmin)

        #Cria anotação do grid
        anotacao_y = []
        for i in range (len(data)):
            anotacao_y.append('%.2fmm' % float(i*step_y))
            
        anotacao_x=[]
        for i in range (len(data[0])):
            anotacao_x.append('%.2fmm' % float(i*step_x))
            
        #Configuração de apresentação das anotações
        ax.set_xticks(np.arange(len(anotacao_x)))
        ax.set_yticks(np.arange(len(anotacao_y)))
        ax.set_xticklabels(anotacao_x)
        ax.set_yticklabels(anotacao_y)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")

        #Titulo do mapa de calor
        ax.set_title('cleisson - '+titulo)

        #Adiciona barra de cor
        plt.colorbar(im)

        #tamanho do grafico
        """plt.xlim(right=len(data[0])-1)
        plt.xlim(left=0)
        plt.ylim(top=0)
        plt.ylim(bottom=len(data)-1)"""
        plt.grid(color='w', which='major', alpha=0.5)
        
        if (flag_save):
            #Salva imagem
            plt.savefig(titulo+'_img_1.png',bbox_inches="tight")
        else:   
            #Plot imagem
            plt.show()
            
    #------------------------------------------------------------
    def mapa_de_calor_andre(data, vmax, vmin, step_x, step_y, titulo, flag_save):
        #Tamanho da figura - FUTURO ADICIONAR REDIMENSIONAMENTO
        #plt.figure(figsize=(8,10))
        
        #Cria anotação do grid
        anotacao_y = []
        for i in range (len(data)):
            anotacao_y.append('%.2fmm' % float(i*step_y))
            
        anotacao_x=[]
        for i in range (len(data[0])):
            anotacao_x.append('%.2fmm' % float(i*step_x))
        
        #Definição da barra de cor
        cmap = LinearSegmentedColormap.from_list('inferno', ['#000000', '#510E6C', '#BA3655',
                                                     '#F78212', '#F6FA96'])
        
        #Gera mapa de calor
        ax = sns.heatmap(data, cmap=cmap, vmin=vmin, vmax=vmax,
                 cbar_kws={'label': 'dBuI'})
        
        #Titulo do mapa de calor
        ax.set_title('andre - '+titulo)
        
        #Fixa anotação nos eixos
        ax.set_xticklabels(anotacao_x)
        ax.set_yticklabels(anotacao_y)
        
        #Rotaciona anotação do eixo
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")
        plt.setp(ax.get_yticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")

        #Ativa grade
        plt.grid(color='w', which='major', alpha=0.35)
        
        if (flag_save):
            #Salva imagem
            plt.savefig(titulo+'_img_2.png',bbox_inches="tight")
        else:   
            #Plot imagem
            plt.show()
        
    #------------------------------------------------------------     
    