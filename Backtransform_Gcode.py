import re
import numpy as np
import time

# -----------------------------------------------------------------------------------------
# Transformation Settings
# -----------------------------------------------------------------------------------------
FILE_NAME = 'Shape-Cyl.gcode'      # filename including extension
FOLDER_NAME = 'gcodes/'                              # name of the subfolder in which the gcode is located
CONE_ANGLE = 32                                      # transformation angle
CONE_TYPE = 'outward'                                # type of the cone: 'inward' & 'outward'
FIRST_LAYER_HEIGHT = 0.2                            # moves all the gcode up to this height. Use also for stacking
PLATE_X = 110                                       # moves your gcode away from the origin into the center of the bed (usually bed size / 2)
PLATE_Y = 110
X_MOVE = 0
Y_MOVE = 0
theta = np.radians(CONE_ANGLE)

def move(x,y):
    x,y = x-220,y-220
    return x,y

def replace_z(x,y,z_val,e_val):
    if CONE_TYPE == 'outward':
        c = -1
    elif CONE_TYPE == 'inward':
        c = 1
    z_val = z_val + c * (np.tan(theta) * np.sqrt(x**2+y**2))
    #move(x,y,1)
    row_new = "G1"+" X"+str(round(x,3))+ " Y"+str(round(y,3))+" Z"+str(round(z_val+FIRST_LAYER_HEIGHT,3))+" E"+str(e_val)+"\n"
    return row_new


def backtransform_data(data):
    new_data = []
    pattern_X = r'X[-0-9]*[.]?[0-9]*'
    pattern_Y = r'Y[-0-9]*[.]?[0-9]*'
    pattern_Z = r'Z[-0-9]*[.]?[0-9]*'
    pattern_E = r'E[-0-9]*[.]?[0-9]*'
    pattern_G = r'\AG[1] '

    x_new, y_new = 0, 0
    z_layer = 0
    e_new = 0
    for row in data:
        g_match = re.search(pattern_G, row)

        if g_match is None:
            new_data.append(row)
        else:
            x_match = re.search(pattern_X, row)
            y_match = re.search(pattern_Y, row)
            z_match = re.search(pattern_Z, row)
            e_match = re.search(pattern_E, row)

            if x_match is None and y_match is None and z_match is None:
                new_data.append(row)
            else:
                if z_match is not None:
                    z_layer = float(z_match.group(0).replace('Z', ''))
                if x_match is not None:
                    x_new = float(x_match.group(0).replace('X', ''))
                if y_match is not None:
                    y_new = float(y_match.group(0).replace('Y', ''))
                if e_match is not None:
                    e_new = float(e_match.group(0).replace('E', ''))
                x_new,y_new = move(x_new,y_new)
                new_data.append(replace_z(x_new,y_new,z_layer,e_new))
    return new_data


def main(path):

    with open(path, 'r') as f_gcode:
        data = f_gcode.readlines()
    data_bt = backtransform_data(data)#data_bt is data_backtransformed
    data_bt_string = ' '.join(data_bt)
    data_bt = [row + ' \n' for row in data_bt_string.split('\n')]
    data_bt_string = ''.join(data_bt)
    path_write = re.sub(r'gcodes', 'gcodes_backtransformed', path)
    path_write = re.sub(r'.gcode','_bt.gcode', path_write)
    print(path_write)
    with open(path_write, 'w+') as f_gcode_bt:
        f_gcode_bt.write(data_bt_string)
    print('File successfully backtransformed.')
    return None

starttime = time.time()
main(FOLDER_NAME + FILE_NAME)
endtime = time.time()
print('GCode translated, time used:', endtime - starttime)
