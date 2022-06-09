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
MOTION_OPTION = [0]


def TCP(conn, addr):
    buffer = array('B', [0] * 300)
    cnt = 0
    def hexOf(BUFFER): return ','.join([hex(i) for i in BUFFER])
    while True:
        try:
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

            # Add by zcc
            # #                 0,    1,    2, 3, 4, 5, 6, 7, 8, 9
            # cmd = array('B', [TID0, TID1, 0, 0, 0, 6, 1, 6, ])
            # conn.send()

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
                        DAT = array('B', np.array(
                            [MOTION_OPTION[0]], dtype=np.dtype('>i2')).tobytes())

                        # DAT = array('B', np.arange(
                        #     cnt, LEN+cnt + 1000, dtype=np.dtype('>i2')).tobytes())
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
    html.Div(id='my-output', style=style),

])


# %%
@app.callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='dropdown-1', component_property='value')
)
def update_output_div(input_value):
    print(input_value)

    if input_value == 0:
        MOTION_OPTION[0] = 0

    if input_value == 1:
        MOTION_OPTION[0] = 1100

    if input_value == 2:
        MOTION_OPTION[0] = 1200

    output = 'Success, {}, {}'.format(input_value, MOTION_OPTION)
    return output


# %%
if __name__ == '__main__':
    # try:
    #     app.run_server(host='0.0.0.0', debug=False)
    #     # app.run_server(debug=True)
    # except:
    #     pass

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 502))
    s.listen(1)

    conn, addr = s.accept()
    print("Connected by", addr[0])

    kwargs = dict(host='0.0.0.0', debug=False)
    a = threading.Thread(target=app.run_server, kwargs=kwargs)
    a.setDaemon(True)
    a.start()

    t = threading.Thread(target=TCP, args=(conn, addr))
    t.setDaemon(True)
    t.start()

    while True:
        inp = input()
        if inp == 'q':
            break

        MOTION_OPTION[0] = 0

        if inp == '1':
            MOTION_OPTION[0] = 1100

        if inp == '2':
            MOTION_OPTION[0] = 1200

    print('Done.')
