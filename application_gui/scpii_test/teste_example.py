#configura modo do analisador em reciver (mede faixa de freq)
from scpiinterface import Instrument, manager
MHz = 1000000
kHz = 1000

try:
    
    instrument = Instrument()
    
    instrument.activate_mode_receiver()
    instrument.receiver_set_step(100 * kHz)
    
    for freq in range(200*kHz,10*MHz,int(instrument.receiver_step)):
        # Set and read levels from 200kHz to 10MHz in receiver mode
        instrument.write('RMOD:FREQ {}'.format(freq))
        print(instrument.receiver_frequency)
        print(instrument.receiver_level)
        
        
    print(instrument.hello)
    
    instrument.close()

    
except (KeyboardInterrupt, Exception) as e:
    print("Something went wrong: " + str(e))
    try:
        instrument.close()
    except AttributeError:
        pass
    
    manager.close()