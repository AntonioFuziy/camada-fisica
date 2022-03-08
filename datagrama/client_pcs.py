import client_functions

from enlace import *
import time
from tkinter import filedialog
import binascii
import math
import libscrc

serialName1 = "COM3"

eop = b"\xff\xaa\xff\xaa"

erro = 44
sucesso = 33

def main():
    try:
        client_functions.clear_log()

        com1 = enlace(serialName1)
        
        com1.enable()

        fileRead = "./code.png"
        arquivo = bytearray(open(fileRead, "rb").read())
        print("-------------------------")
        print("Seu arquivo contém {} bytes".format(len(arquivo)))
        time.sleep(1)

        handshake_client_msg = "quero falar com voce"
        first_client_payload = str.encode(handshake_client_msg)

        entire_handshake = client_functions.define_package(handshake_client_msg, 1, first_client_payload, 1, erro, sucesso)
        
        print("-------------------------")
        print("enviando handshake")
        com1.sendData(entire_handshake)
        client_functions.write_log("envio", entire_handshake)
        waiting_time = time.time()
        
        while com1.rx.getIsEmpty():
            total_time = time.time() - waiting_time
            if total_time >= 5:
                print("-------------------------")
                print("Reenviando...")
                client_functions.write_log("envio", entire_handshake)
                com1.sendData(entire_handshake)
                waiting_time = time.time()

            print("-------------------------")
            print("Esperando o server responder...")
            time.sleep(0.5)

        head_handshake = com1.getHead()
        server_response = com1.rx.getNData(9)
        eop_handshake = com1.getEop()
        response_package = head_handshake + server_response + eop_handshake
        client_functions.check_eop(eop_handshake)
        
        if server_response == b"na escuta":
            print("-------------------------")
            print("mensagem recebida")
            client_functions.write_log("recebido", response_package)
        else:
            print("-------------------------")
            print("erro no handshake")
            client_functions.write_log("recebido", response_package)

        print(len(arquivo))
        len_package = math.ceil(len(arquivo)/114)

        for i in range(0, len_package):

            payload = arquivo[:114]
            del arquivo[:114]

            package = client_functions.define_package(arquivo, 3, payload, i+1, erro, sucesso)
            package[3] = len_package
            print("-------------------------")
            print("Pacote {}".format(i+1))
            print("-------------------------")
            print("enviando pacote...")
            
            time.sleep(0.5)
    
            crc16 = libscrc.ibm(payload)
            print("CRC convertion: {}".format(crc16))

            crc16bytes = client_functions.transform_ints(crc16)
            print("CRC bytes: {}".format(crc16bytes))
            print("CRC byte 0: {}".format(crc16bytes[0].to_bytes(1, byteorder="big")))
            print("CRC byte 1: {}".format(crc16bytes[1].to_bytes(1, byteorder="big")))

            package[8] = crc16bytes[0]
            package[9] = crc16bytes[1]
            print(package[:10])
            
            com1.sendData(package)
            client_functions.write_log("envio", package)
            
            quit_time = time.time()
            waiting_time = time.time()

            while com1.rx.getIsEmpty():
                time_quit = time.time() - quit_time
                total_time = time.time() - waiting_time

                if total_time >= 5:
                    print("-------------------------")
                    print("Reenviando...")
                    client_functions.write_log("envio", package)
                    com1.sendData(package)
                    waiting_time = time.time()

                if time_quit >= 20:
                    print("-------------------------")
                    print("Erro de conexão com o server")
                    t5_data = client_functions.define_package("", 5, str.encode(""), 1, erro, sucesso)
                    print(t5_data)
                    client_functions.write_log("envio", t5_data)
                    com1.sendData(t5_data)
                    quit_time = time.time()
                    quit()

            time.sleep(1)

            t4_head = com1.getHead()

            if t4_head[0] == 5:
                print("-------------------------")
                print("erro de timeout")

                server_package = t4_head + eop
                
                client_functions.write_log("recebido", server_package)
                quit()
            
            elif t4_head[0] == 6:
                print("-------------------------")
                print("erro no número do pacote")
                server_package = t4_head + eop
                print(server_package)
                client_functions.write_log("recebido", server_package)
                quit()


            t4_eop = com1.getEop()
            response_t4 = t4_head + t4_eop
            client_functions.check_eop(t4_eop)

            client_functions.write_log("recebido", response_t4)
            print("-------------------------")
            print(t4_head[4])
        
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        print("SUCESSO client")
        client_functions.write_log("SUCESSO", [])
        com1.disable()
        
    except:
        print("-------------------------")
        print("ops! :-\\")
        com1.disable()

if __name__ == "__main__":
    main()