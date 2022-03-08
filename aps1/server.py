# -*- coding: utf-8 -*-

from enlace import *
import time

serialName2 = "COM10"

def main():
    try:
        print("-------------------------")
        print("começando server")
        com2 = enlace(serialName2)
        print("-------------------------")
        print('declarou enlace')

        com2.enable()
        print("-------------------------")
        print('habilitou com')

        imageW = "./copy-code.png"

        while com2.rx.getBufferLen() == 0:
            print("-------------------------")
            print("Esperando client enviar o buffer...")

        t_inicial = time.clock()

        time.sleep(0.5)
        rxSize = com2.rx.getBufferLen()

        rxBuffer, nRx = com2.getData(rxSize)
        print("-------------------------")
        print('recebeu {} bytes de dados' .format(len(rxBuffer)))

        time.sleep(2)
        com2.sendData(rxBuffer)
        
        f = open(imageW, 'wb')
        f.write(rxBuffer)

        f.close()

        print("-------------------------")
        print("Comunicação encerrada")
        com2.disable()

        time_receive = time.clock() - t_inicial
        print("-------------------------")
        print("Tempo de recebimento: {} seg".format(time_receive))

        bytes_per_second_receive = len(rxBuffer)/time_receive
        print("-------------------------")
        print("Bytes por segundo: {} B/s".format(bytes_per_second_receive))

    except:
        print("-------------------------")
        print("ops! :-\\")
        com2.disable()

if __name__ == "__main__":
    main()