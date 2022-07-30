from serial_init import *
from config import *
from protocolo import *
import time 
import numpy as np
#import matplotlib
#from matplotlib import pyplot as plt

def receive_msg(Port, event="ff"):
    event_code = bytearray.fromhex("0000")
    cmp1 = bytearray.fromhex("04ff")
    cmp2 = bytearray.fromhex("040e")
    cmp3 = bytearray.fromhex("043e")
    while (event_code != cmp1) and (event_code != cmp2) and (event_code != cmp3):
        time.sleep(0.1)
        #print(f"IN: {Port.in_waiting} - OUT: {Port.out_waiting}")
        event_code = Port.read(2)
        time.sleep(0.1)
        #print(f"IN: {Port.in_waiting} - OUT: {Port.out_waiting}")
        data_length = Port.read(1)
    if data_length == bytearray.fromhex(""):
        data_length = bytearray.fromhex("00")
    data = Port.read(int(data_length.hex(),16))
    return event_code.hex(" ") + " " + data_length.hex() + " " + data.hex(" ")

def get_data(Port):
    # Descarto los primeros 14 bytes
    Port.read(14)
    canales =""
    for i in range(5): 
        dato = int(Port.read(3).hex(),16)
        if dato > int("7FFFFF",16):
            dato -= int("1000000",16)
        canales += (str(dato)+",")
    Port.read(2)
    canales +="0,0,0\n"
    return canales

def main():
    print(serial_ports())
    print("Plataforma: " + sys.platform )
    
    #seleccion de puerto serie
    puerto = serial_choose()
    #puerto = "/dev/ttyACM1"
    print("Puerto serie elegido : " + puerto)

    #declaro el objeto de puerto serie (sin abrirlo)
    Port = serial.Serial()

    #parametros del puerto serie
    Port.port       = puerto
    Port.baudrate   = DEFAULT_BAURDATE
    Port.bytesize   = serial.EIGHTBITS      # number of bits per bytes # SEVENBITS
    Port.parity     = serial.PARITY_NONE    # set parity check: no parity # PARITY_ODD
    Port.stopbits   = serial.STOPBITS_ONE   # number of stop bits # STOPBITS_TWO

    try:
        Port.open()

    except Exception as e:
        print("Error abriendo puerto serie.\n" + str(e) + '\nFin de programa.')
        exit()
    Port.flushInput()       # flush input buffer, discarding all its contents
    Port.flushOutput()      # flush output buffer, aborting current output
                            # and discard all that is in buffer
    
    ba = bytearray.fromhex("01 1D FC 01 00") #HCIExt_ResetSystemCmd
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    msg = receive_msg(Port)
    print("Receiving: ", msg )
    if msg == "04 ff 05 1d 04 00 1d fc": print("OK")

    ba = bytearray.fromhex("01 00 FE 26 08 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00")
    Port.write(ba)
    print("Sending: ",ba.hex(" ")) # GAP_DeviceInit
    msg = receive_msg(Port)
    print("Receiving: ", msg)
    if msg == "04 ff 06 7f 06 00 00 fe 00": print("OK")
               
    msg = receive_msg(Port)
    print("Receiving: ", msg)
    if msg == "04 ff 2c 00 06 00 33 57 9b 0e 6c 54 ff 00 05 f2 50 43 88 08 84 42 2b 4a ac 34 38 b0 35 11 24 5d c5 ca 11 cf 56 80 25 14 64 9e df ed 64 0e d6": print("OK")

    ba = bytearray.fromhex("01 31 FE 01 15")
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    msg = receive_msg(Port)
    print("Receiving: ", msg)
    if msg == "04 ff 08 7f 06 00 31 fe 02 50 00": print("OK")

    ba = bytearray.fromhex("01 31 FE 01 16")
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    msg = receive_msg(Port)
    print("Receiving: ", msg)
    if msg == "04 ff 08 7f 06 00 31 fe 02 50 00": print("OK")

    ba = bytearray.fromhex("01 31 FE 01 1A")
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    msg = receive_msg(Port)
    print("Receiving: ", msg)
    if msg == "04 ff 08 7f 06 00 31 fe 02 00 00": print("OK")

    ba = bytearray.fromhex("01 31 FE 01 19")
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    msg = receive_msg(Port)
    print("Receiving: ", msg)
    if msg == "04 ff 08 7f 06 00 31 fe 02 d0 07": print("OK")

    print("--- GAP_DeviceDiscoveryRequest ---")
    ba = bytearray.fromhex("01 04 FE 03 03 01 00") #GAP_DeviceDiscoveryRequest
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    msg = "                "
    while msg[9:14] != "01 06":
        #print("--------------------",msg[9:14])
        time.sleep(1)
        msg = receive_msg(Port)
        print("Receiving: ", msg)
    
    
    # msg = receive_msg(Port)
    # print("Receiving: ", msg)
    # if msg == "04 ff 06 7f 06 00 04 fe 00": 
    #     print("OK")
    # msg = receive_msg(Port)
    # print("Receiving: ", msg)
    # msg = receive_msg(Port)
    # print("Receiving: ", msg)
    # msg = receive_msg(Port)
    # print("Receiving: ", msg)
    # msg = receive_msg(Port)
    # print("Receiving: ", msg)
    
    print("--- GAP_EstablishLinkRequest ---")
    ba = bytearray.fromhex("01 09 FE 09 00 00 00 FF 0F 6D F9 81 00") #Id de mi dispositivo
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    print("Receiving: ", receive_msg(Port))
    print("Receiving: ", receive_msg(Port))
    
    print("--- HCI_LE_SetDataLength ---")
    time.sleep(1)
    ba = bytearray.fromhex("01 22 20 06 00 00 FB 00 48 08") #set data length
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    print("Receiving: ", receive_msg(Port, event = HCI_CommandCompleteEvent))
    print("Receiving: ", receive_msg(Port, event = HCI_LE_GenericReportEvent))
    print("Receiving: ", receive_msg(Port))

    print("Waiting for GAP_LinkParamUpdateRequest")
    print("Receiving: ", receive_msg(Port))
    ba = bytearray.fromhex("01 20 20 0E 00 00 06 00 06 00 00 00 0A 00 00 00 00 00")
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    print("Receiving: ", receive_msg(Port))
    print("Receiving: ", receive_msg(Port))
    
    print("-------------------GATT_DiscAllCharDescs------------------")
    ba = bytearray.fromhex("01 84 FD 06 00 00 01 00 FF FF")
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    i=1
    while msg != "04 ff 06 05 05 1a 00 00 00":
        msg = receive_msg(Port)
        print(f"Receiving {i}: {msg}")
        i+=1



    # print("-------------------GATT_DiscAllPrimaryServices------------------")
    # ba = bytearray.fromhex("01 90 FD 02 00 00")
    # Port.write(ba)
    # print("Sending: ",ba.hex(" "))
    # #print("Receiving: ", Port.read(Port.in_waiting).hex(" "))
    # for i in range (2):
    #     msg = receive_msg(Port)
    #     print(f"Receiving {i+1}: {msg}")
    #     time.sleep(0.2)
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
    
    parameter_list = [ '01', '1F', '01','05', '07', '1E', '17','06', '18' ]    
    #parameter_list = [ '01', '1F', '01', '05', '08', '09', '0A', '17', '06', '18' ]    
    #parameter_list = ['01', '05', '07', '16', '06', '18' ]    
    for parameter in parameter_list:
        print("-------------------GATT_WriteCharValue------------------")
        ba = bytearray.fromhex(f"01 92 FD 05 00 00 20 00 {parameter}")
        Port.write(ba)
        print("Sending: ",ba.hex(" "))
        print("Receiving: ", receive_msg(Port))
        print("Receiving: ", receive_msg(Port))
  
   # escribir en  ti/simplelink_cc2640r2_sdk_5_10_00_02/source/ti/ble5stack/icall/inc/ble_user_config.h -> #MAX_PDU_SIZE 255
    print("GATT_ExchangeMTU")
    ba = bytearray.fromhex("01 82 FD 04 00 00 1E 00") # Le pido 0x1E canales, osea 30 porque el payload es eso -3.
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    print("Receiving: ", receive_msg(Port))
    print("Receiving: ", receive_msg(Port))
    print("Receiving: ", receive_msg(Port))
    
    print("-------------------GATT_WriteCharValue------------------")
    ba = bytearray.fromhex(f"01 92 FD 06 00 00 26 00 01 00")
    Port.write(ba)
    print("Sending: ",ba.hex(" "))
    print("Receiving: ", receive_msg(Port))
    print("Receiving: ", receive_msg(Port))
 
    start = time.monotonic()
    tiempo = 0
    DATA_FILE = 'data_8CH_1.csv'
    with open(DATA_FILE,"w",encoding="utf-8") as f: 
        while tiempo < 10:
            tiempo = time.monotonic()-start
            #data = get_data(Port)
            #print(f"{tiempo} - {data}")
            msg = receive_msg(Port)
            #print(msg)
            print(f"STATUS: {msg[33:41]}  CH1: {msg[42:50]}  CH2: {msg[51:59]}  CH3: {msg[60:68]}  CH4: {msg[69:77]}  CH5: {msg[78:86]}  CH6: {msg[87:95]}  CH7: {msg[96:104]} CH8: {msg[105:113]} Time: {tiempo}")
            #f.write(data)
            #f.write(f"{tiempo},{data}")
            
    Port.close()

# def plot(x=0, y=0):
#     """
#     Display the simulation using matplotlib, optionally using blit for speed
#     """
#     fig, ax = plt.subplots(1, 1)
#     ax.set_aspect('equal')
#     if x<60:
#         x_min = 0
#     else:
#         x_min = x
#     ax.set_xlim( x_min, x)
#     ax.set_ylim(-8000000, 8000000)
#     ax.hold(True)
#     plt.show(False)
#     plt.draw()

#     background = fig.canvas.copy_from_bbox(ax.bbox)

#     points = ax.plot(x, y, 'o')[0]
#     for ii in xrange(niter):

#         # update the xy data
#         x, y = rw.next()
#         points.set_data(x, y)
#         # restore background
#         fig.canvas.restore_region(background)
#         # redraw just the points
#         ax.draw_artist(points)
#         # fill in the axes rectangle
#         fig.canvas.blit(ax.bbox)

if __name__ == "__main__":
    
    main()