import pyvisa
import serial

class controle_analisador:
    def open_visa_analisador(com_port, visa_analisador):
        if (visa_analisador == None):
            #retirar numero da COM 
            for i in range (len(com_port)):
                if com_port[i].isnumeric():
                    break
            com_port = com_port[i:int(com_port.find(' -'))]
            #Inicialização da COM
            rm = pyvisa.ResourceManager()
            #Se não tiver uma porta COM compativel instrumento retorna False
            #para apresentação de erro,  falta de drive
            if not any(str(com_port) in i for i in rm.list_resources()):
                return False
            else:
                try:
                    my_instrument = rm.open_resource('ASRL'+str(com_port)+'::INSTR')
                except Exception as e:
                    print(e)
                    my_instrument.close()
                    return None
                #inicialização do instrumento
                my_instrument.write('*RST;*CLS')     #reset no instrumento e limpa erro
                my_instrument.write('SYST:MODE RMOD')#ativa modo reciver
                
                return my_instrument
        else:
            visa_analisador.close()
            return None
        
    #Função de indentificação
    def identificação(visa_analisador):
        return visa_analisador.query('*IDN?')
        
    #Função definição da frequencia em Hz
    def receiver_frequencia(visa_analisador,freq):
        visa_analisador.write('RMOD:FREQ {}'.format(freq))
        
    #Função leitura da amplitude
    def receiver_amplitude(visa_analisador):
        return eval(visa_analisador.query('RMODe:LEV?').split(',')[1])
        
        