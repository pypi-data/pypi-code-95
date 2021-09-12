import numpy as np


def spring_force(points, i, k, space):
    v1 = space.vec(points[i - 1, :], points[i, :])
    v2 = space.vec(points[i + 1, :], points[i, :])
    return k * (v1 + v2)


def component_in_line(vector, direction):
    return direction * sum(vector * direction) / np.linalg.norm(direction) ** 2


def get_neb_tuning(points, bo, space, maxf):
    # if a point is moved directly towards its neighbour by the mean
    # distance between points, it will get assigned maximum parallel force
    dist = np.linalg.norm(space.vec(points[0, :], points[1, :]))
    spring_k = maxf / (2 * dist)

    # maximum perpendicular force is assigned to the steepest gradient
    n_pts = points.shape[0]
    dim = points.shape[1]
    gradients = bo.get_grad(points)[0]
    maxg = 0
    for i in range(n_pts):
        temp = np.zeros(dim)
        for j in range(dim):
            temp[j] = gradients[i][j][0]
        length = np.linalg.norm(temp)
        if length > maxg:
            maxg = length
    grad_k = maxf / maxg
    return spring_k, grad_k


def neb(points, bo, space, maxiter=1000):
    # initialize
    n_pts = points.shape[0]
    dim = points.shape[1]
    maxf = np.min(space.bounds[1, :] - space.bounds[0, :]) / 100
    spring_k, grad_k = get_neb_tuning(points, bo, space, maxf)

    for abc in range(maxiter):
        # get gradients
        gradients = bo.get_grad(points)[0]
        temp = np.zeros(n_pts * dim).reshape(n_pts, dim)
        for i in range(n_pts):
            for j in range(dim):
                temp[i, j] = gradients[i][j][0]
        gradients = temp

        # get spring forces
        spring_f = np.zeros(n_pts * dim).reshape(n_pts, dim)
        for i in range(1, n_pts - 1):
            spring_f[i] = spring_force(points, i, spring_k, space)

        # get and combine components
        forces = np.zeros(n_pts * dim).reshape(n_pts, dim)
        worst = 0.0
        for i in range(1, n_pts - 1):
            parallel = space.vec(points[i - 1, :], points[i + 1, :])
            parallel_f = component_in_line(spring_f[i], parallel)
            perpendic = -gradients[i] * grad_k
            perpendic_f = perpendic - component_in_line(perpendic, parallel)
            forces[i, :] = parallel_f + perpendic_f
            fnorm = np.linalg.norm(forces[i, :])
            worst = np.max((worst, fnorm))
            if fnorm > maxf:
                forces[i, :] = forces[i, :] / fnorm * maxf

        prev_pts = points.copy()
        points = points + forces
        points = space.crds(points)
        outofbounds = np.isnan(points[:, 0])
        points[outofbounds, :] = prev_pts[outofbounds, :]

        if worst < 0.1 * maxf:
            break

    return points
