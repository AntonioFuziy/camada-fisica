# -*- coding: utf-8 -*-

from enlace import *
import time
from tkinter import filedialog

serialName1 = "COM3"

global filename

def main():
    try:
        print("-------------------------")
        print("começando client")
        com1 = enlace(serialName1)
        print("-------------------------")
        print('declarou enlace')
    
        com1.enable()
        print("-------------------------")
        print('habilitou com')
        
        filename = filedialog.askopenfilename()
       
        imageR = filename
        
        t_inicial = time.clock()

        txBuffer = open(imageR, 'rb').read()
       
        print(len(txBuffer))

        com1.sendData(txBuffer)
        print('enviou')

        while com1.rx.getBufferLen() == 0:
            print("-------------------------")
            print("Esperando resposta do server...")
        
        time.sleep(0.5)
        rxSize = com1.rx.getBufferLen()
        print(rxSize)
        print("-------------------------")
        print('tamanho do que recebido do server {}' .format(rxSize))

        print("-------------------------")
        print("Comunicação encerrada")
        
        com1.disable()

        time_send = time.clock() - t_inicial
        print("-------------------------")
        print("Tempo de envio: {} seg".format(time_send))

        bytes_per_second_send = com1.tx.getBufferLen()/time_send
        print("-------------------------")
        print("Bytes por segundo: {} B/s".format(bytes_per_second_send))

    except:
        print("-------------------------")
        print("ops! :-\\")
        com1.disable()

if __name__ == "__main__":
    main()