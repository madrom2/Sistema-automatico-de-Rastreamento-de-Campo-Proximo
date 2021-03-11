import time
import serial.tools.list_ports

class controle_cnc:
    #def __init__(self):
    #    pass
    
    def list_serial():         
        ports = serial.tools.list_ports.comports()
        
        print('Detected serial ports:')
        for i in ports:
            print(str(i))
        
        #retorna string de portas COM conectadas
        return ports 
    
    def open_serial_cnc(com_port, serial_cnc):      
        com_port = com_port.split()
        
        if (serial_cnc != None):
            if (serial_cnc.is_open):
                serial_cnc.close()
                print('Fechando: ' + com_port[0])
                return None
        else:
            try:
                serial_cnc = serial.Serial(com_port[0], 115200, timeout=0.5)
                print('Abrindo: ' + com_port[0])
                #retorna porta aberta
                return serial_cnc
            
            except Exception as e:
                sys.stderr.write('--- ERROR opening new port: {} ---\n'.format(e))
                #new_serial.close()#???? o que seria isso?
    
    def cnc_jog(jog_cmd_string, serial_cnc):
        if (serial_cnc != None):
            if (serial_cnc.is_open):
                cmd = str(jog_cmd_string + '\n').encode()
                serial_cnc.write(cmd)
                
                data = serial_cnc.read_until('ok\n\r')
                
                return (data)
    
    def send_cmd(str_cmd, serial_cnc):
        if (serial_cnc != None):
            if (serial_cnc.is_open):
                #
                cmd = str(str_cmd+'\n').encode()
                serial_cnc.write(cmd)
                
                data = serial_cnc.read_until('ok')
                return (data)
        
    def current_pos(serial_cnc):
        if (serial_cnc != None):
            if (serial_cnc.is_open):
                #Envia comando de pergunta de possição da maquina
                cmd = str('?\n').encode()
                serial_cnc.write(cmd)      
                data = str(serial_cnc.read_until('ok'))
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
    
    def go_home(serial_cnc):
        pass