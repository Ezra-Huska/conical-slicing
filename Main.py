import re
import math
import time
from stl import mesh
import numpy as np
import os

operation = input("Operation: ")
if operation=="tf":
    CONE_TYPE = input("Cone Type: ")
    if CONE_TYPE=="outward" or CONE_TYPE=="inward":
        CONE_ANGLE = int(input("Cone Angle: "))
        REFINEMENT_ITERATIONS = int(input("Refinment Iterations:"))
        FILE_PATH = input("File path): ")
        FILE_NAME = os.path.splitext(os.path.basename(FILE_PATH))[0]
        TF_FILE_PATH = input("Transfomed FolName (with der Location: ")
    elif CONE_TYPE=="default":
        CONE_ANGLE = 16
        REFINEMENT_ITERATIONS = 2
        FILE_PATH = "stl/"+input("File Name: ")
        FILE_NAME = os.path.splitext(os.path.basename(FILE_PATH))[0]
        TF_FILE_PATH = 'stl_transformed/'
    else:
        print("Unable to do said cone type")
        exit()
    def refinement_four_triangles(triangle):
        #Compute a refinement of a triangle. On every side, the midpoint is added. The three corner points and three midpoints result in four smaller triangles.
        point1 = triangle[0]
        point2 = triangle[1]
        point3 = triangle[2]
        midpoint12 = (point1 + point2) / 2
        midpoint23 = (point2 + point3) / 2
        midpoint31 = (point3 + point1) / 2
        triangle1 = np.array([point1, midpoint12, midpoint31])
        triangle2 = np.array([point2, midpoint23, midpoint12])
        triangle3 = np.array([point3, midpoint31, midpoint23])
        triangle4 = np.array([midpoint12, midpoint23, midpoint31])
        return np.array([triangle1, triangle2, triangle3, triangle4])


    def refinement_triangulation(triangle_array):
        #Compute a refinement of a triangulation using the refinement_four_triangles function.
        #The number of iteration defines, how often the triangulation has to be refined; n iterations lead to
        #4^n times many triangles.
        refined_array = triangle_array
        for i in range(0, REFINEMENT_ITERATIONS):
            n_triangles = refined_array.shape[0]*4
            refined_array = np.array(list(map(refinement_four_triangles, refined_array)))
            refined_array = np.reshape(refined_array, (n_triangles, 3, 3))
        return refined_array

    def transform(points):
        # Transfoms the points on the triagle bassed on their position to the center
        if CONE_TYPE == 'outward':
            c = 1
        elif CONE_TYPE == 'inward':
            c = -1
        else:
            raise ValueError('{} is not a admissible type for the transformation'.format(CONE_TYPE))
        transformation_method = (lambda x, y, z: np.array([x, y, z + c * np.sqrt(x**2 + y**2)*np.tan(np.radians(CONE_ANGLE))]))
        points_transformed = list(map(transformation_method, points[:, 0], points[:, 1], points[:, 2]))# makes it work in list form
        return np.array(points_transformed)


    def main(path):
        # takes the triangles from stl reifines them, transforms them, then makes a file with the data
        my_mesh = mesh.Mesh.from_file(path)
        vectors = my_mesh.vectors
        vectors_refined = refinement_triangulation(vectors)
        vectors_refined = np.reshape(vectors_refined, (-1, 3))
        vectors_transformed = transform(vectors_refined)
        vectors_transformed = np.reshape(vectors_transformed, (-1, 3, 3))
        my_mesh_transformed = np.zeros(vectors_transformed.shape[0], dtype=mesh.Mesh.dtype)
        my_mesh_transformed['vectors'] = vectors_transformed
        my_mesh_transformed = mesh.Mesh(my_mesh_transformed)
        return my_mesh_transformed

    start = time.time()
    transformed_STL = main(FILE_PATH + '.stl')
    transformed_STL.save(TF_FILE_PATH + FILE_NAME + '2_tf.stl')
    end = time.time()
    print('Transformation time:', end - start)

elif operation=="bt":
    CONE_TYPE = input("Cone Type: ")
    if CONE_TYPE=="outward" or CONE_TYPE=="inward":
        CONE_ANGLE = int(input("Cone Angle: "))
        FILE_PATH = input("File Name (with path): ")
        BT_FILE_PATH = input("Back-Transformed Folder Location: ")
        PLATE_X = int(input("Build Plate X Value: "))
        PLATE_Y = int(input("Build Plate Y Value: "))
    elif CONE_TYPE=="default":
        CONE_ANGLE = 16
        FILE_PATH = "gcodes/"+input("File Name: ")
        BT_FILE_PATH = 'gcodes_backtransformed/'
    else:
        print("Unable to do said cone type")
        exit()
    
    FIRST_LAYER_HEIGHT = 0.2
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
        row_new = "G1"+" X"+str(round(x,3))+ " Y"+str(round(y,3))+" Z"+str(round(z_val+FIRST_LAYER_HEIGHT,3))+" E"+str(e_val)+"\n"
        return row_new


    def backtransform_data(data):
        new_data = []

        # makes the pattern for re to look for in Gcode
        pattern_X = r'X[-0-9]*[.]?[0-9]*'
        pattern_Y = r'Y[-0-9]*[.]?[0-9]*'
        pattern_Z = r'Z[-0-9]*[.]?[0-9]*'
        pattern_E = r'E[-0-9]*[.]?[0-9]*'
        pattern_G = r'\AG[1] '
        pattern_G0 = r'\AG[0] '

        # sets important variables
        x_new, y_new = 0, 0
        z_layer = 0
        e_new = 0
        for row in data:

            # checks if the row is a G1 command
            g_match = re.search(pattern_G, row)
            g0_mathch = re.search(pattern_G0, row)

            if g_match is None and g0_mathch is None:
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

    main(FILE_PATH)

    end_time = time.time()
    print('GCode translated, time used:', end_time - start_time)
else:
    print("Unable to do said operation")
    exit()
