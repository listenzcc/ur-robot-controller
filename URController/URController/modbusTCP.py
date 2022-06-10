# %%
import socket
import threading
from array import array
from math import ceil
from struct import unpack
import numpy as np

# %%


class ModbusTCP(object):
    def __init__(self, sz=1000):
        self.REGISTER = [0] * sz
        self.serve_forever()

    def serve_forever(self):
        t = threading.Thread(target=self.serve)
        t.setDaemon(True)
        t.start()

    def print_register(self):
        non_zeros = []
        for j, e in enumerate(self.REGISTER):
            if e == 0:
                continue
            non_zeros.append('{}: {}'.format(j, e))

        print('>> ' + ',\t'.join(non_zeros))
        return

    def serve(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 502))
        s.listen(1)

        conn, addr = s.accept()
        print("Connected by", addr[0])

        self.TCP(conn, addr)

    def TCP(self, conn, addr):
        buffer = array('B', [0] * 300)
        cnt = 0
        def hexOf(BUFFER): return ','.join([hex(i) for i in BUFFER])
        while True:
            try:
                self.print_register()
                conn.recv_into(buffer)
                TID0 = buffer[0]  # Transaction ID	to sync
                TID1 = buffer[1]  # Transaction ID
                ID = buffer[6]  # Unit ID
                FC = buffer[7]  # Function Code
                mADR = buffer[8]  # Address MSB
                lADR = buffer[9]  # Address LSB
                ADR = mADR * 256 + lADR
                LEN = 1
                if FC not in [5, 6]:
                    LEN = buffer[10] * 256 + buffer[11]
                BYT = LEN * 2

                '''
                Supported Function Codes:

                1 = Read Coils or Digital Outputs
                2 = Read Digital Inputs
                3 = Read Holding Registers
                4 = Read Input Registers
                5 = Write Single Coil
                6 = Write Single Register
                15 = Write Coils or Digital Outputs
                16 = Write Holding Registers
                '''

                print("Received: ", hexOf(buffer[:6+buffer[5]]))
                if (FC in [1, 2, 3, 4]):  # Read Inputs or Registers
                    DAT = array('B')
                    if FC < 3:
                        BYT = ceil(LEN / 8)  # Round off the no. of bytes
                        v = 85  # send 85,86.. for bytes.
                        for i in range(BYT):
                            DAT.append(v)
                            v = (lambda x: x + 1 if (x < 255) else 85)(v)
                        DATA = DAT
                    else:
                        if FC == 4:
                            # FC: 4
                            # Read Input Registers
                            DAT = array('B', np.array(
                                self.REGISTER[ID:ID+LEN], dtype=np.dtype('>i2')).tobytes())
                            DATA = [i for i in range(cnt, LEN+cnt)]
                        else:
                            DAT = array('B', np.arange(
                                cnt, LEN+cnt, dtype=np.dtype('>i2')).tobytes())
                            DATA = [i for i in range(cnt, LEN+cnt)]

                    conn.send(
                        array('B', [TID0, TID1, 0, 0, 0, BYT + 3, ID, FC, BYT]) + DAT)

                    print(
                        f"TID = {(TID0 * 256 + TID1)}, ID= {ID}, Fun.Code= {FC}, Address= {ADR}, Length= {LEN}, Data= {DATA}\n--------")
                    if cnt < 60000:
                        cnt = cnt + 1
                    else:
                        cnt = 1
                elif (FC in [5, 6, 15, 16]):  # Write Registers
                    conn.send(
                        array('B', [TID0, TID1, 0, 0, 0, 6, ID, FC, mADR, lADR, buffer[10], buffer[11]]))

                    if FC in [5, 6]:
                        BYT = 2
                        buf = buffer[10:12]
                    else:
                        BYT = buffer[12]
                        buf = buffer[13:13+BYT]
                    print(
                        f"TID = {(TID0 * 256 + TID1)}, ID= {ID}, Fun.Code= {FC}, Address= {ADR}, Length= {LEN}, Bytes= {BYT}")
                    if FC == 5 or FC == 15:
                        message = 'bytes: ' + str(unpack('B' * BYT, buf))
                    elif FC == 6 or FC == 16:
                        message = str(unpack('>' + 'H' * int(BYT / 2), buf))
                        self.REGISTER[ID:ID+LEN] = eval(message)

                    print(f"Received Write Values = {message}\n--------")

                else:
                    print(f"Function Code {FC} Not Supported")
                    exit()
            except Exception as e:
                print(e, "\nConnection with Client terminated")
                exit()

# %%
