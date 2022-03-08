# -*- coding: utf-8 -*-

from enlace import *
import time

serialName2 = "COM10"

eop = [255, 255, 255, 255]

def transform_ints(data):
    entire_data = bytearray()
    for i in data:
        new_data_byte = (i).to_bytes(1, byteorder ='big')
        entire_data.append(new_data_byte[0])
    return entire_data

def pacote(head, payload, eop):
    package = head + payload + eop
    return package

def defining_handshake():
    head = [0, 0, 0, 0, 0, 0, 0, 0, 0 ,0]
    handshake_head = transform_ints(head)
    return handshake_head

def EOP():
    new_eop = transform_ints(eop)
    return new_eop

def main():
    try:
        com2 = enlace(serialName2)

        com2.enable()

        loop = True
        
        all_bytes_file = bytearray()
        
        delay_server = time.time()

        while com2.rx.getIsEmpty():
            print("-------------------------")
            print("Esperando o client...")
            time.sleep(0.5)

        client_handshake, len_client_handshake = com2.getData(14)
        print("handshake recebido")
        #print(client_handshake)
        time.sleep(1)

        server_handshake = defining_handshake()
        server_eop = EOP()
        
        entire_handshake = server_handshake + server_eop

        if client_handshake == entire_handshake:
            handshake = "handshake funcionando"
            handshake_bytes = str.encode(handshake)
            entire_handshake = server_handshake + handshake_bytes + server_eop
            com2.sendData(entire_handshake)
        else:
            handshake = "handshake fracassado "
            handshake_bytes = str.encode(handshake)
            entire_handshake = server_handshake + handshake_bytes + server_eop        
            com2.sendData(entire_handshake)

            print("-------------------------")
            print("handshake failed")
            quit()

        while loop:
            client_head, len_head = com2.getHead()
            print("-------------------------")
            print("Head recebido")
            print("-------------------------")
            #print(client_head)
            time.sleep(1)

            entire_head = [x for x in client_head]

            if entire_head[0] != com2.rx.getBufferLen():
                print("-------------------------")
                print("Número do pacote errado")
                failed_head = transform_ints(entire_head)
                failed_response = "Pacote {} com número errado".format(entire_head[1])
                failed_eop = b"\xff\xff\xff\xff"
                convert_response = str.encode(failed_response)
                com2.sendData(failed_head + convert_response + failed_eop)
                quit()

            print("-------------------------")
            print("Payload {} recebido com {} bytes".format(entire_head[1], entire_head[0]))
            payload, len_payload = com2.getData(entire_head[0])
            print("-------------------------")
            #print(payload)

            all_bytes_file += payload

            time.sleep(1)
            
            print("-------------------------")
            print("Eop recebido")
            eop, len_eop = com2.getEop()
            print("-------------------------")
            #print(eop)
            time.sleep(1)

            if eop != b"\xff\xff\xff\xff":
                print("eop com erro")
            
            #sucesso, pacote recebido
            entire_head[8] = 1
            success_head = transform_ints(entire_head)
            message_response = "Pacote recebido com sucesso"
            response_bytes = str.encode(message_response)

            response_to_client = success_head + response_bytes + eop

            com2.sendData(response_to_client)

            entire_head[6] -= 1
            entire_head[7] -= 1

            if entire_head[6] == -1:
                loop = False

        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        print("Sucesso ao receber arquivo")
        com2.disable()

    except:
        print("-------------------------")
        print("ops! :-\\")
        com2.disable()

if __name__ == "__main__":
    main()