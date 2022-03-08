# -*- coding: utf-8 -*-

from enlace import *
import time
from tkinter import filedialog
import binascii
import math

serialName1 = "COM3"

global filename

eop = [255, 255, 255, 255]

def transform_ints(data):
    entire_data = bytearray()
    for i in data:
        new_data_byte = (i).to_bytes(1, byteorder ='big')
        entire_data.append(new_data_byte[0])
    return entire_data

def define_head(information):
    payload_len = 1
    number_of_payloads = math.ceil(len(information)/114)
    last_payload_size = len(information) - 114*(number_of_payloads-1)
    number_of_packages = math.ceil(len(information)/114)
    last_package_size = 14 + last_payload_size
    number_of_payloads_left = number_of_payloads 
    number_of_packages_left = number_of_packages
    package_number = 0
    
    head = [payload_len, package_number, number_of_payloads, last_payload_size, number_of_packages, last_package_size, number_of_payloads_left, number_of_packages_left, 0 ,0]
    
    return head

def data(head):
    data_head = transform_ints(head)
    return data_head

def message(head):
    message_head = transform_ints(head)
    return message_head

def handshake():
    head = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    handshake_head = transform_ints(head)
    return handshake_head

def EOP():
    new_eop = transform_ints(eop)
    return new_eop

def pacote(head, payload, eop):
    package = head + payload + eop
    return package

def main():
    try:
        com1 = enlace(serialName1)
        
        com1.enable()
        
        defining_handshake = handshake()
        
        handshake_eop = EOP()

        entire_handshake = defining_handshake + handshake_eop

        print("-------------------------")
        print("enviando handshake")
        com1.sendData(entire_handshake)
        waiting_time = time.time()
        
        while com1.rx.getIsEmpty():
            total_time = time.time() - waiting_time
            if total_time >= 5:
                print("-------------------------")
                resposta = str(input("Servidor inativo, deseja tentar novamente? S/N : "))
                if resposta == "S" or resposta == "s":
                    com1.sendData(entire_handshake)
                    waiting_time = time.time()
                    pass
                else:
                    quit()

            print("-------------------------")
            print("Esperando o server responder...")
            time.sleep(0.5)

        head_confirm, len_head_confirm = com1.getHead()
        confirm = com1.rx.getNData(21)
        eop_confirm, len_eop_confirm = com1.getEop()

        server_confirm = confirm.decode()

        print(total_time)

        if server_confirm == 'handshake funcionando':
            print("-------------------------")
            print("SUCCESS")
            print(server_confirm)
            time.sleep(1)
        else:
            print("-------------------------")
            print("FAILED")
            quit()

        fileRead = filedialog.askopenfilename()
        dado = bytearray(open(fileRead, "rb").read())
        print("-------------------------")
        print("Seu arquivo contém {} bytes".format(len(dado)))
        time.sleep(1)

        defining_head = define_head(dado)

        entire_head = data(defining_head)
        entire_eop = EOP()
            
        for i in range(0, entire_head[4]):
            payload = dado[:114]
            del dado[:114]

            defining_head[0] = len(payload)

            print("-------------------------")
            print("número do pacote: {}".format(defining_head[1]))
            print("número de pacotes faltando: {}".format(defining_head[6]))
            print("tamanho do payload atual: {}".format(defining_head[0]))
            time.sleep(1)
            
            defining_head[1] += 1
            defining_head[6] -= 1
            defining_head[7] -= 1

            entire_head = data(defining_head)

            #if i == 0:
            #    entire_message = pacote(entire_head, payload + b'\xf0', entire_eop)
                
            #else:
            entire_message = pacote(entire_head, payload, entire_eop)

            print("-------------------------")
            print("Pacote enviado:")     
            #print(entire_message)
            print(len(entire_message))
            print("-------------------------")
            com1.sendData(entire_message)
            time.sleep(1)
            
            head_response, len_head_response = com1.getHead()
            server_response, len_server_response = com1.getData(27)
            eop_response, len_eop_response = com1.getEop()

            if head_response[1] != entire_head[1]:
                print("-------------------------")
                print("O número do seu payload está incorreto")
                quit()

            if eop_response != entire_eop:
                print("-------------------------")
                print("Seu eop não foi enviado da forma correta para o server")
                quit()

            server_response = server_response.decode()
            print("-------------------------")
            print(server_response)
            time.sleep(1)

            if server_response == "Payload com tamanho errado ":
                print("-------------------------")
                print("Payload está com o tamanho incorreto")
                quit()


            if defining_head[6] == 0:
                print("-------------------------")
                print("Finalizando transmissão")
                time.sleep(1)
                break

            if server_response == 'Pacote recebido com sucesso':
                print("-------------------------")
                print("Enviando próximo pacote")
                print(server_response)
                
            else:
                print("-------------------------")
                print("FAILED")
                quit()

        
        print("-------------------------")
        print("Sucesso ao enviar seu arquivo")
        com1.disable()

    except:
        print("-------------------------")
        print("ops! :-\\")
        com1.disable()

if __name__ == "__main__":
    main()