import re
import math
import time

# -----------------------------------------------------------------------------------------
# Transformation Settings
# -----------------------------------------------------------------------------------------
FILE_NAME = 'cube.gcode'                             # filename including extension
FOLDER_NAME = 'gcodes/'                              # name of the subfolder in which the gcode is located
CONE_ANGLE = 16                                      # transformation angle
CONE_TYPE = 'outward'                                # type of the cone: 'inward' & 'outward'
FIRST_LAYER_HEIGHT = 0.2                             # moves all the gcode up to this height. Use also for stacking
PLATE_X,PLATE_Y = 110,110                            # moves your gcode away from the origin into the center of the bed (usually bed size / 2)                                       
X_MOVE,Y_MOVE = 0,-30                                # moves the modle away from the center of the bed if wanted

def move(x,y,c):
    # moves the modle to the origin, or away from it bassed on c, -1 or 1
    x,y = x+(c * PLATE_X),y+(c* PLATE_Y)
    return x,y

def transform(x,y,z,e_val,):
    if CONE_TYPE == 'outward':
        c = -1
    elif CONE_TYPE == 'inward':
        c = 1

    # does the math
    x,y = move(x,y,-1)
    z_val = z +c * (math.tan(math.radians(CONE_ANGLE)) * math.sqrt(x**2+y**2))
    x,y = move(x,y,1)

    # combines all info to make new row
    row_new = "G1"+" X"+str(round(x+X_MOVE,3))+ " Y"+str(round(y+Y_MOVE,3))+" Z"+str(round(z_val+FIRST_LAYER_HEIGHT,3))+" E"+str(e_val)+"\n"
    return row_new


def backtransform_data(data):
    new_data = []

    # makes the pattern for re to look for in Gcode
    pattern_X = r'X[-0-9]*[.]?[0-9]*'
    pattern_Y = r'Y[-0-9]*[.]?[0-9]*'
    pattern_Z = r'Z[-0-9]*[.]?[0-9]*'
    pattern_E = r'E[-0-9]*[.]?[0-9]*'
    pattern_G = r'\AG[1] '

    # sets important variables
    x_new, y_new = 0, 0
    z_layer = 0
    e_new = 0
    for row in data:

        # checks if the row is a G1 command
        g_match = re.search(pattern_G, row)

        if g_match is None:
            new_data.append(row)
        else:
            # finds the matches according to the method astablished before
            x_match = re.search(pattern_X, row)
            y_match = re.search(pattern_Y, row)
            z_match = re.search(pattern_Z, row)
            e_match = re.search(pattern_E, row)


            if x_match is None and y_match is None and z_match is None:
                new_data.append(row)
            else:
                # gets the values from the matches and turns it into a float
                if z_match is not None:
                    z_layer = float(z_match.group(0).replace('Z', ''))
                if x_match is not None:
                    x_new = float(x_match.group(0).replace('X', ''))
                if y_match is not None:
                    y_new = float(y_match.group(0).replace('Y', ''))
                if e_match is not None:
                    e_new = float(e_match.group(0).replace('E', ''))
                
                # adds all updated rows to the list of all rows
                new_data.append(transform(x_new,y_new,z_layer,e_new))
    return new_data


def main(path):
    # reads the file, and back-transforms it
    with open(path, 'r') as f_gcode:
        data = f_gcode.readlines()
    data_bt = backtransform_data(data)#data_bt is data_backtransformed

    # turns the list of commands back into a gcode file
    data_bt_string = ' '.join(data_bt)# joins all lines
    data_bt = [row + ' \n' for row in data_bt_string.split('\n')]# splits it into separate lines
    data_bt_string = ''.join(data_bt)# rejoins the lines

    # makes the nes file and puts the gcode commands into it
    path_write = re.sub(r'gcodes', 'gcodes_backtransformed', path)
    path_write = re.sub(r'.gcode','_bt.gcode', path_write)
    print(path_write)
    with open(path_write, 'w+') as f_gcode_bt:
        f_gcode_bt.write(data_bt_string)
    print('File successfully backtransformed.')
    return None

start_time = time.time()

main(FOLDER_NAME + FILE_NAME)

end_time = time.time()
print('GCode translated, time used:', end_time - start_time)
