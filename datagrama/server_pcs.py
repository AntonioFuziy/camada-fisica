import server_functions
from enlace import *
import time
import libscrc

serialName2 = "COM10"

eop = "\xff\xaa\xff\xaa"

erro = 44
sucesso = 33

def main():
    loop = True
    cont = 1
    try:
        server_functions.clear_log()

        com2 = enlace(serialName2)

        com2.enable()

        handshake_server_msg = "na escuta"
        first_server_payload = str.encode(handshake_server_msg)

        while com2.rx.getIsEmpty():
            print("-------------------------")
            print("Esperando o client...")
            time.sleep(0.5)
        
        head_handshake = com2.getHead()
        handshake = com2.rx.getNData(20)
        eop_handshake = com2.getEop()
        client_request = head_handshake + handshake + eop_handshake
        server_functions.check_eop(eop_handshake)
        
        server_functions.write_log("recebido", client_request)

        print("-------------------------")
        print("head do handshake recebido")
        print(head_handshake)

        print("-------------------------")
        print("mensagem recebida")
        print(handshake)
        
        if handshake == b"quero falar com voce":
            print("-------------------------") 
            print("handshake correto")
            
            server_response = server_functions.define_package(handshake_server_msg, 2, first_server_payload, 1, erro, sucesso)
            com2.sendData(server_response)
            
            server_functions.write_log("envio", server_response)
        else:
            print("-------------------------")
            print("handshake errado")
            quit()

        while com2.rx.getIsEmpty():
            print("esperando client entrar em contato")
            time.sleep(0.5)

        while loop:
            quit_time = time.time()

            while com2.rx.getIsEmpty():
                print("esperando client enviar pacote")
                time.sleep(0.5)

                time_quit = time.time() - quit_time

                if time_quit >= 20:
                    print("-------------------------")
                    print("Nenhum pacote recebido")
                    t5_data = server_functions.define_package("", 5, str.encode(""), 1, erro, sucesso)
                    print(t5_data)
                    server_functions.write_log("envio", t5_data)
                    com1.sendData(t5_data)
                    quit_time = time.time()
                    quit()

            t3_head = com2.getHead()
            print("-------------------------")
            print("head recebido")
            print(t3_head)
            
            package_number_t3 = t3_head[4]

            #forcando erro
            #if t3_head[4] == 2:
            #    package_number_t3 = t3_head[4]+1

            if t3_head[0] == 5:
                print("-------------------------")
                print("erro de timeout")

                t3_eop = com2.getEop()
                server_functions.check_eop(t3_eop)
                print("-------------------------")
                print("eop recebido")
                print(t3_eop)

                client_package = t3_head + t3_eop
                
                server_functions.write_log("recebido", client_package)
                quit()

            elif t3_head[4] != package_number_t3:
                print("-------------------------")
                print("erro no número do pacote")
                print("-------------------------")
                print("o pacote correto deveria ser o número {} e foi enviado o número {}".format(t3_head[4], package_number_t3))
                t6_package = server_functions.define_package("", 6, str.encode(""), cont, erro, sucesso)
                com2.sendData(t6_package)
                server_functions.write_log("envio", t6_package)
                quit()

            else:
                t3_payload = com2.rx.getNData(t3_head[5])
                print("-------------------------")
                print("payload recebido")
                print(t3_payload)

            t3_eop = com2.getEop()
            server_functions.check_eop(t3_eop)
            print("-------------------------")
            print("eop recebido")
            print(t3_eop)

            client_package = t3_head + t3_payload + t3_eop


            crc16_confirmation = libscrc.ibm(t3_payload)
            print("CRC convertion: {}".format(crc16_confirmation))

            crc16bytes = server_functions.transform_ints(crc16_confirmation)
            print("CRC bytes: {}".format(crc16bytes))
            print("CRC byte 0: {}".format(crc16bytes[0].to_bytes(1, byteorder="big")))
            print("CRC byte 1: {}".format(crc16bytes[1].to_bytes(1, byteorder="big")))

            if client_package[8] == crc16bytes[0] and client_package[9] == crc16bytes[1]:
                print(client_package[8])
                print(client_package[9])
                print("-------------------------")
                print("CRC confirmado")
            
            
            server_functions.write_log("recebido", client_package)

            time.sleep(0.5)

            t4_package = server_functions.define_package("", 4, str.encode(""), cont, erro, sucesso)

            com2.sendData(t4_package)

            server_functions.write_log("envio", t4_package)

            time.sleep(0.5)

            if t3_head[3] == t3_head[4]:
                loop = False
            
            cont += 1

        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        print("SUCESSO server")
        server_functions.write_log("SUCESSO", [])
        com2.disable()

    except:
        print("-------------------------")
        print("ops! :-\\")
        com2.disable()

if __name__ == "__main__":
    main()