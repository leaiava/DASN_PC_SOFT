from serial_init import *
from config import *
from protocolo import *
import time 
import numpy as np
import logging
#import matplotlib
#from matplotlib import pyplot as plt

def receive_msg(Port, event="ff"):
    event_code = bytearray.fromhex("0000")
    cmp1 = bytearray.fromhex("04ff")
    cmp2 = bytearray.fromhex("040e")
    cmp3 = bytearray.fromhex("043e")
    while (event_code != cmp1) and (event_code != cmp2) and (event_code != cmp3):
        #time.sleep(0.1)
        logging.debug(f"IN: {Port.in_waiting} - OUT: {Port.out_waiting}")
        event_code = Port.read(2)
        logging.debug(f"event_code: {event_code} | event_code_length :{len(event_code)}")
        #time.sleep(0.1)
        logging.debug(f"IN: {Port.in_waiting} - OUT: {Port.out_waiting}")
        if len(event_code) < 2:
            return
        data_length = Port.read(1)
        logging.debug(f"data_length: {data_length}")
    if data_length == bytearray.fromhex(""):
        data_length = bytearray.fromhex("00")
    data = Port.read(int(data_length.hex(),16))
    logging.debug(f"data: {data}")
    return event_code.hex(" ") + " " + data_length.hex() + " " + data.hex(" ")

def msg_to_int(msg):
    CANTIDAD_DE_CANALES = 8
    OFFSET_PRIMER_CH = 42
    frame = ""
    for CH in range(CANTIDAD_DE_CANALES):
        offset_i = OFFSET_PRIMER_CH + (CH*9)
        offset_f = OFFSET_PRIMER_CH + (CH*9) + 8
        try:
            chData = int(msg[offset_i:offset_f].replace(" ","") , 16)
            if chData > int("7FFFFF",16):
                chData -= int("1000000",16)
            frame += ("," + str(chData))
        except:
            pass
    return frame

def main():
    logging.basicConfig( level=logging.INFO)
    logging.info("Iniciando DASN PC Soft")
    logging.info(serial_ports())
    logging.info("Plataforma: " + sys.platform )
    
    #seleccion de puerto serie
    puerto = serial_choose()
    #puerto = "/dev/ttyACM1"
    logging.info("Puerto serie elegido : " + puerto)

    #declaro el objeto de puerto serie (sin abrirlo)
    Port = serial.Serial()

    #parametros del puerto serie
    Port.port       = puerto
    Port.baudrate   = DEFAULT_BAURDATE
    Port.bytesize   = serial.EIGHTBITS      # number of bits per bytes # SEVENBITS
    Port.parity     = serial.PARITY_NONE    # set parity check: no parity # PARITY_ODD
    Port.stopbits   = serial.STOPBITS_ONE   # number of stop bits # STOPBITS_TWO
    Port.timeout    = 15

    try:
        Port.open()

    except Exception as e:
        logging.error("Error abriendo puerto serie.\n" + str(e) + '\nFin de programa.')
        exit()
    Port.flushInput()       # flush input buffer, discarding all its contents
    Port.flushOutput()      # flush output buffer, aborting current output
                            # and discard all that is in buffer
    logging.info("--- HCIExt_ResetSystemCmd ---")
    ba = bytearray.fromhex("01 1D FC 01 00") #HCIExt_ResetSystemCmd
    logging.info("Sending: %s",ba.hex(" "))
    Port.write(ba)
    time.sleep(1)
    if Port.in_waiting == 0: exit(1)
    while Port.in_waiting > 0:
        msg = receive_msg(Port)
        logging.info("Receiving: %s ", msg )
    
    logging.info("--- GAP_DeviceInit ---")
    ba = bytearray.fromhex("01 00 FE 26 08 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00")
    logging.info("Sending: %s ",ba.hex(" ")) # GAP_DeviceInit
    Port.write(ba)
    time.sleep(1)
    while Port.in_waiting > 0:
        msg = receive_msg(Port)
        logging.info("Receiving: %s ", msg)
    
    parameter_list = [ '15', '16', '1A','19']    
    for parameter in parameter_list:
        logging.info("--- GAP_GetParamValue ---")
        ba = bytearray.fromhex(f"01 31 FE 01 {parameter}")
        logging.info("Sending: %s ",ba.hex(" "))
        Port.write(ba)
        time.sleep(0.1)
        while Port.in_waiting > 0:
            msg = receive_msg(Port)
            logging.info("Receiving: %s ", msg)
        
    logging.info("--- GAP_DeviceDiscoveryRequest ---")
    ba = bytearray.fromhex("01 04 FE 03 03 01 00") #GAP_DeviceDiscoveryRequest
    logging.info("Sending: %s ",ba.hex(" "))
    Port.write(ba)
    time.sleep(1)
    while Port.in_waiting > 0:
        msg = "                "
        while msg[9:14] != "01 06":
            time.sleep(1)
            msg = receive_msg(Port)
            if msg == "": msg = "                "
            logging.info("Receiving: %s ", msg)

    logging.info("--- GAP_EstablishLinkRequest ---")
    ba = bytearray.fromhex("01 09 FE 09 00 00 00 FF 0F 6D F9 81 00") #Id de mi dispositivo
    logging.info("Sending: %s ",ba.hex(" "))
    Port.write(ba)
    time.sleep(1)
    while Port.in_waiting > 0:
        msg = receive_msg(Port)
        logging.info("Receiving: %s ", msg)
        time.sleep(3)
    
    ba = bytearray.fromhex("01 20 20 0E 00 00 06 00 06 00 00 00 0A 00 00 00 00 00")
    logging.info("Sending: %s ",ba.hex(" "))
    Port.write(ba)
    time.sleep(1)
    while Port.in_waiting > 0:
        msg = receive_msg(Port)
        logging.info("Receiving: %s ", msg)
    
    logging.info("-------------------GATT_DiscAllCharDescs------------------")
    ba = bytearray.fromhex("01 84 FD 06 00 00 01 00 FF FF")
    logging.info("Sending: %s ",ba.hex(" "))
    Port.write(ba)
    time.sleep(1)
    i=1
    msg = ""
    while msg != "04 ff 06 05 05 1a 00 00 00":
        msg = receive_msg(Port)
        logging.info(f"Receiving {i}: {msg}")
        i+=1
    # 
    # ADS1299_CMD_HOLA = 1,           //!<  1-Iniciar la comunicación.
    # ADS1299_CMD_OK,                 //!<  2-Se interpreto bien el comando recibido
    # ADS1299_CMD_NO_OK,              //!<  3-No se interpreto el comando recibido
    # ADS1299_CMD_CHAU,               //!<  4-Terminar comunicacion
    # ADS1299_CMD_CONFIG_INICIAR,     //!<  5-Inicia configuracion
    # ADS1299_CMD_CONFIG_TERMINAR,    //!<  6-Termina configuracion
    # ADS1299_CMD_CONFIG_CH_ALL_ON,   //!<  7-Todos los canales habilitados
    # ADS1299_CMD_CONFIG_CH_ALL_OFF,  //!<  8-Todos los canales deshabilitados
    # ADS1299_CMD_CONFIG_CH1_ON,      //!<  9-Canal 1 habilitdo
    # ADS1299_CMD_CONFIG_CH2_ON,      //!<  A-Canal 2 habilitdo
    # ADS1299_CMD_CONFIG_CH3_ON,      //!<  B-Canal 3 habilitdo
    # ADS1299_CMD_CONFIG_CH4_ON,      //!<  C-Canal 4 habilitdo
    # ADS1299_CMD_CONFIG_CH5_ON,      //!<  D-Canal 5 habilitdo
    # ADS1299_CMD_CONFIG_CH6_ON,      //!<  E-Canal 6 habilitdo
    # ADS1299_CMD_CONFIG_CH7_ON,      //!<  F-Canal 7 habilitdo
    # ADS1299_CMD_CONFIG_CH8_ON,      //!< 10-Canal 8 habilitdo
    # ADS1299_CMD_CONFIG_FREC_1,      //!< 11-Configura ADC con frecuencia 1 (16KHz)
    # ADS1299_CMD_CONFIG_FREC_2,      //!< 12-Configura ADC con frecuencia 2 ( 8KHz)
    # ADS1299_CMD_CONFIG_FREC_3,      //!< 13-Configura ADC con frecuencia 3 ( 4KHz)
    # ADS1299_CMD_CONFIG_FREC_4,      //!< 14-Configura ADC con frecuencia 4 ( 2KHz)
    # ADS1299_CMD_CONFIG_FREC_5,      //!< 15-Configura ADC con frecuencia 5 ( 1KHz)
    # ADS1299_CMD_CONFIG_FREC_6,      //!< 16-Configura ADC con frecuencia 6 (500Hz)
    # ADS1299_CMD_CONFIG_FREC_7,      //!< 17-Configura ADC con frecuencia 7 (250Hz)
    # ADS1299_CMD_ADQUIRIR,           //!< 18-Inicia la adquisición
    # ADS1299_CMD_PARAR,              //!< 19-Para la adquisición
    # ADS1299_CMD_OCUPADO,            //!< 1A-Respuesta si no puede atender un comando
    # ADS1299_CMD_LEER_ESTADO,        //!< 1B-Pregunta en que estado se encuentra
    # ADS1299_CMD_WAKE_UP,            //!< 1C-Sirve para actualizar la MEF interna del modulo
    # ADS1299_CMD_ZSIGNAL_ON,         //!< 1D-Inyecta la señal de impedancia
    # ADS1299_CMD_ZSIGNAL_OFF,        //!< 1E-Apaga la señal de impedancia
    # ADS1299_CMD_RESET,              //!< 1F
    
    parameter_list = [ '01', '1F', '01','05', '07', '1D', '17','06', '18' ]    
    #parameter_list = [ '01', '1F', '01', '05', '08', '09', '0A', '17', '06', '18' ]    
    #parameter_list = ['01', '05', '07', '16', '06', '18' ]    
    for parameter in parameter_list:
        logging.info("-------------------GATT_WriteCharValue------------------")
        ba = bytearray.fromhex(f"01 92 FD 05 00 00 20 00 {parameter}")
        logging.info("Sending: %s ",ba.hex(" "))
        Port.write(ba)
        time.sleep(0.5)
        while Port.in_waiting > 0:
            msg = receive_msg(Port)
            logging.info("Receiving: %s ", msg)

   # escribir en  ti/simplelink_cc2640r2_sdk_5_10_00_02/source/ti/ble5stack/icall/inc/ble_user_config.h -> #MAX_PDU_SIZE 255
    logging.info("GATT_ExchangeMTU")
    ba = bytearray.fromhex("01 82 FD 04 00 00 1E 00") # Le pido 0x1E canales, osea 30 porque el payload es eso -3.
    logging.info("Sending: %s ",ba.hex(" "))
    Port.write(ba)
    time.sleep(3)
    while Port.in_waiting > 0:
        msg = receive_msg(Port)
        logging.info("Receiving: %s ", msg)
    
    logging.info("-------------------GATT_WriteCharValue------------------")
    ba = bytearray.fromhex(f"01 92 FD 06 00 00 26 00 01 00")
    logging.info("Sending: %s ",ba.hex(" "))
    Port.write(ba)
    #time.sleep(1)
    while Port.in_waiting > 0:
        msg = receive_msg(Port)
        logging.info("Receiving: %s ", msg)
    
    start = time.monotonic()
    tiempo = 0
    DATA_FILE = 'data_8CH_7Hz.csv'
    secuencia = 0
    with open(DATA_FILE,"w",encoding="utf-8") as f: 
        while tiempo < 10:
            tiempo = time.monotonic()-start
            msg = receive_msg(Port)
            try:
                print(f"STATUS:{msg[33:41]} CH1:{msg[42:50]} CH2:{msg[51:59]} CH3:{msg[60:68]} CH4:{msg[69:77]} CH5:{msg[78:86]} CH6:{msg[87:95]} CH7:{msg[96:104]} CH8:{msg[105:113]} Time: {round(tiempo,3)} Buffer:{Port.in_waiting} Secuencia:{secuencia}")
            except:
                print("Error in data")
            secuencia += 1
            
            f.write(f"{round(tiempo,5)}{msg_to_int(msg)}\n")
            

    parameter_list = [ '19', '04' ]    
    for parameter in parameter_list:
        logging.info("-------------------GATT_WriteCharValue------------------")
        ba = bytearray.fromhex(f"01 92 FD 05 00 00 20 00 {parameter}")
        logging.info("Sending: %s ",ba.hex(" "))
        Port.write(ba)
        time.sleep(0.1)
        while Port.in_waiting > 0:
            msg = receive_msg(Port)
            logging.info("Receiving: %s ", msg)        

    logging.info("--- HCIExt_ResetSystemCmd ---")
    ba = bytearray.fromhex("01 1D FC 01 00") #HCIExt_ResetSystemCmd
    logging.info("Sending: %s",ba.hex(" "))
    Port.write(ba)
    time.sleep(1)
    while Port.in_waiting > 0:
        msg = receive_msg(Port)
        logging.info("Receiving: %s ", msg )
    
    Port.close()

if __name__ == "__main__":
    
    main()