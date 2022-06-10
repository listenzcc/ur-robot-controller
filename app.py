# %%
import time
import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

import plotly.express as px
import pandas as pd

# %%
import socket
import threading
from array import array
from math import ceil
from struct import unpack
import numpy as np

# %%
# Initialize the very large REGISTER
_sz = 1000
REGISTER = [0] * _sz
REGISTER[101] = 5
REGISTER[102] = 5


def print_register():
    non_zeros = []
    for j, e in enumerate(REGISTER):
        if e == 0:
            continue
        non_zeros.append('{}: {}'.format(j, e))

    print('>> ' + ',\t'.join(non_zeros))
    return


# %%
MOTION_OPTION = [0]


def TCP(conn, addr):
    buffer = array('B', [0] * 300)
    cnt = 0
    def hexOf(BUFFER): return ','.join([hex(i) for i in BUFFER])
    while True:
        try:
            print_register()
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
                            REGISTER[ID:ID+LEN], dtype=np.dtype('>i2')).tobytes())
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
                    REGISTER[ID:ID+LEN] = eval(message)

                if message == '(400,)':
                    MOTION_OPTION[0] = 0

                print(f"Received Write Values = {message}\n--------")

            else:
                print(f"Function Code {FC} Not Supported")
                exit()
        except Exception as e:
            print(e, "\nConnection with Client terminated")
            exit()
# %%
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__)


# %%
# ------------------------------------------------------------------------------
# Motion Options
options = [0, 1, 2]

# %%
# ------------------------------------------------------------------------------
# App Layout
style = dict(
    width='90%'
)
title = 'Motion Options'
app.layout = html.Div([
    html.Div(html.H1('Amazing UR controller'), style=style),
    html.Div(html.H2(title), style=style),
    html.Div(dcc.Dropdown(id='dropdown-1',
                          options=options, value=0), style=style),
    html.Br(),
    html.Div(dcc.Slider(id='slider-1',
                        value=0, max=100, min=0, step=1)),
    html.Div(dcc.Slider(id='slider-2', vertical=True,
                        value=0, max=100, min=0, step=1)),
    html.Br(),
    html.Div(id='my-output', style=style),

])


# %%
@app.callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='slider-1', component_property='value'),
    Input(component_id='slider-2', component_property='value'),
)
def update_output_div(slider1, slider2):
    print(slider1, slider2)

    REGISTER[101] = min(100, int(slider1))
    REGISTER[102] = min(100, int(slider2))

    output = 'Success, slider-1: {}, slider-2: {}'.format(slider1, slider2)
    return output


# %%
if __name__ == '__main__':
    # try:
    #     app.run_server(host='0.0.0.0', debug=False)
    #     # app.run_server(debug=True)
    # except:
    #     pass

    # Wait for connect form UR
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 502))
    s.listen(1)

    conn, addr = s.accept()
    print("Connected by", addr[0])

    # Start HTML service
    use_html = True
    if use_html:
        kwargs = dict(host='0.0.0.0', debug=False)
        a = threading.Thread(target=app.run_server, kwargs=kwargs)
        a.setDaemon(True)
        a.start()

    # Start Modbus service
    t = threading.Thread(target=TCP, args=(conn, addr))
    t.setDaemon(True)
    t.start()

    # Terminal interaction
    while True:
        inp = input()
        if inp == 'q':
            break

        try:
            v = int(inp)
        except ValueError:
            v = 0

        REGISTER[101] = min(v, 100)


    print('Done.')
