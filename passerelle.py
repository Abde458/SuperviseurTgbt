from pymodbus.client import ModbusSerialClient
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import threading
import time

# Configuration du client Modbus RTU (RS485)
modbus_rtu_client = ModbusSerialClient(
    port='COM4',  
    baudrate=9600,
    timeout=1,
    parity='N',
    stopbits=1,
    bytesize=8
)

# Configuration du serveur Modbus TCP
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0]*100),
    co=ModbusSequentialDataBlock(0, [0]*100),
    hr=ModbusSequentialDataBlock(0, [0]*100),
    ir=ModbusSequentialDataBlock(0, [0]*100)
)
context = ModbusServerContext(slaves={0x00: store}, single=False)  # Esclave ID 0x00

def rtu_to_tcp_bridge():
    """Lit les données du Modbus RTU et met à jour le serveur TCP."""
    while True:
        if modbus_rtu_client.connect():
            response = modbus_rtu_client.read_holding_registers(address=0, count=10, slave=0)
            if not response:
                print("pas de reponse")
            elif response.isError():
                print("Erreur de lecture RTU")
            else:
                # Correction ici : accès correct au datastore
                context[0x00].setValues(4, 0, response.registers)




                print(f"RTU → TCP : {response.registers}")
        time.sleep(2)  # Rafraîchir toutes les 2 secondes

# Lancer le pont RTU->TCP en thread
threading.Thread(target=rtu_to_tcp_bridge, daemon=True).start()

# Lancer le serveur Modbus TCP
print("🚀 Démarrage du serveur Modbus TCP sur le port 5020...")
StartTcpServer(context, address=("0.0.0.0", 5020))
