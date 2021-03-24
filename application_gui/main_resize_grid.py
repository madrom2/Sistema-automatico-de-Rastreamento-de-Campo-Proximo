#Biblioteca de interface
from tkinter import *
from tkinter.ttk import * # Frame, Label, Entry, Button
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import font

#Biblioteca do mapa de calor
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import serial.tools.list_ports   #Bibliote de conecção serial
import time                      #Biblioteca para delay
import csv                       #Biblioteca salvar dados em arquivo csv
import numpy as np               #Biblioteca de array FUTURO RETIRAR
from datetime import datetime    #Biblioteca do tempo da maquina

#Escrita e Leitura serial com grbl
from cnc_controle import controle_cnc

class main_window(Frame):
    dict_jog = {'up': '$J=G91 Y+% F200',\
                'down': '$J=G91 Y-% F200',\
                'left': '$J=G91 X-% F200',\
                'right': '$J=G91 X+% F200',
                'z_up': '$J=G91 Z+% F200',
                'z_down': '$J=G91 Z-% F200'}
    
    rows, cols = 13, 13  # tamanho da tabela
    rows_disp = 13  # numero de linhas apresentado
    cols_disp = 13 # numero de colunas apresentado
    var_step_x, var_step_y = 1, 1 # passo de cada eixo
    flag_medindo, flag_stop ,flag_resize= False, False, False
    flag_grade, flag_anotacao, flag_auto_maxmin= True, True, True
    tempo_entre_medidas=1 #em segundos
    
    s_w, s_h =1, 1
    n_w, n_h = 1920, 1080
    last_callback_time = time.time()
    
    def __init__(self):
        super().__init__()

        self.initUI()
        
        self.serial_cnc = None
        
    def initUI(self):
        """Configuração da escala e tamanho"""
        self.master.call('tk', 'scaling', 1.3)
        try:
            self.master.state('zoomed')
        except:
            try:
                self.master.attributes('-zoomed', True)
            except:
                self.master.wm_attributes('-zoomed', True)
        
        self.s_w= self.winfo_screenwidth()/self.n_w
        self.s_h= self.winfo_screenheight()/self.n_h
        
        self.padx=3
        self.pady=3
        
        """Configura da Fonte"""
        self.def_font = font.nametofont("TkDefaultFont")
        #self.def_font.config(size=int(15 * (self.s_h+self.s_w)/2))
        
        #self.master.bind("<Configure>", self.resize)
        
        """Configuração do nome da janela"""
        self.master.title('Controle Auto Scan')
        self.pack(fill=BOTH, expand=True)
        
        """Configuração do icone"""
        try:
            icone = PhotoImage(file = 'labcem_icone.png') 
            self.master.iconphoto(False, icone)
        except:
            pass
        
        """Criação notebook"""
        notebook = Notebook(self)
        notebook.pack(fill=BOTH, expand=True)
        
        """Adicionando notebook de medida e controle"""
        self.frm_notebook1 = Frame(notebook)
        self.frm_notebook1.pack(fill=BOTH, expand=True)
        
        notebook.add(self.frm_notebook1, text='      Controle & Medição      ')
        
        self.frm_notebook1.rowconfigure( 0, weight=1)
        self.frm_notebook1.rowconfigure( 1, weight=1)
        self.frm_notebook1.rowconfigure( 2, weight=1)
        self.frm_notebook1.rowconfigure( 3, weight=1)
        self.frm_notebook1.rowconfigure( 4, weight=1)
        self.frm_notebook1.rowconfigure( 5, weight=1)
        self.frm_notebook1.columnconfigure( 0, weight=1)
        self.frm_notebook1.columnconfigure( 1, weight=3, minsize=160)
        self.frm_notebook1.columnconfigure( 2, weight=7, minsize=500)
        
        """Criando Labelframe Serial e seus widgets"""
        lblfrm = LabelFrame(self.frm_notebook1,text="Serial")
        lblfrm.grid(row=0, column=0, columnspan=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)

        lblfrm.rowconfigure( 0, weight=1)
        lblfrm.rowconfigure( 1, weight=1)
        lblfrm.columnconfigure( 0, weight=1)
        lblfrm.columnconfigure( 1, weight=4)
        lblfrm.columnconfigure( 2, weight=1)
        lblfrm.columnconfigure( 3, weight=1)
        
        lbl_01 = Label(lblfrm, text='Analisador:')
        lbl_01.grid(row=0, column=0, padx=self.padx, pady=self.pady)
                
        self.cmb_analyzer = Combobox(lblfrm)
        self.cmb_analyzer.grid(row=0, column=1, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
                
        btn_open_analyzer = Button(lblfrm, text='Abrir')
        btn_open_analyzer.grid(row=0, column=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
                        
        btn_refresh = Button(lblfrm, text='Atualizar')
        btn_refresh.grid(row=0, column=3, rowspan=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
                      
        lbl_02 = Label(lblfrm, text='CNC:')
        lbl_02.grid(row=1, column=0, padx=self.padx, pady=self.pady)

        self.cmb_cnc = Combobox(lblfrm)
        self.cmb_cnc.grid(row=1, column=1, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
                
        btn_open_cnc = Button(lblfrm, text='Abrir')
        btn_open_cnc.grid(row=1, column=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        """Criando Labelframe Controle e seus widgets"""
        frm_ctrls = Labelframe(self.frm_notebook1, text='Controle')
        frm_ctrls.grid(row=1, column=0, columnspan=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        frm_ctrls.columnconfigure( 0, weight=1, minsize=20)
        frm_ctrls.columnconfigure( 1, weight=1, minsize=60)
        frm_ctrls.columnconfigure( 2, weight=1, minsize=60)
        frm_ctrls.columnconfigure( 3, weight=1, minsize=60)
        frm_ctrls.columnconfigure( 4, weight=1, minsize=50)
        frm_ctrls.columnconfigure( 5, weight=1, minsize=60)
        
        frm_ctrls.rowconfigure( 0, weight=1, minsize=20)
        frm_ctrls.rowconfigure( 1, weight=1)
        frm_ctrls.rowconfigure( 2, weight=1)
        frm_ctrls.rowconfigure( 3, weight=1)
        
        lbl_03 = Label(frm_ctrls, text='Y:')
        lbl_03.grid(row=0, column=2)
        
        lbl_04 = Label(frm_ctrls, text='X:')
        lbl_04.grid(row=2, column=0)
        
        lbl_05 = Label(frm_ctrls, text='Z:')
        lbl_05.grid(row=0, column=4)
        
        btn_home = btn_up = Button(frm_ctrls, text= 'Origem')
        btn_home.grid(row=1, column=5, rowspan=3, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        # Primeira linha
        btn_dig_no = Button(frm_ctrls, text=u'\u25F8')
        btn_dig_no.grid(row=1, column=1, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        btn_up = Button(frm_ctrls, text= u'\u25B2')
        btn_up.grid(row=1, column=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_up['command'] = lambda direcao=self.dict_jog['up'] : self.ctrl_movimento_cnc(direcao)      
        
        btn_dig_ne = Button(frm_ctrls, text=u'\u25F9')
        btn_dig_ne.grid(row=1, column=3, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        btn_z_up_btn = Button(frm_ctrls, text= u'\u25B2')
        btn_z_up_btn.grid(row=1, column=4, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_z_up_btn['command'] = lambda direcao=self.dict_jog['z_up'] : self.ctrl_movimento_cnc(direcao)
        
        # Segunda linha
        btn_left_btn = Button(frm_ctrls, text=u'\u25C0')
        btn_left_btn.grid(row=2, column=1, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_left_btn['command'] = lambda direcao=self.dict_jog['left'] : self.ctrl_movimento_cnc(direcao)
        
        btn_home_btn = Button(frm_ctrls, text=u'\u25EF')
        btn_home_btn.grid(row=2, column=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        btn_right_btn = Button(frm_ctrls, text=u'\u25B6')
        btn_right_btn.grid(row=2, column=3, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_right_btn['command'] = lambda direcao=self.dict_jog['right'] : self.ctrl_movimento_cnc(direcao)
        
        self.cmb_step = Combobox(frm_ctrls)# Janela de seleção do tamanho de passo
        self.cmb_step.grid(row=2, column=4, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        self.cmb_step['values'] = ['2','1','0.5','0.1']
        self.cmb_step.current(1)
        
        # Terceira linha       
        btn_diag_so = Button(frm_ctrls, text=u'\u25FA')
        btn_diag_so.grid(row=3, column=1, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        btn_down = Button(frm_ctrls, text=u'\u25BC')
        btn_down.grid(row=3, column=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_down['command'] = lambda direcao=self.dict_jog['down'] : self.ctrl_movimento_cnc(direcao)
        
        btn_diag_se = Button(frm_ctrls, text=u'\u25FF')
        btn_diag_se.grid(row=3, column=3, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
                
        btn_z_down = Button(frm_ctrls, text=u'\u25BC')
        btn_z_down.grid(row=3, column=4, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_z_down['command'] = lambda direcao=self.dict_jog['z_down'] : self.ctrl_movimento_cnc(direcao)
              
        """Criando labelframe dos pontos com botões"""
        frm_pont = Labelframe(self.frm_notebook1, text='Definição dos pontos')
        frm_pont.grid(row=2, column=0, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        frm_pont.rowconfigure( 0, weight=1)
        frm_pont.columnconfigure( 0, weight=1)
        frm_pont.columnconfigure( 1, weight=1)
        
        btn_pont_start = Button(frm_pont, text='Ponto 1')
        btn_pont_start.grid(row=0, column=0, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_pont_start['command'] = self.start_point
        
        btn_pont_end = Button(frm_pont, text='Ponto 2')
        btn_pont_end.grid(row=0, column=1, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_pont_end['command'] = self.end_point
        
        """Criando labelframe tamanho da matriz"""
        frm_inic = Labelframe(self.frm_notebook1, text='Tamanho Matriz')
        frm_inic.grid(row=3, column=0, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        frm_inic.columnconfigure( 0, weight=1, minsize=20)
        frm_inic.columnconfigure( 1, weight=1)
        frm_inic.columnconfigure( 2, weight=1, minsize=20)
        frm_inic.columnconfigure( 3, weight=1)
        
        frm_inic.rowconfigure( 0, weight=1)
        frm_inic.rowconfigure( 1, weight=1)
        
        lbl_08 = Label(frm_inic, text='X:')
        lbl_08.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        
        self.var_matriz_x=Entry(frm_inic)
        self.var_matriz_x.insert(END, '%d' % self.rows)
        self.var_matriz_x.grid(row=0, column=1, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        lbl_9 = Label(frm_inic, text='Y:')
        lbl_9.grid(row=0, column=2, padx=self.padx, pady=self.pady)
        
        self.var_matriz_y=Entry(frm_inic)
        self.var_matriz_y.insert(END, '%d' % self.cols)
        self.var_matriz_y.grid(row=0, column=3, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        btn_matriz_refresh = Button(frm_inic, text='Atualizar')
        btn_matriz_refresh.grid(row=1, column=1, columnspan=3, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_matriz_refresh['command'] = self.att_matriz
        
        """Criando labelframe Frequência e entrada da mesma"""
        frm_freq = Labelframe(self.frm_notebook1, text='Frequência')
        frm_freq.grid(row=4, column=0, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        frm_freq.columnconfigure( 0, weight=1, minsize=75)
        frm_freq.columnconfigure( 1, weight=10, minsize=75)
        frm_freq.columnconfigure( 2, weight=1)
        frm_freq.rowconfigure( 0, weight=1)
        frm_freq.rowconfigure( 1, weight=1)
        
        lbl_08 = Label(frm_freq, text='Frequência:')
        lbl_08.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        
        self.var_freq=Entry(frm_freq)
        self.var_freq.insert(END, '%d' % 300)
        self.var_freq.grid(row=0, column=1, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        self.cmb_freq = Combobox(frm_freq)
        self.cmb_freq.grid(row=0, column=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        self.cmb_freq['values'] = ['GHz','MHz','KHz']
        self.cmb_freq.current(1)
        
        self.btn_freq_refresh = Button(frm_freq, text='Atualizar')
        self.btn_freq_refresh.grid(row=1, column=1, columnspan=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        self.btn_freq_refresh['command'] = self.att_freq
        
        """Criando labelframe Parametros e label de dados"""
        frm_param = Labelframe(self.frm_notebook1, text='Parametros')
        frm_param.grid(row=2, column=1, rowspan=3, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        frm_param.columnconfigure( 0, weight=1)
        frm_param.rowconfigure( 0, weight=1)
        frm_param.rowconfigure( 1, weight=1)
        frm_param.rowconfigure( 2, weight=1)
        frm_param.rowconfigure( 3, weight=1)
        frm_param.rowconfigure( 4, weight=1)
        frm_param.rowconfigure( 5, weight=1)
        frm_param.rowconfigure( 6, weight=1)
        frm_param.rowconfigure( 7, weight=1)
        
        lbl_par_1 = Label(frm_param, text='Possição Ponto 1 (cm):')
        lbl_par_2 = Label(frm_param, text='Possição Ponto 2 (cm):')
        lbl_par_3 = Label(frm_param, text='Passo eixo X (cm):')
        lbl_par_4 = Label(frm_param, text='Passo eixo Y (cm):')
        self.lbl_par_5 = Label(frm_param, text='0,00 0,00')
        self.lbl_par_6 = Label(frm_param, text='0,00 0,00')
        self.lbl_par_7 = Label(frm_param, text='0,0000')
        self.lbl_par_8 = Label(frm_param, text='0,0000')
        
        lbl_par_1.grid(row=0, column=0, sticky=W, padx=self.padx, pady=self.pady)
        lbl_par_2.grid(row=2, column=0, sticky=W, padx=self.padx, pady=self.pady)
        lbl_par_3.grid(row=4, column=0, sticky=W, padx=self.padx, pady=self.pady)
        lbl_par_4.grid(row=6, column=0, sticky=W, padx=self.padx, pady=self.pady)
        self.lbl_par_5.grid(row=1, column=0, sticky=E, padx=self.padx, pady=self.pady)
        self.lbl_par_6.grid(row=3, column=0, sticky=E, padx=self.padx, pady=self.pady)
        self.lbl_par_7.grid(row=5, column=0, sticky=E, padx=self.padx, pady=self.pady)
        self.lbl_par_8.grid(row=7, column=0, sticky=E, padx=self.padx, pady=self.pady)
        
        """Botões de medição"""
        frm_btn_meas= Frame(self.frm_notebook1)
        frm_btn_meas.grid(row=5, column=0, columnspan=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        frm_btn_meas.columnconfigure( 0, weight=1)
        frm_btn_meas.columnconfigure( 1, weight=1)
        frm_btn_meas.columnconfigure( 2, weight=1)
        frm_btn_meas.rowconfigure( 0, weight=1)
        
        btn_stop = Button(frm_btn_meas, text='Parar Medição')
        btn_stop.grid(row=0, column=0, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_stop['command'] = self.stop_meas
        
        self.btn_pause = Button(frm_btn_meas, text='Pausar Medição')
        self.btn_pause.grid(row=0, column=1, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        self.btn_pause['command'] = self.pause_meas
        
        btn_start = Button(frm_btn_meas, text='Iniciar Medição')
        btn_start.grid(row=0, column=2, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_start['command'] = self.measurement
        
        """Frame para coluna da direita"""
        self.frm_direita = Frame(self.frm_notebook1)
        self.frm_direita.grid(row=0, column=2, rowspan=6, sticky=N+S+E+W)
        
        self.frm_direita.columnconfigure( 0, weight=1)
        self.frm_direita.rowconfigure( 0, weight=1)
        self.frm_direita.rowconfigure( 1, weight=100)
        self.frm_direita.rowconfigure( 2, weight=1)
        
        """Criando labelfram de salvar arquivo"""
        frm_04 = Labelframe(self.frm_direita, text='Arquivo')
        frm_04.grid(row=0, column=0, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        frm_04.columnconfigure( 0, weight=1)
        frm_04.columnconfigure( 1, weight=10)
        frm_04.columnconfigure( 2, weight=1)
        frm_04.columnconfigure( 3, weight=1)
        frm_04.rowconfigure( 0, weight=1)
        
        lbl_11 = Label(frm_04, text='Nome do Arquivo:')
        lbl_11.grid(row=0, column=0, padx=self.padx, pady=self.pady)
        
        self.str_save = Entry(frm_04)
        self.str_save.grid(row=0, column=1, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        lbl_12 = Label(frm_04, text='info.xlsx')
        lbl_12.grid(row=0, column=2, padx=self.padx, pady=self.pady)
        
        btn_save = Button(frm_04, text='Salvar')
        btn_save.grid(row=0,column=3, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        btn_save['command'] = self.save
        
        """Matriz de dados"""
        self.att_matriz()
        
        """Labelfrade progresso"""
        frm_progress = Labelframe(self.frm_direita)
        frm_progress.grid(row=2, column=0, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        frm_progress.columnconfigure( 0, weight=1)
        frm_progress.columnconfigure( 1, weight=10)
        frm_progress.rowconfigure( 0, weight=1)
        
        lbl_10 = Label(frm_progress, text='Tempo estimado de '+'HH'+' : '+'MM'+' : '+'SS')
        lbl_10.grid(row=0, column=0, sticky=W, padx=self.padx, pady=self.pady)
        
        self.var_pb=DoubleVar()
        self.var_pb.set(1)
        
        pb=Progressbar(frm_progress,variable=self.var_pb,maximum=100)
        pb.grid(row=0, column=1, sticky=N+S+E+W, padx=self.padx, pady=self.pady)
        
        """Inicializações"""
        self.lista_serial()
        self.att_matriz()
    
    def resize(self,event):
        cur_time = time.time()
        if (cur_time - self.last_callback_time) > 0.80:
            print(event.width, event.height)
            self.ajuste_fonte(event.height, event.width)
            
            self.last_callback_time = time.time()
    
    #Função de ajusta da fonte de acordo com o tamanho da tela
    def ajuste_fonte(self, altura_atual, largura_atual):
        self.s_h= altura_atual/self.n_h
        self.s_w= largura_atual/self.n_w
            
        self.def_font.config(size=int(9 * (self.s_h+self.s_w)/2))
    
    #Função para atualizar lista das portas COM
    def lista_serial(self):        
        portas=controle_cnc.list_serial()
        
        self.cmb_analyzer['values'] = portas
        self.cmb_analyzer.set('Escolha...')
        
        self.cmb_cnc['values'] = portas
        self.cmb_cnc.set('Escolha...')
    
    #Função para abrir porta serial da CNC
    def abrir_serial_cnc(self):
        if (self.verifica_medicao()):
            return
        com_port =  self.cmb_cnc.get()
        self.serial_cnc=controle_cnc.open_serial_cnc(com_port, self.serial_cnc)
        
        if(self.serial_cnc==None):
            self.btn_open_cnc['text'] = 'Abrir'
        else:
            #forçar conecção
            self.btn_open_cnc['text'] = 'Fechar'
    
    #Função de movimento através do botões de controle
    def ctrl_movimento_cnc(self, direcao):
        if (self.serial_cnc != None):
            direcao = direcao.replace('%', self.cmb_step.get())
            str_resposta=controle_cnc.cnc_jog(direcao, self.serial_cnc)
            
            self.txt_log.insert(END, direcao+"  ")
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
            
    #Função de motivmento durante medição        
    def meas_movimento_cnc(self, direcao, step):
        if (self.serial_cnc != None):
            direcao = direcao.replace('%', str(step))
            str_resposta=controle_cnc.cnc_jog(direcao, self.serial_cnc)
            self.txt_log.insert(END, direcao+"  ")
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
    
    #Função de envio comandos para serial CNC
    def envia_cmd_cnc(self):
        if (self.serial_cnc != None):
            str_comando=self.ent_cmd.get()
            
            str_resposta=controle_cnc.send_cmd(str_comando, self.serial_cnc)
            
            self.txt_log.insert(END, str_resposta)
            self.txt_log.see(END)
    
    #Função de evento de "ENTER"       
    def comp_s(self, event):
        self.envia_cmd_cnc()
    
    #Função para verificar se está medindo     
    def verifica_medicao(self):
        #Caso esteja medindo acusa erro e retorna true para if de break
        if (self.flag_medindo):
            messagebox.showwarning(title="Erro Ação impossivel",
                                   message="Não é possivel realizar está função\ndurante a medição")
            return True
        else:
            return False
    
    #Função se string contem somente numero e maior que zero     
    def verifica_string(self, string, mensagem):
        #Caso string contem somente numero
        if not(string.isdigit()):
            messagebox.showwarning(title=('Erro nos valores de '+mensagem),
                                   message=('O valor '+mensagem+' deve ser um numero decimal maior que zero'))
            return True
        
        if(int(string)==0):
            messagebox.showwarning(title=('Erro nos valores de '+mensagem),
                                   message=('O valor '+mensagem+' deve ser um numero decimal maior que zero'))
            return True
        else:
            return False
        
    #Verifica se string é um numero decimal     
    def verifica_numero(self, string, mensagem):
        #Caso numero comece com sinal negativo
        if(string[0]=='-'):
            string=string.replace('-','0',1)
        if not(string.isdigit()):#verifica se é somente digito
            messagebox.showwarning(title=('Erro nos valores de '+mensagem),
                                   message=('O valor '+mensagem+' deve ser um numero decimal'))
            return True
        return False
       
    
    #Função de definição de ponto 1
    def start_point(self):
        if (self.verifica_medicao()):
            return
        xyz=controle_cnc.current_pos(self.serial_cnc)
        self.start_point_x=float(xyz[0])
        self.start_point_y=float(xyz[1])
        
        self.lbl_par_5.config(text=(("%.2f %.2f" % (self.start_point_x, self.start_point_y)).replace('.',',')))
        self.atualiza_passo()
    
    #Funções de definição de ponto 2
    def end_point(self):#da pra melhorar juntado star_point com end_point passando pra função se é start ou end
        if (self.verifica_medicao()):
            return
        xyz=controle_cnc.current_pos(self.serial_cnc)
        self.end_point_x=float(xyz[0])
        self.end_point_y=float(xyz[1])
        
        self.lbl_par_6.config(text=(("%.2f %.2f" % (self.end_point_x, self.end_point_y)).replace('.',',')))
        self.atualiza_passo()
    
    #Função para atualiza passo entre medidas
    def atualiza_passo(self):
        if (self.verifica_medicao()):
            return
        try:
            #Para o passo do eixo X
            self.var_step_x=abs(self.start_point_x-self.end_point_x)/(int(self.cols)-1)
            print("xlinha="+str(self.var_step_x))
            self.lbl_par_7.config(text=(("%.4f" % (self.var_step_x)).replace('.',',')))
            #Para o passo do eixo Y
            self.var_step_y=abs(self.start_point_y-self.end_point_y)/(int(self.rows)-1)
            print("ylinha="+str(self.var_step_y))
            self.lbl_par_8.config(text=(("%.4f" % (self.var_step_y)).replace('.',',')))
        except AttributeError:
            return
    
    #Função de ativação flag de parar medição
    def stop_meas(self):
        if(self.flag_medindo):
            #envia para o arduino parar
            self.flag_stop=True
            self.flag_medindo=False
    
    #Função de ativação flag de pausa medição
    def pause_meas(self):
        if(self.flag_medindo):
            if not (self.flag_stop):
                #envia para o arduino parar
                self.flag_stop=True
            else :
                self.btn_pause.config(text=('Continuar'))
                pass # AQUI ENTRA CONTINUAÇÃO DA MEDIÇÃO
    
    #Função para atualziar tamanho da matriz
    def att_matriz(self):
        if (self.flag_medindo):
            print("Botão pressionado y="+str(row)+" x="+str(col))
            messagebox.showwarning(title="Erro Ação impossivel",
                                   message="Não é possivel realizar está função")
            return
        
        valor_x = self.var_matriz_x.get()
        valor_y = self.var_matriz_y.get()
        
        #tratamento do valor de entrada
        if (self.verifica_string(valor_x, 'X e Y') or
            self.verifica_string(valor_y, 'X e Y')):
            return
        
        if(int(valor_x)==0 or int(valor_y)==0):
            messagebox.showwarning(title="Erro nos valores X e Y", message="X e Y deve ser um numero decimal maior que zero\n ")
            return
        
        #destruir tabela existente
        try:
            self.frm_tabela.destroy()
        except AttributeError:
            pass
        else:
            self.frame2.destroy()
            self.canvas.destroy()
            self.buttons_frame.destroy()
            for i in range(0, self.rows):
                for j in range(0, self.cols):
                    self.button_matriz[i][j].destroy()
                    
        #//////////////////////////////////////////////////////////////////////////////////
        # Cria o frame para area dos botões e scrollbar
        self.frame2 = Frame(self.frm_direita, relief=RIDGE)
        self.frame2.grid(row=1, column=0, sticky=N+S+E+W)
        
        self.frame2.rowconfigure( 0, weight=1)
        self.frame2.rowconfigure( 1, weight=1, minsize=10)
        self.frame2.columnconfigure( 0, weight=1)
        self.frame2.columnconfigure( 1, weight=1, minsize=10)
        
        
        # Cria area dos botões
        self.canvas = Canvas(self.frame2)
        self.canvas.grid(row=0, column=0, sticky=N+S+E+W)
        
        # Cria scrollbar vertical e anexa a area de botões
        vsbar = Scrollbar(self.frame2, orient=VERTICAL, command=self.canvas.yview)
        vsbar.grid(row=0, column=1, sticky=N+S+E)
        self.canvas.configure(yscrollcommand=vsbar.set)
        
        # Cria scrollbar horizontal e anexa a area de botões
        hsbar = Scrollbar(self.frame2, orient=HORIZONTAL, command=self.canvas.xview)
        hsbar.grid(row=1, column=0, sticky=S+E+W)
        self.canvas.configure(xscrollcommand=hsbar.set)

        # Cria frame que contem os botões
        self.buttons_frame = Frame(self.canvas)
        
        # Cria matriz de botões
        self.button_matriz = [[None for _ in range(int(valor_x))] for _ in range(int(valor_y))]
        
        # Configuração do grid
        for i in range(0, int(valor_y)):
            self.buttons_frame.grid_columnconfigure(i, weight=1)
        for j in range(0, int(valor_x)):
            self.buttons_frame.grid_rowconfigure(j, weight=1)
            
        # Adiciona botões no frame
        for i in range(0, int(valor_y)):
            for j in range(0, int(valor_x)):
                self.button_matriz[i][j] = Button(self.buttons_frame, text="m[%d,%d]\nx=%d\ny=%d" % (int(valor_x), int(valor_y),j+1,i+1))
                self.button_matriz[i][j].grid(row=i, column=j, sticky=N+S+E+W)
                self.button_matriz[i][j]['command'] = lambda var1=i, var2=j: self.meas_ponto(var1,var2)
        
        # Cria janela para os botões
        self.canvas.create_window((0,0), window=self.buttons_frame, anchor=NW)

        self.buttons_frame.update_idletasks()  # Needed to make bbox info available.
        bbox = self.canvas.bbox(ALL)  # Get bounding box of canvas with Buttons.

        # Define the scrollable region as entire canvas with only the desired
        # number of rows and columns displayed.
        w, h = bbox[2]-bbox[1], bbox[3]-bbox[1]
        dw, dh = int((w/int(valor_x)) * self.cols_disp), int((h/int(valor_y)) * self.rows_disp)
        self.canvas.configure(scrollregion=bbox, width=dw, height=dh)
        
        #//////////////////////////////////////////////////////////////////////////////////
                
        self.cols=int(valor_x)
        self.rows=int(valor_y)
        self.atualiza_passo()
    
    #Função de re medição de ponto
    def meas_ponto(self,row,col):
        if (self.verifica_medicao()):
            return
        
        #Verifica se ponto superior esquerdo foi definido e atribui a variaveis
        #de coordenada
        try:
            if(self.start_point_x<self.end_point_x): x = float(self.start_point_x)
            else: x = float(self.end_point_x)
            if(self.start_point_y>self.end_point_y): y = float(self.start_point_y)
            else: y = float(self.end_point_y)
            print("ponto inicial= "+str(x)+' '+str(y))
        except AttributeError:
            messagebox.showwarning(title="Erro!!!Limites não definidos",
                                   message="Pontos não definidos    ")
            return
        
        self.flag_medindo=True
        print("Medir ponto x="+str(col)+" y="+str(row))            
        
        xyz=controle_cnc.current_pos(self.serial_cnc)
        
        x=x+(self.var_step_x*col)-float(xyz[0])
        if not (x==0):#Vai para a coordenada do ponto no eixo x
            print("movimento x="+str(x))
            if(x>0):direcao=self.dict_jog['right']
            elif(x<0):direcao=self.dict_jog['left']
            self.meas_movimento_cnc(direcao, abs(x))
            time.sleep(4) #colocar delay
            
        y=y+(self.var_step_y*row)-float(xyz[1])
        if not (y==0):#Vai para a coordenada do ponto no eixo y
            print("movimento y="+str(y))
            if(y>0):direcao=self.dict_jog['up']
            elif(y<0):direcao=self.dict_jog['down']
            self.meas_movimento_cnc(direcao, abs(y))
            time.sleep(4) #colocar delay
        
        self.flag_medindo=False
    
    #Função comunicação com analisador para definição
    #frequencia de medição
    def att_freq(self):
        if (self.verifica_medicao()):
            return
        
        freq = self.var_freq.get()
        
        #Verifica se string contem somente numero e maior que zero
        if (self.verifica_string(freq, 'frequência')):
            return
        
        if(self.cmb_freq.get()=="KHz"):
            freq=int(freq)*pow(10, 3)
        elif(self.cmb_freq.get()=="MHz"):
            freq=int(freq)*pow(10, 6)
        else:
            freq=int(freq)*pow(10, 9)
        #AQUI entra Função que manda pro analisador
        print('SYST:MODE RMOD')#Ativa modo reciver
        print("RMOD:FREQ {}.format("+ str(freq) +")")#Define frequencia do modo reciver
        
    #Função de medição
    def measurement(self):
        if (self.verifica_medicao()):
            return
        #Verifica se ponto superior esquerdo foi definido e atribui a variaveis
        #de coordenada
        try:
            if(self.start_point_x<self.end_point_x): x = float(self.start_point_x)
            else: x = float(self.end_point_x)
            if(self.start_point_y>self.end_point_y): y = float(self.start_point_y)
            else: y = float(self.end_point_y)
            print("ponto inicial= "+str(x)+' '+str(y))
        except AttributeError:
            messagebox.showwarning(title="Erro!!!Limites não definidos",
                                   message="Pontos não definidos    ")
            return
        
        self.meas_time = datetime.now()
        self.flag_medindo=True
        
        self.var_pb.set(1)
        
        xyz=controle_cnc.current_pos(self.serial_cnc)
        
        x= x-float(xyz[0])
        if not (x==0):#Vai para a coordenada do ponto no eixo x
            print("movimento x="+str(x))
            if(x>0):direcao=self.dict_jog['right']
            elif(x<0):direcao=self.dict_jog['left']
            self.meas_movimento_cnc(direcao, abs(x))
            time.sleep(4) #colocar delay
            
        y=y-float(xyz[1])
        if not (y==0):#Vai para a coordenada do ponto no eixo y
            print("movimento y="+str(y))
            if(y>0):direcao=self.dict_jog['up']
            elif(y<0):direcao=self.dict_jog['down']
            self.meas_movimento_cnc(direcao, abs(y))
            time.sleep(4) #colocar delay
        
        self.matrix_meas = [[-80 for _ in range(self.cols)] for _ in range(self.rows)]
        
        var_progressbar=0
        self.var_pb.set(var_progressbar)
        step_progressbar=100/((self.rows)*(self.cols))
        
        flag_ordem=True #false=esquerda pra direita
        for i in range(0, self.rows):#linha
            if(flag_ordem):
                for j in range(0, self.cols):#coluna
                    if(self.flag_stop):
                        return
                    self.matrix_meas[i][j]=-40# entra valor medido
                    self.button_matriz[i][j].config(text="meas+\nx=%d\ny=%d" % (j+1, i+1))
                    var_progressbar=var_progressbar+step_progressbar
                    self.var_pb.set(var_progressbar)
                    self.master.update()
                    print("Mede")
                    if(j+1<self.cols):
                        time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                        self.meas_movimento_cnc(self.dict_jog['right'], self.var_step_x)
                flag_ordem=False
            else:
                for j in reversed(range(0,self.cols)):#coluna
                    if(self.flag_stop):
                        return
                    self.matrix_meas[i][j]=4# entra valor medido
                    self.button_matriz[i][j].config(text="meas-\nx=%d\ny=%d" % (j+1, i+1))
                    var_progressbar=var_progressbar+step_progressbar
                    self.var_pb.set(var_progressbar)
                    self.master.update()
                    print ("Mede")
                    if(j!=0):
                        time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                        self.meas_movimento_cnc(self.dict_jog['left'], self.var_step_x)
                flag_ordem=True
            if(i+1<self.rows):
                time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                self.meas_movimento_cnc(self.dict_jog['down'], self.var_step_y)
                
        self.flag_medindo=False
    
    #Função para salvar arquivo com extensão csv
    def save(self):
        try:
            self.meas_time.strftime
            file_path=(filedialog.askdirectory()+'\\'+self.str_save.get()+
                       self.meas_time.strftime("_%d-%m-%Y_%H-%M")+".csv")
            
            #Abrir arquivo csv mode "write"
            file = open(file_path, 'w', newline ='') 

            #Escreve resultado da medida no arquivo csv
            with file:
                write = csv.writer(file, delimiter=';') 
                write.writerows(self.matrix_meas) 
            
        except AttributeError:
            messagebox.showwarning(title="Erro!!!Medida não realizada", message="Nenhuma informação para salvar ")
    
    #Função de alteração da flag de plot da grade
    def plot_grade(self):
        if(self.flag_grade):
            self.btn_plt_grade.config(text='        Grade\nDESABILITADO')
            self.flag_grade=False
        else:
            self.btn_plt_grade.config(text='      Grade\nHABILITADO')
            self.flag_grade=True
    
    #Função de alteração da flag de plot das anotações nos eixos
    def plot_anotacao(self):     
        if(self.flag_anotacao):
            self.btn_plt_anotacao.config(text='     Anotação\nDESABILITADO')
            self.flag_anotacao=False
        else:
            self.btn_plt_anotacao.config(text='   Anotação\nHABILITADO')
            self.flag_anotacao=True
            
    #Função de alteração da flag de plot das anotações nos eixos
    def plot_auto_maxmin(self):     
        if(self.flag_auto_maxmin):
            self.btn_plt_maxmin.config(text='MAX/MIN automático DESABILITADO')
            self.flag_auto_maxmin=False
        else:
            self.btn_plt_maxmin.config(text='MAX/MIN automático HABILITADO')
            self.flag_auto_maxmin=True
            
    #Função de apresentação do mapa de calor para o dado medida realizada
    def plot_dadoatual(self):
        if not(self.flag_auto_maxmin):
            if(self.verifica_numero(self.var_plot_max.get(), 'MAX e MIN do plot')):
                return
            if(self.verifica_numero(self.var_plot_min.get(), 'MAX e MIN do plot')):
                return
        try:
            data=self.matrix_meas
        except:
            #erro no dado atual
            return
        
        if(self.flag_auto_maxmin):
            vmax=max(max(data))
            vmin=min(min(data))
        else:
            vmax=int(self.var_plot_max.get())#função que verifica se é numero
            vmin=int(self.var_plot_min.get())#função que veririca se é numero
        step=[self.var_step_x, self.var_step_y]
        escolhas=[self.cmb_plot_cor.get(), self.var_plot_titulo.get(),
                  self.cmb_plot_interpolacao.get()]
        flag=[self.flag_anotacao, self.flag_grade, False]
        destino_save=None
    
        self.mapa_de_calor(data, vmax, vmin, step, flag, escolhas, destino_save)
        
    def plot_arquivo_csv(self):
        if not (self.flag_auto_maxmin):
            if(self.verifica_numero(self.var_plot_max.get(), 'MAX e MIN do plot')):
                return
            if(self.verifica_numero(self.var_plot_min.get(), 'MAX e MIN do plot')):
                return
        if(self.verifica_string(self.var_plot_tamanho_x.get(), 'Tamanho da placa')):
            return
        if(self.verifica_string(self.var_plot_tamanho_y.get(), 'Tamanho da placa')):
            return
        try:
            data_caminho = filedialog.askopenfilename(initialdir = "/",
                                                      title = "Selecione arquivo com extensão CSV",
                                                      filetypes = (("Arquivo Csv","*.csv*"),
                                                                   ("all files","*.*")))
            data=[]
            with open(data_caminho, 'r') as file:
                reader = csv.reader(file, delimiter = ';', quoting=csv.QUOTE_NONNUMERIC)
                for row in reader: # each row is a list
                    data.append(row)
        except:
            return
        if(len(data)<1)or(len(data[0])<1):
            #acusa erro de arquivo csv com problema na linha ou coluna
            return
        
        if(self.flag_auto_maxmin):
            vmax=max(max(data))
            vmin=min(min(data))
        else:
            vmax=int(self.var_plot_max.get())#função que verifica se é numero
            vmin=int(self.var_plot_min.get())#função que veririca se é numero
        step=[1,1]
        step[0]=float(self.var_plot_tamanho_x.get())/(len(data[0])-1)
        step[1]=float(self.var_plot_tamanho_y.get())/(len(data)-1)
        
        escolhas=[self.cmb_plot_cor.get(), self.var_plot_titulo.get(),
                  self.cmb_plot_interpolacao.get()]
        flag=[self.flag_anotacao, self.flag_grade, False]
        destino_save=None
        
        self.mapa_de_calor(data, vmax, vmin, step, flag, escolhas, destino_save)
    
    def plot_salva(self):
        files = [('Portable Graphics Format(PNG)', '*.png'),
                 ('All Files', '*.*')] 
        destino= filedialog.asksaveasfilename(filetypes = files, defaultextension = ".png")
        
        plt.savefig(destino,bbox_inches="tight")
    
    def mapa_de_calor(self, data, vmax, vmin, step, flag, escolhas, destino_save):
        #flag[0] habilitação da anotação
        #flag[1] habilitação da grade
        #flag[2] escolha entre apresentação ou salvar
        #step[0] passo x
        #step[1] passo y
        #escolhas[0] cor do mapa de calor
        #escolhas[1] titulo do mapa de calor
        #escolhas[2] interpolação do mapa de calor
        
        try:
            self.canvas2.destroy()
            plt.close('all')
        except:
            pass
        
        #Gera figura de plotagem 
        fig, ax = plt.subplots()
        
        #cor cinza de background
        if not(flag[2]):
            fig.patch.set_facecolor('#F0F0F0')
        
        #Gera mapa de calor
        im = ax.imshow(data, interpolation=escolhas[2], cmap=escolhas[0], vmax=vmax, vmin=vmin)

        #Cria anotação do grid
        anotacao_y = []
        for i in range (len(data)):
            anotacao_y.append('%.2fcm' % float(i*step[1]))
            
        anotacao_x=[]
        for i in range (len(data[0])):
            anotacao_x.append('%.2fcm' % float(i*step[0]))
            
        #Configuração de apresentação das anotações
        if(flag[0]):
            ax.set_xticks(np.arange(len(anotacao_x)))
            ax.set_yticks(np.arange(len(anotacao_y)))
            ax.set_xticklabels(anotacao_x)
            ax.set_yticklabels(anotacao_y)
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                     rotation_mode="anchor")

        #Titulo do mapa de calor
        ax.set_title(escolhas[1])

        #Adiciona barra de cor
        if(len(data)>len(data[0])):
            plt.colorbar(im, shrink=1)
        else:
            plt.colorbar(im, shrink=0.8)
        
        #Tamanho do mapa de calor
        plt.xlim(right=len(data[0])-0.5)
        plt.xlim(left=-0.5)
        plt.ylim(top=-0.5)
        plt.ylim(bottom=len(data)-0.5)
        
        #Grade
        if(flag[1]):
            plt.grid(color='w', which='major', alpha=0.5)
        
        self.canvas2 = FigureCanvasTkAgg(fig, master = self.frm_heatmap)
        self.canvas2.draw()
        if(len(data)>=len(data[0])):
            self.canvas2.get_tk_widget().place(x=5,y=5,height=650)
        else:
            self.canvas2.get_tk_widget().place(x=5,y=5,width=790)

def main():
    root = Tk()
    root.minsize(854, 480)
    
    app = main_window()
    root.mainloop()

if __name__ == '__main__':
    main()