from tkinter import *
from tkinter.ttk import * # Frame, Label, Entry, Button
from tkinter import scrolledtext
from tkinter import filedialog
#from tkinter import font as tkFont

import serial.tools.list_ports
import time
import openpyxl 
from datetime import datetime

class main_window(Frame):
    dict_jog = {'up': '$J=G91 Y+% F100000',\
                'down': '$J=G91 Y-% F100000',\
                'left': '$J=G91 X-% F100000',\
                'right': '$J=G91 X+% F100000',
                'z_up': '$J=G91 Z+% F100000',
                'z_down': '$J=G91 Z-% F100000'}
    
    rows, cols = 13, 13  # tamanho da tabela
    rows_disp = 10.5  # numero de linhas apresentado
    cols_disp = 7.75 # numero de colunas apresentado
    var_step_x, var_step_y = 1, 1 # passo de cada eixo
    flag_medindo, flag_stop = False, False
    tempo_entre_medidas=0.2 #em segundos
    
    def __init__(self):
        super().__init__()

        self.initUI()
        
        self.serial_cnc = None
    
    def initUI(self):
        #---nome da janela---------------------
        self.master.title('Controle Auto Scan')
        self.pack(fill=BOTH, expand=True)
        
        #-----------------------------configuração do frame-----------------------------
        #---nome do frame---------------------
        frm_01 = Labelframe(self, text='Serial')
        frm_01.place(x=10,y=10,width=440,height=80)
        
        #---configuração da linha/coluna------
        frm_01.columnconfigure(0, pad=3)
        frm_01.columnconfigure(1, pad=3)
        frm_01.rowconfigure(0, pad=3)
        frm_01.rowconfigure(1, pad=3)
        frm_01.rowconfigure(2, pad=3)
        frm_01.rowconfigure(3, pad=3)
        
        #---configuração linha analisador-----
        lbl_01 = Label(frm_01, text='Analisador:')
        lbl_01.grid(row=0, column=0, padx= 3)
        
        self.cmb_analyzer = Combobox(frm_01, width=27)
        self.cmb_analyzer.grid(row=0, column=1, padx= 3)
        
        btn_open_analyzer = Button(frm_01, text='Abrir')
        btn_open_analyzer.grid(row=0, column=2, padx= 3)
        
        #---Atualização de ports-----------
        btn_refresh = Button(frm_01, text='Atualizar')
        btn_refresh.place(x=353,y=1,width=75,height=53)
        btn_refresh['command'] = self.list_serial
        
        #---configuração linha CNC---------      
        lbl_02 = Label(frm_01, text='CNC:')
        lbl_02.grid(row=1, column=0, padx= 3)

        self.cmb_cnc = Combobox(frm_01, width=27)
        self.cmb_cnc.grid(row=1, column=1, padx= 3)
        
        self.btn_open_cnc = Button(frm_01, text='Abrir')
        self.btn_open_cnc.grid(row=1, column=2, padx= 3)
        self.btn_open_cnc['command'] = self.open_serial_cnc
        
        #---nome do frame---------------------
        frm_ctrls = Labelframe(self, text='Controle')
        frm_ctrls.place(x=10,y=365,width=440,height=340)
        
        #---configuração da linha/coluna------
        frm_ctrls.columnconfigure(0, pad=3)
        frm_ctrls.columnconfigure(1, pad=3)
        frm_ctrls.columnconfigure(2, pad=3)
        frm_ctrls.columnconfigure(3, pad=3)
        frm_ctrls.columnconfigure(4, pad=3)
        
        frm_ctrls.rowconfigure(0, pad=3)
        frm_ctrls.rowconfigure(1, pad=3)
        frm_ctrls.rowconfigure(2, pad=3)
        frm_ctrls.rowconfigure(3, pad=3)
        frm_ctrls.rowconfigure(3, pad=7)
        frm_ctrls.rowconfigure(4, pad=7)
        
        #---escrita XYZ---------------------
        lbl_03 = Label(frm_ctrls, text='Y:')
        lbl_03.grid(row=0, column=2)
        
        lbl_04 = Label(frm_ctrls, text='             X:')
        lbl_04.grid(row=2, column=0)
        
        lbl_05 = Label(frm_ctrls, text='Z:')
        lbl_05.grid(row=0, column=4)
        
        #---configuração linhas------------   
        # Primeira linha
        btn_dig_no = Button(frm_ctrls, text=u'\u25F8')
        btn_dig_no.grid(row=1, column=1)
        
        btn_up = Button(frm_ctrls, text= u'\u25B2')
        btn_up.grid(row=1, column=2)
        btn_up['command'] = lambda arg1=self.dict_jog['up'] : self.cnc_jog(arg1)       
        
        btn_dig_ne = Button(frm_ctrls, text=u'\u25F9')
        btn_dig_ne.grid(row=1, column=3)
        
        btn_z_up_btn = Button(frm_ctrls, text= u'\u25B2')
        btn_z_up_btn.grid(row=1, column=4)
        btn_z_up_btn['command'] = lambda arg1=self.dict_jog['z_up'] : self.cnc_jog(arg1)
        
        # Segunda linha
        btn_left_btn = Button(frm_ctrls, text=u'\u25C0')
        btn_left_btn.grid(row=2, column=1)
        btn_left_btn['command'] = lambda arg1=self.dict_jog['left'] : self.cnc_jog(arg1)
        
        btn_home_btn = Button(frm_ctrls, text=u'\u25EF')
        btn_home_btn.grid(row=2, column=2)
        
        btn_right_btn = Button(frm_ctrls, text=u'\u25B6')
        btn_right_btn.grid(row=2, column=3)
        btn_right_btn['command'] = lambda arg1=self.dict_jog['right'] : self.cnc_jog(arg1)
        
        # Terceira linha       
        btn_diag_so = Button(frm_ctrls, text=u'\u25FA')
        btn_diag_so.grid(row=3, column=1)
        
        btn_down = Button(frm_ctrls, text=u'\u25BC')
        btn_down.grid(row=3, column=2)
        btn_down['command'] = lambda arg1=self.dict_jog['down'] : self.cnc_jog(arg1)
        
        btn_diag_se = Button(frm_ctrls, text=u'\u25FF')
        btn_diag_se.grid(row=3, column=3)
                
        btn_z_down = Button(frm_ctrls, text=u'\u25BC')
        btn_z_down.grid(row=3, column=4)
        btn_z_down['command'] = lambda arg1=self.dict_jog['z_down'] : self.cnc_jog(arg1)

        # Janela de seleção do tamanho de passo
        self.cmb_step = Combobox(frm_ctrls, width=5)
        self.cmb_step.grid(row=2, column=4)
        self.cmb_step['values'] = ['10','5','2','1','0.1']
        self.cmb_step.current(3)        
        
        lbl_06 = Labelframe(frm_ctrls, text='Log:')
        lbl_06.place(x=10,y=120,width=415,height=170)
                
        self.txt_log = scrolledtext.ScrolledText(lbl_06, width=48, height=9)
        self.txt_log.place(x=1,y=1)
         
        lbl_07 = Label(frm_ctrls, text='Comando:')
        lbl_07.place(x=10,y=295,width=60,height=20)
         
        self.ent_cmd = Entry(frm_ctrls, width=25)
        self.ent_cmd.place(x=80,y=295,width=294,height=20)       
        self.ent_cmd.bind('<Return>', self.comp_s)
         
        self.btn_send_cmd = Button(frm_ctrls, text='Enviar')
        self.btn_send_cmd.place(x=376,y=294,width=50,height=22)  
        self.btn_send_cmd['command'] = self.send_cmd
        
        #---nome do frame---------------------
        frm_inic = Labelframe(self, text='Tamanho Matriz')
        frm_inic.place(x=10,y=90,width=215,height=75)
        
        frm_inic.columnconfigure(0, pad=3)
        frm_inic.columnconfigure(1, pad=3)
        frm_inic.columnconfigure(2, pad=3)
        frm_inic.columnconfigure(3, pad=3)
        
        frm_inic.rowconfigure(0, pad=3)
        frm_inic.rowconfigure(1, pad=3)
        
        #---valores da matriz-----------------
        lbl_08 = Label(frm_inic, text='X :')
        lbl_08.grid(row=0, column=0)
        
        self.var_matriz_x=Entry(frm_inic, width=12)
        self.var_matriz_x.insert(END, '%d' % self.rows)
        self.var_matriz_x.grid(row=0, column=1)
        
        lbl_9 = Label(frm_inic, text='Y :')
        lbl_9.grid(row=0, column=2)
        
        self.var_matriz_y=Entry(frm_inic, width=12)
        self.var_matriz_y.insert(END, '%d' % self.cols)
        self.var_matriz_y.grid(row=0, column=3)
        
        #---botão de atualizar----------------
        
        btn_matriz_refresh = Button(frm_inic, text='Atualizar')
        btn_matriz_refresh.place(x=20,y=25,width=181,height=25)
        btn_matriz_refresh['command'] = self.att_matriz
        
        #---nome do frame---------------------
        frm_param = Labelframe(self, text='Parametros')
        frm_param.place(x=235,y=90,width=215,height=225)
        
        frm_param.columnconfigure(0, pad=3)
        frm_param.columnconfigure(1, pad=3)
        
        frm_param.rowconfigure(0, pad=3)
        frm_param.rowconfigure(1, pad=3)
        frm_param.rowconfigure(2, pad=3)
        frm_param.rowconfigure(3, pad=3)
        
        lbl_par_1 = Label(frm_param, text='Possição Ponto 1 (cm):')
        lbl_par_2 = Label(frm_param, text='Possição Ponto 2 (cm):')
        lbl_par_3 = Label(frm_param, text='Passo eixo X (mm):')
        lbl_par_4 = Label(frm_param, text='Passo eixo Y (mm):')
        self.lbl_par_5 = Label(frm_param, text='00,00 00,00')
        self.lbl_par_6 = Label(frm_param, text='00,00 00,00')
        self.lbl_par_7 = Label(frm_param, text='0,0000')
        self.lbl_par_8 = Label(frm_param, text='0,0000')
        
        lbl_par_1.grid(row=0, column=0, sticky=W)
        lbl_par_2.grid(row=1, column=0, sticky=W)
        lbl_par_3.grid(row=2, column=0, sticky=W)
        lbl_par_4.grid(row=3, column=0, sticky=W)
        self.lbl_par_5.grid(row=0, column=1, sticky=E)
        self.lbl_par_6.grid(row=1, column=1, sticky=E)
        self.lbl_par_7.grid(row=2, column=1, sticky=E)
        self.lbl_par_8.grid(row=3, column=1, sticky=E)
        
        #---nome do frame---------------------
        frm_progress = Labelframe(self)
        frm_progress.place(x=460,y=660,width=608,height=45)
        
        #---tempo de progresso----------------
        #chama função determina tempo max
        
        lbl_10 = Label(frm_progress, text='Tempo estimado de '+'HH'+' : '+'MM'+' : '+'SS')
        lbl_10.place(x=10,y=0,width=300,height=20)
        
        #---barra de progresso----------------
        self.var_pb=DoubleVar()
        self.var_pb.set(1)
        #chamaria uma função de definição da barra
        
        pb=Progressbar(frm_progress,variable=self.var_pb,maximum=100)
        pb.place(x=200,y=0,width=397,height=20)
        
        #---nome do frame---------------------
        frm_04 = Labelframe(self, text='Arquivo')
        frm_04.place(x=460,y=10,width=608,height=47)
        
        frm_inic.columnconfigure(0, pad=3)
        frm_inic.columnconfigure(1, pad=3)
        frm_inic.columnconfigure(2, pad=3)
        frm_inic.columnconfigure(3, pad=3)
        
        frm_inic.rowconfigure(0, pad=3)
        
        lbl_11 = Label(frm_04, text='  Nome do Arquivo:  ')
        lbl_11.grid(row=0, column=0)
        
        self.str_save = Entry(frm_04, width=41)
        self.str_save.grid(row=0, column=1)
        
        lbl_12 = Label(frm_04, text=' _dd-mm-yyyy_HH-MM.xlsx ')
        lbl_12.grid(row=0, column=2)
        
        btn_save = Button(frm_04, text='Salvar')
        btn_save.grid(row=0,column=3)
        btn_save['command'] = self.save
        
        #---nome do frame---------------------
        #futuramente aplicara função de pontos iniciais
        frm_pont = Labelframe(self, text='Definição dos pontos')
        frm_pont.place(x=10,y=165,width=215,height=75)
        
        btn_pont_start = Button(frm_pont, text='Ponto 1')
        btn_pont_start.place(x=5,y=1,width=100,height=50)
        btn_pont_start['command'] = self.start_point
        
        btn_pont_end = Button(frm_pont, text='Ponto 2')
        btn_pont_end.place(x=110,y=1,width=95,height=50)
        btn_pont_end['command'] = self.end_point
        
        #---nome do frame---------------------
        frm_freq = Labelframe(self, text='Frequência')
        frm_freq.place(x=10,y=240,width=215,height=75)
        
        frm_freq.columnconfigure(0, pad=3)
        frm_freq.columnconfigure(1, pad=3)
        frm_freq.columnconfigure(2, pad=3)
        
        frm_freq.rowconfigure(0, pad=3)
        frm_freq.rowconfigure(1, pad=3)
        
        #---valores da matriz-----------------
        lbl_08 = Label(frm_freq, text='Frequência:')
        lbl_08.grid(row=0, column=0)
        
        self.var_freq=Entry(frm_freq, width=12)
        self.var_freq.insert(END, '%d' % 300)
        self.var_freq.grid(row=0, column=1)
        
        self.cmb_freq = Combobox(frm_freq, width=5)
        self.cmb_freq.grid(row=0, column=2)
        self.cmb_freq['values'] = ['GHz','MHz','KHz']
        self.cmb_freq.current(1)
        
        self.btn_freq_refresh = Button(frm_freq, text='Atualizar')
        self.btn_freq_refresh.place(x=68,y=25,width=136,height=25)
        self.btn_freq_refresh['command'] = self.att_freq
        
        #---botão origem-----------------
        btn_origin = Button(self, text='Parar Medição')
        btn_origin.place(x=10,y=320,width=215,height=45)
        btn_origin['command'] = self.stop_meas
        
        btn_start = Button(self, text='Inicia Medição')
        btn_start.place(x=235,y=320,width=215,height=45)
        btn_start['command'] = self.measurement
        
        #---constantes e inicializações-------
        self.list_serial()
        self.att_matriz()
        self.att_freq()
    
    def cnc_jog(self, jog_cmd_string):
        if not (self.flag_medindo):
            step = self.cmb_step.get()
        else:
            if ('X' in jog_cmd_string): #verifica se movimento na medida é no eixo x
                step=self.var_step_x
            else:
                step=self.var_step_y
            
        jog_cmd_string = jog_cmd_string.replace('%', str(step))        
        print(jog_cmd_string)
        
        if (self.serial_cnc != None):
            if (self.serial_cnc.is_open):
                cmd = str(jog_cmd_string + '\n').encode()
                self.serial_cnc.write(cmd)
                
                data = self.serial_cnc.read_until('ok\n\r')
                self.txt_log.insert(END,data)
                
                self.txt_log.see(END)
                
    
    def comp_s(self, event):
        self.send_cmd()
        

    def list_serial(self):         
        ports = serial.tools.list_ports.comports()
        
        print('Detected serial ports:')
        for i in ports:
            print(str(i))
        
        self.cmb_analyzer['values'] = ports
        self.cmb_analyzer.set('Escolha...')
        
        self.cmb_cnc['values'] = ports
        self.cmb_cnc.set('Escolha...')
        
        
    def send_cmd(self):
        if (self.serial_cnc != None):
            if (self.serial_cnc.is_open): 
                cmd = str(self.ent_cmd.get() + '\n').encode()
                self.serial_cnc.write(cmd)
                
                data = self.serial_cnc.read_until('ok')
                self.txt_log.insert(END,data)
                
                self.txt_log.see(END)
            
                
    def open_serial_cnc(self):        
        
        com_port = self.cmb_cnc.get()        
        com_port = com_port.split()
        
        if (self.serial_cnc != None):
            if (self.serial_cnc.is_open):
                self.serial_cnc.close()
                self.btn_open_cnc['text'] = 'Abrir'
                print('Fechando: ' + com_port[0])
                self.serial_cnc = None
        else:
            try:
                self.serial_cnc = serial.Serial(com_port[0], 115200, timeout=0.5)
                self.btn_open_cnc['text'] = 'Fechar'
                print('Abrindo: ' + com_port[0])
            
            except Exception as e:
                sys.stderr.write('--- ERROR opening new port: {} ---\n'.format(e))
                # new_serial.close()
    
    def start_point(self):
        xyz=self.possicao_atual()
        self.start_point_x=float(xyz[0])
        self.start_point_y=float(xyz[1])
        
        self.lbl_par_5.config(text=(("%.2f %.2f" % (self.start_point_x/10, self.start_point_y/10)).replace('.',',')))
        self.atualiza_passo()
        
    def end_point(self):#da pra melhorar juntado star_point com end_point passando pra função se é start ou end
        xyz=self.possicao_atual()
        self.end_point_x=float(xyz[0])
        self.end_point_y=float(xyz[1])
        
        self.lbl_par_6.config(text=(("%.2f %.2f" % (self.end_point_x/10, self.end_point_y/10)).replace('.',',')))
        self.atualiza_passo()
        
    def atualiza_passo(self):
        try:
            #passo eixo x
            self.var_step_x=abs(self.start_point_x-self.end_point_x)/self.cols
            print("xlinha="+str(self.var_step_x))
            self.lbl_par_7.config(text=(("%.4f" % (self.var_step_x)).replace('.',',')))
            #passo eixo y
            self.var_step_y=abs(self.start_point_y-self.end_point_y)/self.rows
            print("ylinha="+str(self.var_step_y))
            self.lbl_par_8.config(text=(("%.4f" % (self.var_step_y)).replace('.',',')))
        except AttributeError:
            return
        
    def possicao_atual(self):
        if (self.serial_cnc != None):
            if (self.serial_cnc.is_open):
                cmd = str('?\n').encode()
                self.serial_cnc.write(cmd)      
                data = str(self.serial_cnc.read_until('ok'))
                try:
                    start = data.index( "|MPos:" ) + len( "|MPos:" )
                    end = data.index( '|', start )
                    return data[start:end].split(',')
                except ValueError:
                    return ['0.000', '0.000', '0.000']
        else:
            return ['0.000', '0.000', '0.000']
        
    def stop_meas(self):
        print("stop_meas")
        if(self.flag_medindo):
            #envia para o arduino parar
            self.flag_stop=True
            
        
    def att_matriz(self):
        
        valor_x = self.var_matriz_x.get()
        valor_y = self.var_matriz_y.get()
        
        #tratamento do valor de entrada
        if not(valor_x.isdigit() and valor_y.isdigit()):
            messagebox.showwarning(title="Erro nos valores X e Y", message="X e Y deve ser um numero decimal maior que zero\n ")
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
        
        self.frm_tabela = Frame(self, relief=RIDGE)
        self.frm_tabela.place(x=460,y=65,width=608,height=595)
        
        # Create a frame for the canvas and scrollbar(s).
        self.frame2 = Frame(self.frm_tabela)
        self.frame2.grid(row=3, column=0, sticky=NW)
        
        # Add a canvas in that frame.
        self.canvas = Canvas(self.frame2)
        self.canvas.grid(row=0, column=0)
        
        # Create a vertical scrollbar linked to the canvas.
        vsbar = Scrollbar(self.frame2, orient=VERTICAL, command=self.canvas.yview)
        vsbar.grid(row=0, column=1, sticky=NS)
        self.canvas.configure(yscrollcommand=vsbar.set)
        
        # Create a horizontal scrollbar linked to the canvas.
        hsbar = Scrollbar(self.frame2, orient=HORIZONTAL, command=self.canvas.xview)
        hsbar.grid(row=1, column=0, sticky=EW)
        self.canvas.configure(xscrollcommand=hsbar.set)

        # Create a frame on the canvas to contain the buttons.
        self.buttons_frame = Frame(self.canvas)
        
        #creat matrix for buttons
        self.button_matriz = [[None for _ in range(int(valor_x))] for _ in range(int(valor_y))]
        #print("button_matriz["+valor_y+"]["+valor_x+"]=")
        #print(self.button_matriz)
        
        # Add the buttons to the frame.
        for i in range(0, int(valor_y)):
            for j in range(0, int(valor_x)):
                self.button_matriz[i][j] = Button(self.buttons_frame, text="m[%d,%d]\nx=%d\ny=%d" % (int(valor_x), int(valor_y),j+1,i+1))
                self.button_matriz[i][j].grid(row=i, column=j)
        
        # Create canvas window to hold the buttons_frame.
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
        
    def att_freq(self):
        freq = self.var_freq.get()
        if not (freq.isdigit()):
            messagebox.showwarning(title="Erro nos valor de Frequência",
                                   message="Frequência deve ser um numero decimal maior que zero\n ")
            return
        if(int(freq)==0):
            messagebox.showwarning(title="Erro nos valor de Frequência",
                                   message="Frequência deve ser um numero decimal maior que zero\n ")
            return
        if(self.cmb_freq.get()=="KHz"):
            freq=int(freq)*pow(10, 3)
        elif(self.cmb_freq.get()=="MHz"):
            freq=int(freq)*pow(10, 6)
        else:
            freq=int(freq)*pow(10, 9)
        #try: #verificar se analisador está conectado
        print('SYST:MODE RMOD')#ativa modo reciver
        print("RMOD:FREQ {}.format("+ str(freq) +")")#define frequencia do modo reciver
    
    def measurement(self):
        #manda pro ponto inicial (canto superior esquerdo)
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
        
        #manda pro ponto inicial
        xyz=self.possicao_atual()
        #eixo x
        x= x-float(xyz[0])
        print("movimento x="+str(x))
        if(x>0):arg=self.dict_jog['left']
        elif(x<0):arg=self.dict_jog['right']
        aux=self.var_step_x
        self.var_step_x=abs(x)
        self.cnc_jog(arg)
        self.var_step_x=aux
        #colocar delay
        #eixo y
        y=y-float(xyz[1])
        print("movimento y="+str(y))
        if(y>0):arg=self.dict_jog['up']
        elif(y<0):arg=self.dict_jog['down']
        aux=self.var_step_y
        self.var_step_y=abs(y)
        self.cnc_jog(arg)
        self.var_step_y=aux
        #colocar delay
        
        self.matrix_meas = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        var_progressbar=0
        self.var_pb.set(var_progressbar)
        step_progressbar=100/((self.rows)*(self.cols))
        
        flag_ordem=True #false=esquerda pra direita
        for i in range(0, self.rows):#linha
            if(flag_ordem):
                for j in range(0, self.cols):#coluna
                    self.matrix_meas[i][j]=99# entra valor medido
                    self.button_matriz[i][j].config(text="meas+\nx=%d\ny=%d" % (j+1, i+1))
                    var_progressbar=var_progressbar+step_progressbar
                    self.var_pb.set(var_progressbar)
                    self.master.update()
                    print("Mede")
                    if(j+1<self.cols):
                        time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                        arg=self.dict_jog['right']
                        self.cnc_jog(arg)
                flag_ordem=False
            else:
                for j in reversed(range(0,self.cols)):#coluna
                    self.matrix_meas[i][j]=98# entra valor medido
                    self.button_matriz[i][j].config(text="meas-\nx=%d\ny=%d" % (j+1, i+1))
                    var_progressbar=var_progressbar+step_progressbar
                    self.var_pb.set(var_progressbar)
                    self.master.update()
                    print ("Mede")
                    if(j!=0):
                        time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                        arg=self.dict_jog['left']
                        self.cnc_jog(arg)
                flag_ordem=True
            if(i+1<self.rows):
                time.sleep(self.tempo_entre_medidas) #pra teste da tela atualizando
                arg=self.dict_jog['down']
                self.cnc_jog(arg)
                
        self.flag_medindo=False
    def save(self):
        try:
            self.meas_time.strftime("_%d-%m-%Y_%H-%M")
            file_path=(filedialog.askdirectory()+'\\'+self.str_save.get()+self.meas_time.strftime("_%d-%m-%Y_%H-%M")+".xlsx")
            wb = openpyxl.Workbook()
            sheet = wb.active
            for i in range(1, self.rows+1):
                for j in range(1, self.cols+1):
                    celula = sheet.cell(row=i, column=j)
                    celula.value = self.matrix_meas[i-1][j-1]
                    #no futuro se necessário adicionar formatação da celula para numerica
            wb.save(file_path)
        except AttributeError:
            messagebox.showwarning(title="Erro!!!Medida não realizada", message="Nenhuma informação para salvar ")
        
def main():
    #---Gera janela-----------------------
    root = Tk()
    root.geometry('1080x720')
    root.resizable(0, 0) 
    #---icone da janela-------------------
    #icone = PhotoImage(file = 'labcem_icone.png') 
    #root.iconphoto(False, icone) 
    #-------------------------------------
    app = main_window()
    root.mainloop()

if __name__ == '__main__':
    main()