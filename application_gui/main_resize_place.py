#Biblioteca de interface
from tkinter import *
from tkinter.ttk import * # Frame, Label, Entry, Button
from tkinter import scrolledtext
from tkinter import filedialog

#Biblioteca do mapa de calor
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import serial.tools.list_ports   #Bibliote de conecção serial
import time                      #Biblioteca para delay
import csv                       #Biblioteca salvar dados em arquivo csv
import numpy as np               #Biblioteca de array FUTURO RETIRAR
from datetime import datetime    #Biblioteca do tempo da maquina

class main_window(Frame):
    dict_jog = {'up': '$J=G91 Y+% F200',\
                'down': '$J=G91 Y-% F200',\
                'left': '$J=G91 X-% F200',\
                'right': '$J=G91 X+% F200',
                'z_up': '$J=G91 Z+% F200',
                'z_down': '$J=G91 Z-% F200'}
    
    rows, cols = 13, 13  # tamanho da tabela
    rows_disp = 10.35  # numero de linhas apresentado
    cols_disp = 7.75 # numero de colunas apresentado
    var_step_x, var_step_y = 1, 1 # passo de cada eixo
    flag_medindo, flag_stop ,flag_resize= False, False, False
    flag_grade, flag_anotacao, flag_auto_maxmin= True, True, True
    tempo_entre_medidas=1 #em segundos
    
    s_w, s_h =1, 1
    n_w, n_h = 1080, 720
    last_callback_time = time.time()
    
    def __init__(self):
        super().__init__()

        self.initUI()
        
        self.serial_cnc = None
    
    def initUI(self):
        self.s_w= self.winfo_screenwidth()/self.n_w
        self.s_h= self.winfo_screenheight()/self.n_h
        
        print(self.winfo_screenwidth(),self.winfo_screenheight())
        
        self.def_font = font.nametofont("TkDefaultFont")
        self.def_font.config(size=int(9 * (self.s_h+self.s_w)/2))
        
        self.master.bind("<Configure>", self.resize)
        
        #---nome da janela---------------------
        self.master.title('Controle Auto Scan')
        self.pack(fill=BOTH, expand=True)
        
        notebook = Notebook(self)
        notebook.pack(fill=BOTH, expand=True)
        
        self.frm_notebook1 = Frame(notebook)
        self.frm_notebook1.pack(fill=BOTH, expand=True)
                
        notebook.add(self.frm_notebook1, text='      Controle & Medição      ')
        
        #-----------------------------configuração do frame-----------------------------
        #---nome do frame---------------------
        self.frm_01 = Labelframe(self.frm_notebook1, text='Serial')
        self.frm_01.place(x=int(10*self.s_w),y=int(1*self.s_h),width=int(440*self.s_w),height=int(80*self.s_h))
                
        #---configuração linha analisador-----
        self.lbl_01 = Label(self.frm_01, text='Analisador:')
        self.lbl_01.place(x=int(5*self.s_w),y=int(3*self.s_h),width=int(90*self.s_w),height=int(20*self.s_h))
        
        self.cmb_analyzer = Combobox(self.frm_01)
        self.cmb_analyzer.place(x=int(73*self.s_w),y=int(2*self.s_h),width=int(185*self.s_w),height=int(23*self.s_h))
        
        self.btn_open_analyzer = Button(self.frm_01, text='Abrir')
        self.btn_open_analyzer.place(x=int(267*self.s_w),y=int(1*self.s_h),width=int(80*self.s_w),height=int(25*self.s_h))
        
        #---Atualização de ports-----------
        self.btn_refresh = Button(self.frm_01, text='Atualizar')
        self.btn_refresh.place(x=int(353*self.s_w),y=int(1*self.s_h),width=int(75*self.s_w),height=int(53*self.s_h))
        
        #---configuração linha CNC---------      
        self.lbl_02 = Label(self.frm_01, text='CNC:')
        self.lbl_02.place(x=int(5*self.s_w),y=int(30*self.s_h),width=int(90*self.s_w),height=int(20*self.s_h))

        self.cmb_cnc = Combobox(self.frm_01, width=27)
        self.cmb_cnc.place(x=int(73*self.s_w),y=int(29*self.s_h),width=int(185*self.s_w),height=int(23*self.s_h))
        
        self.btn_open_cnc = Button(self.frm_01, text='Abrir')
        self.btn_open_cnc.place(x=int(267*self.s_w),y=int(28*self.s_h),width=int(80*self.s_w),height=int(25*self.s_h))
        
        #---nome do frame---------------------
        self.frm_ctrls = Labelframe(self.frm_notebook1, text='Controle')
        self.frm_ctrls.place(x=int(10*self.s_w),y=int(83*self.s_h),width=int(440*self.s_w),height=int(340*self.s_h))
        #---configuração da linha/coluna------
        
        #---escrita XYZ---------------------
        self.lbl_03 = Label(self.frm_ctrls, text='Y:')
        self.lbl_03.place(x=int(138*self.s_w),y=int(1*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        self.lbl_04 = Label(self.frm_ctrls, text='X:')
        self.lbl_04.place(x=int(10*self.s_w),y=int(50*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        self.lbl_05 = Label(self.frm_ctrls, text='Z:')
        self.lbl_05.place(x=int(295*self.s_w),y=int(1*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        #---botão de home------------------
        self.btn_home = btn_up = Button(self.frm_ctrls, text= 'Origem')
        self.btn_home.place(x=int(344*self.s_w),y=int(25*self.s_h),width=int(70*self.s_w),height=int(88*self.s_h))
        
        #---configuração linhas------------   
        # Primeira linha
        self.btn_dig_no = Button(self.frm_ctrls, text=u'\u25F8')
        self.btn_dig_no.place(x=int(27*self.s_w),y=int(25*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        self.btn_up = Button(self.frm_ctrls, text= u'\u25B2')
        self.btn_up.place(x=int(106*self.s_w),y=int(25*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        self.btn_dig_ne = Button(self.frm_ctrls, text=u'\u25F9')
        self.btn_dig_ne.place(x=int(186*self.s_w),y=int(25*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        self.btn_z_up_btn = Button(self.frm_ctrls, text= u'\u25B2')
        self.btn_z_up_btn.place(x=int(264*self.s_w),y=int(25*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        # Segunda linha
        self.btn_left_btn = Button(self.frm_ctrls, text=u'\u25C0')
        self.btn_left_btn.place(x=int(27*self.s_w),y=int(56*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        self.btn_home_btn = Button(self.frm_ctrls, text=u'\u25EF')
        self.btn_home_btn.place(x=int(106*self.s_w),y=int(56*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        self.btn_right_btn = Button(self.frm_ctrls, text=u'\u25B6')
        self.btn_right_btn.place(x=int(186*self.s_w),y=int(56*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        # Terceira linha       
        self.btn_diag_so = Button(self.frm_ctrls, text=u'\u25FA')
        self.btn_diag_so.place(x=int(27*self.s_w),y=int(87*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        self.btn_down = Button(self.frm_ctrls, text=u'\u25BC')
        self.btn_down.place(x=int(106*self.s_w),y=int(87*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        
        self.btn_diag_se = Button(self.frm_ctrls, text=u'\u25FF')
        self.btn_diag_se.place(x=int(185*self.s_w),y=int(87*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
                
        self.btn_z_down = Button(self.frm_ctrls, text=u'\u25BC')
        self.btn_z_down.place(x=int(264*self.s_w),y=int(87*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))

        self.cmb_step = Combobox(self.frm_ctrls, width=5)# Janela de seleção do tamanho de passo
        self.cmb_step.place(x=int(264*self.s_w),y=int(56*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
        self.cmb_step['values'] = ['2','1','0.5','0.1']
        self.cmb_step.current(1)
        
        self.flag_resize = True
        #self.resize()
        self.all_children()
        
    def resize(self, event):
        cur_time = time.time()
        if ((cur_time - self.last_callback_time) > 0.10) and (self.flag_resize):
            print(event.width,event.height)
            self.s_w= event.width/self.n_w
            self.s_h= event.height/self.n_h
            
            self.def_font.config(size=int(9 * (self.s_h+self.s_w)/2))
            
            self.frm_01.place(x=int(10*self.s_w),y=int(1*self.s_h),width=int(440*self.s_w),height=int(80*self.s_h))
            self.lbl_01.place(x=int(5*self.s_w),y=int(3*self.s_h),width=int(90*self.s_w),height=int(20*self.s_h))
            self.cmb_analyzer.place(x=int(73*self.s_w),y=int(2*self.s_h),width=int(185*self.s_w),height=int(23*self.s_h))
            self.btn_open_analyzer.place(x=int(267*self.s_w),y=int(1*self.s_h),width=int(80*self.s_w),height=int(25*self.s_h))
            self.btn_refresh.place(x=int(353*self.s_w),y=int(1*self.s_h),width=int(75*self.s_w),height=int(53*self.s_h))
            self.lbl_02.place(x=int(5*self.s_w),y=int(30*self.s_h),width=int(90*self.s_w),height=int(20*self.s_h))
            self.cmb_cnc.place(x=int(73*self.s_w),y=int(29*self.s_h),width=int(185*self.s_w),height=int(23*self.s_h))
            self.btn_open_cnc.place(x=int(267*self.s_w),y=int(28*self.s_h),width=int(80*self.s_w),height=int(25*self.s_h))
            self.frm_ctrls.place(x=int(10*self.s_w),y=int(345*self.s_h),width=int(440*self.s_w),height=int(340*self.s_h))
            self.frm_ctrls.place(x=int(10*self.s_w),y=int(83*self.s_h),width=int(440*self.s_w),height=int(340*self.s_h))
            self.lbl_03.place(x=int(138*self.s_w),y=int(1*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.lbl_04.place(x=int(10*self.s_w),y=int(50*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.lbl_05.place(x=int(295*self.s_w),y=int(1*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            
            self.btn_home.place(x=int(344*self.s_w),y=int(25*self.s_h),width=int(70*self.s_w),height=int(88*self.s_h))
            self.btn_dig_no.place(x=int(27*self.s_w),y=int(25*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.btn_up.place(x=int(106*self.s_w),y=int(25*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.btn_dig_ne.place(x=int(186*self.s_w),y=int(25*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.btn_z_up_btn.place(x=int(264*self.s_w),y=int(25*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.btn_left_btn.place(x=int(27*self.s_w),y=int(56*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.btn_home_btn.place(x=int(106*self.s_w),y=int(56*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.btn_right_btn.place(x=int(186*self.s_w),y=int(56*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.btn_diag_so.place(x=int(27*self.s_w),y=int(87*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.btn_down.place(x=int(106*self.s_w),y=int(87*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.btn_diag_se.place(x=int(185*self.s_w),y=int(87*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.btn_z_down.place(x=int(264*self.s_w),y=int(87*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            self.cmb_step.place(x=int(264*self.s_w),y=int(56*self.s_h),width=int(75*self.s_w),height=int(26*self.s_h))
            
            self.last_callback_time = time.time()
            
    def all_children (self) :
        #lista de widget 
        widget_list = self.frm_notebook1.winfo_children()
        
        for item in widget_list :
            if item.winfo_children() :
                widget_list.extend(item.winfo_children())
        
        print(widget_list)
def main():
    root = Tk()
    
    root.state('zoomed')
    #root.geometry('1080x720')
    
    #root.call('tk', 'scaling', 1.3)
    root.minsize(854, 480)
    
    app = main_window()
    root.mainloop()

if __name__ == '__main__':
    main()