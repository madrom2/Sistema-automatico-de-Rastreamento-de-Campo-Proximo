import pyvisa
import time

#lista de recursos
manager = pyvisa.ResourceManager()
manager.list_resources()

#abrindo interface
print("Instrumento disponiveis")
print(manager.list_resources())
inst = manager.open_resource(manager.list_resources()[int(input("Digite o valor respectivamente ao instrumento:"))])

#inicialização/configuração comunicação
inst.write_termination = '\n'   #
#ins.read_termination = '\n'     #
inst.ext_clear_status()         #limpa estado

#identifição
print("Instrumento : " + inst.query("*IDN?"))
input("Enter para continuar...")

dict_comandos ={'1': ['*IDN?'],\
                '2': ['RMODe:LEV?'],\
                '3': ['RMOD:FREQ:STEP?'],\
                '4': ['SYST:MODE RMOD'],\
                '5': ['SYST:MODE SWE'],\
                '6': ['RMOD:FREQ:STEP 20000'],\
                '7': ['*IDN?'],\}

selecao=1
while(True):
    print("Digite o valor do comando desejado ..."+
          "1 - *IDN?                  identificação"+
          "2 - RMODe:LEV?             frequencia e amplitude"+
          "3 - RMOD:FREQ:STEP?        passo do modo reciver"+
          "4 - SYST:MODE RMOD         ativa modo reciver"+
          "5 - SYST:MODE SWE          ativa modo sweep"+
          "6 - RMOD:FREQ:STEP 20000   define frequencia ")
    
    selecao=input("Comando : ")
    if (selecao.isnumeric()):
        time.sleep(0.5) 
        try:
            if(selecao<4): #comando que necessita resposta
                #resposta = inst.query(dict_comandos[int(selecao-1)])
                print(inst.query(dict_comandos[int(selecao-1)]))
            else:          #comando que não necessita de resposta
                inst.write(dict_comandos[int(selecao-1)])
        except Exception as e:
            print(e)            
     else :
        print("Digite um numero!")

#fecha interface de comunicação
inst.close()