import math
import datetime

eop = b"\xff\xaa\xff\xaa"

def transform_ints(data):
    new_data_byte = (data).to_bytes(2, byteorder ='big')
    return new_data_byte

def define_package(information, tipo, payload, index, erro, sucesso):
    sensor_id = 11
    server_id = 22
    id_arquivo = 10
    number_of_packages = math.ceil(len(information)/114)
    package_number = index

    if tipo == 1:
        head = bytearray([tipo, sensor_id, server_id, number_of_packages, package_number, id_arquivo, erro, sucesso, 0, 0])
    elif tipo == 2:
        head = bytearray([tipo, sensor_id, server_id, number_of_packages, package_number, id_arquivo, erro, sucesso, 0, 0])
    elif tipo == 3:
        head = bytearray([tipo, sensor_id, server_id, number_of_packages, package_number, len(payload), erro, sucesso, 0, 0])
    elif tipo == 4:
        head = bytearray([tipo, sensor_id, server_id, number_of_packages, package_number, id_arquivo, erro, sucesso, 0, 0])
    elif tipo == 5:
        head = bytearray([tipo, sensor_id, server_id, number_of_packages, package_number, id_arquivo, erro, sucesso, 0, 0])
    elif tipo == 6:
        head = bytearray([tipo, sensor_id, server_id, number_of_packages, package_number, id_arquivo, erro, sucesso, 0, 0])
    
    pacote = head + payload + eop

    return pacote

def EOP():
    new_eop = transform_ints(eop)
    return new_eop

def pacote(head, payload, eop):
    package = head + payload + eop
    return package

def clear_log():
    with open("Client3.txt", "w") as file:
        file.write("")

def write_log(send_receive, package):
    with open("Client3.txt", "a+") as file:
        file.write("\n")
        file.write("-------------------------")
        file.write("\n")
        file.write("{}".format(datetime.datetime.now()))
        file.write(" /")
        file.write(send_receive)
        file.write(" /")
        file.write("{}".format(package[0]))
        file.write(" /")
        file.write("{}".format(len(package)))
        if package[0] == 3:
            file.write(" /")
            file.write("{}".format(package[4]))
            file.write(" /")
            file.write("{}".format(package[3]))
            file.write(" /")
            file.write("{}".format(package[8].to_bytes(1, byteorder="big")+package[9].to_bytes(1, byteorder="big")))

def check_eop(eop):
    if eop != b"\xff\xaa\xff\xaa":
        print("-------------------------")
        print("eop incorreto")
        