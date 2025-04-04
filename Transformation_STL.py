from stl import mesh
import numpy as np
import time

#-----------------------------------------------------------------------------------------
# Transformation Settings
#-----------------------------------------------------------------------------------------

FILE_NAME = 'EN_cube'                              # Filename without extension
FOLDER_NAME_UNTRANSFORMED = 'stl/'
FOLDER_NAME_TRANSFORMED = 'stl_transformed/'    # Make sure this folder exists
CONE_ANGLE = 16                                 # Transformation angle
REFINEMENT_ITERATIONS = 3                       # refinement iterations of the stl. 2-3 is a good start for regular stls. If its already uniformaly fine, use 0 or 1. High number cause huge models and long script runtimes
CONE_TYPE = 'outward'                           # type of the cone: 'inward' & 'outward'


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


def transformation(points):
    # Transfoms the points on the triagle bassed on their position to the center
    if CONE_TYPE == 'outward':
        c = 1
    elif CONE_TYPE == 'inward':
        c = -1
    else:
        raise ValueError('{} is not a admissible type for the transformation'.format(CONE_TYPE))
    transformation_method = (lambda x, y, z: np.array([x/np.cos(np.radians(CONE_ANGLE)), y/np.cos(np.radians(CONE_ANGLE)), z + c * np.sqrt(x**2 + y**2)*np.tan(np.radians(CONE_ANGLE))]))
    points_transformed = list(map(transformation_method, points[:, 0], points[:, 1], points[:, 2]))# makes it work in list form
    return np.array(points_transformed)


def main(path):
    # takes the triangles from stl reifines them, transforms them, then makes a file with the data
    my_mesh = mesh.Mesh.from_file(path)
    vectors = my_mesh.vectors
    vectors_refined = refinement_triangulation(vectors)
    vectors_refined = np.reshape(vectors_refined, (-1, 3))
    vectors_transformed = transformation(vectors_refined)
    vectors_transformed = np.reshape(vectors_transformed, (-1, 3, 3))
    my_mesh_transformed = np.zeros(vectors_transformed.shape[0], dtype=mesh.Mesh.dtype)
    my_mesh_transformed['vectors'] = vectors_transformed
    my_mesh_transformed = mesh.Mesh(my_mesh_transformed)
    return my_mesh_transformed

start = time.time()
transformed_STL = main(path=FOLDER_NAME_UNTRANSFORMED + FILE_NAME + '.stl')
transformed_STL.save(FOLDER_NAME_TRANSFORMED + FILE_NAME + '_tf.stl')
end = time.time()
print('Transformation time:', end - start)
