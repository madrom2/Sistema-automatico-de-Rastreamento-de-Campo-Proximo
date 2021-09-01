import time
import serial.tools.list_ports
import sys

class controle_cnc:
    
    #Função que retorna portas COM seriais disponiveis
    def list_serial():         
        ports = serial.tools.list_ports.comports()
        
        print('Detected serial ports:')
        for i in ports:
            print(str(i))
        
        #retorna string de portas COM conectadas
        return ports 
    
    #Função de abertura de porta COM serial
    def open_serial_cnc(com_port, serial_cnc):      
        com_port = com_port.split() #retira valor da 'COMx'
        
        if (serial_cnc != None):    #se já tiver com aberta fecha ela
            if (serial_cnc.is_open):
                serial_cnc.close()
                print('Fechando: ' + com_port[0])
                return None
        else:
            try:
                serial_cnc = serial.Serial(com_port[0], 115200, timeout=0.5)
                print('Abrindo: ' + com_port[0])
                while(True):#loop para destravar a maquina para não precisar delay
                    if(len(controle_cnc.send_cmd('$X',serial_cnc).decode())>0):
                        controle_cnc.send_cmd('$X',serial_cnc).decode()
                        break
                
                return serial_cnc        #retorna porta aberta
            
            except Exception as e:
                pass
                sys.stderr.write('--- ERROR opening new port: {} ---\n'.format(e))
    
    #Função de jog
    def cnc_jog(jog_cmd_string, serial_cnc):
        if (serial_cnc != None):
            if (serial_cnc.is_open):
                cmd = str(jog_cmd_string + '\n').encode()
                serial_cnc.write(cmd)
                
                data = serial_cnc.read_until('ok\n\r')
                
                return (data)
    
    #Função de envia comando 
    def send_cmd(str_cmd, serial_cnc):
        if (serial_cnc != None):
            if (serial_cnc.is_open):
                cmd = str(str_cmd+'\n').encode()
                serial_cnc.write(cmd)
                
                data = serial_cnc.read_until('ok')
                return (data)
    
    #Função que retorna possição futura da maquina
    def current_pos(serial_cnc):
        if (serial_cnc != None):
            if (serial_cnc.is_open):
                #Envia comando de pergunta de possição da maquina
                cmd = str('?\n').encode()
                serial_cnc.write(cmd)      
                data = serial_cnc.read_until('ok').decode()
                try:
                    #Seleciona parte da string e sapara em possição X, Y e Z
                    start = data.index( "|MPos:" ) + len( "|MPos:" )
                    end = data.index( '|', start )
                    return data[start:end].split(',')
                except ValueError:
                    #Caso leitura do comando "?" não retorne possição atual
                    return ['0.000', '0.000', '0.000']
        else:
            #Caso não tenha conectador o arduino/grbl
            return ['0.000', '0.000', '0.000']
    
    #Função que retorna o estado da maquina
    def estado_atual(serial_cnc):
        if (serial_cnc != None):
            if (serial_cnc.is_open):
                #Envia comando de pergunta o estado da maquina
                cmd = str('?\n').encode()
                serial_cnc.write(cmd)      
                data = serial_cnc.read_until('ok').decode()
                try:
                    #Seleciona parte da string e sapara estado
                    end = data.index( '|', 1 )
                    print(data[1:end])
                    return data[1:end]
                except ValueError:
                    #Caso leitura do comando "?" não retorne estado atual
                    return 
        else:
            #Caso não tenha conectador o arduino/grbl
            return