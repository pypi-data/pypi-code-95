import sage
import numpy as np
def harmonicFormMatrix(sc, d, ring=sage.rings.rational_field.QQ, verbose=False):
    """
    Returns a matrix representation of a linear map
    
    C_d(sc) -> C_d(sc)
    
    which takes every cycle to the unique harmonic representative of its homology class.
    This matrix is relative to the standard basis given by the d-cells of sc, with the
    order aligning with that of sc._n_cells_sorted(d).

    Parameters
    ----------
    sc : SimplicialComplex
        The simplicial complex.
    
    d : int
        The dimension of cells and degree of homology in question.
    
    ring : optional
        The coefficient ring for the homology groups. If the harmonic form matrix does
        not exist over the given ring, raises a ZeroDivisionError. (Default is QQ.)

    Raises
    ------
    ZeroDivisionError
        If the matrix does not exist over the given ring.
    """
    
    if verbose: print("Constructing chain complex", flush=True)
    chain = sc.chain_complex(base_ring = ring, check = False, dimensions = [d,d+1],verbose=verbose)
    if verbose: print("Extracting boundary module", flush=True)
    B = chain.differential(d+1).column_space() #B_{d}
    if verbose: print("Mapping to B complement.", flush=True)
    qmap = B.complement().basis_matrix()
    try:
        if verbose: print("Constructing Pseudoinverse", flush=True)
        pseudoinverse = qmap.transpose() *(qmap * qmap.transpose()).inverse() #Works since qmap is surjective
    except ZeroDivisionError as err:
        raise ZeroDivisionError("Harmonic form matrix does not exist for this complex over {}.".format(ring))
    return pseudoinverse*qmap


def boundaryMatrix(sc, d, ring=sage.rings.rational_field.QQ, verbose = False, cochain=False):
    chain = sc.chain_complex(base_ring = ring, check = False, dimensions = [d-1,d],verbose=verbose,cochain=cochain)
    if cochain:
        return chain.differential(d-1)
    else:
        return chain.differential(d)

def plotCycle(pointCloud, cycle, simplices, ring=sage.rings.rational_field.QQ, threeD=False, plotSupportOnly=False):
    #Determine edge weights
    edge_weights = {}
    #For each 1-cell
    for i in range(len(cycle)):
        tup = simplices[i]
        #Assign edge weight to this edge
        if ring.characteristic() == 0:
            if plotSupportOnly:
                if cycle[i]==0: edge_weights[tup] = float(0)
                else:           edge_weights[tup] = float(1)
            else:
                edge_weights[tup] = float(abs(cycle[i]))
        else:
            if plotSupportOnly:
                if cycle[i].lift()==0: edge_weights[tup] = float(0)
                else:                  edge_weights[tup] = float(1)
            else:
                edge_weights[tup] = float(cycle[i].lift_centered())
    max_edge_weight = max(edge_weights.values())

    #Plotting starts here
    import matplotlib.pyplot as plt

    if threeD:
        from mpl_toolkits.mplot3d.art3d import Line3D
        x_input_list = [float(x) for x in pointCloud['x']]
        y_input_list = [float(y) for y in pointCloud['y']]
        z_input_list = [float(z) for z in pointCloud['z']]
        fig = plt.figure()
        ax = plt.axes(projection="3d")
        ax.set_box_aspect((np.ptp(x_input_list), np.ptp(y_input_list), np.ptp(z_input_list)))
        
        ax.scatter3D(pointCloud['x'],pointCloud['y'],pointCloud['z'])

        for edge, weight in edge_weights.items():
            x_list = [x_input_list[edge[0]],x_input_list[edge[1]]]
            y_list = [y_input_list[edge[0]],y_input_list[edge[1]]]
            z_list = [z_input_list[edge[0]],z_input_list[edge[1]]]
            importance = weight/max_edge_weight
            ax.plot(x_list,y_list,z_list,"b", linewidth = importance*2)
    else:
        fig = plt.figure()
        # fig.plot_width = int(1000)
        # fig.plot_height = int(1000)
        ax = plt.axes()

        x_input_list = [float(x) for x in pointCloud['x']]
        y_input_list = [float(y) for y in pointCloud['y']]

        ax.scatter(pointCloud['x'],pointCloud['y'])

        for edge, weight in edge_weights.items():
            x_list = [x_input_list[edge[0]],x_input_list[edge[1]]]
            y_list = [y_input_list[edge[0]],y_input_list[edge[1]]]
            importance = weight/max_edge_weight
            ax.plot(x_list,y_list,"b", linewidth = importance*2)
    plt.show(fig)

def spanningCotrees(sc,d):
    """
    #Finds all spanning cotrees of a simplicial complex.

    """
    
    bd = boundaryMatrix(sc,d, cochain=True)
    coboundary_matroid = sage.all.Matroid(coboundary_matrix)
    d_minus_one_cells = set(range(coboundary_matrix.ncols()))
    #This line uses the default Sage algorithm for finding bases of general matroids. It is not efficient.
    return [d_minus_one_cells.difference(base) for base in coboundary_matroid.bases()]

def restrictedLaplacian(sc,d):
    #Compute dth laplacian
    bd = boundaryMatrix(sc,d+1)
    cob = bd.transpose()
    lap = bd*cob
    #Restrict Laplacian
    inclusion_map = bd.column_space().basis_matrix().transpose()
    inclusion_map_pseudo = inclusion_map.pseudoinverse()
    restricted_lap = inclusion_map_pseudo*lap*inclusion_map
    return restricted_lap