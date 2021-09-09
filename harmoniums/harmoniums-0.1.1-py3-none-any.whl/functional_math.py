import ctypes

import numba as nb
from numba import carray, njit, types
from numpy import (
    absolute,
    array,
    bool_,
    float64,
    exp,
    log,
    logaddexp,
)
from scipy import LowLevelCallable

from harmoniums.utils import generate_binary_permutations

# Code from StackOverflow:
# https://stackoverflow.com/questions/58421549/passing-numpy-arrays-as-arguments-to-numba-cfunc
# Void Pointer from Int64
@nb.extending.intrinsic
def address_as_void_pointer(typingctx, src):
    """ returns a void pointer from a given memory address """

    sig = nb.core.types.voidptr(src)

    def codegen(cgctx, builder, sig, args):
        return builder.inttoptr(args[0], nb.core.cgutils.voidptr_t)

    return sig, codegen


@njit
def _phi(X_A, X_B, X_C, W_A, W_B, W_C, V, sigma, b):
    # Binary model: sum_i x_i W_ij
    phi_A = X_A @ W_A

    # Gamma model: sum_i x_i W_ij - log[x_i] |V_ij|
    # Take log safely, by replacing 0 values with large instead of `inf`
    # number.
    phi_B = X_B @ W_B - log(X_B) @ absolute(V)

    # Gauss model: sum_i x_i W_ij/sigma_i
    phi_C = X_C / sigma.T @ W_C

    # And the overall bias.
    return b.T + phi_A + phi_B + phi_C


@njit
def _partition_function_i(
    x_args,
    x_A,
    x_B,
    x_C,
    mask_A,
    mask_B,
    mask_C,
    a_A,
    a_B,
    a_C,
    c,
    W_A,
    W_B,
    W_C,
    V,
    sigma,
    b,
):
    """
    Compute latent partition function of a triplet row.
    """
    # The first n_B elements in `x_args` are survival variables, and the
    # remaining elements (n_C in total) are Gaussian variables.
    n_A = (~mask_A).sum()
    n_B = (~mask_B).sum()

    x_B[~mask_B] = x_args[:n_B]
    F_B = x_B @ a_B - log(x_B) @ absolute(c)

    x_C[~mask_C] = x_args[n_B:]
    quadratic = ((x_C - a_C.T) / sigma.T) ** 2 / 2
    F_C = quadratic.sum(axis=1)

    # Marginalise out the missing values.
    if n_A > 0:
        result = 0.0
        for x_A_censored in generate_binary_permutations(n_A):
            x_A[~mask_A] = x_A_censored
            F_A = x_A @ a_A
            F = (
                F_A
                + F_B
                + F_C
                - logaddexp(0, -_phi(x_A, x_B, x_C, W_A, W_B, W_C, V, sigma, b)).sum(
                    axis=1
                )
            )
            # Convert scalar array to float.
            result += exp(-F[0])
        return result

    F_A = x_A @ a_A
    F = (
        F_A
        + F_B
        + F_C
        - logaddexp(0, -_phi(x_A, x_B, x_C, W_A, W_B, W_C, V, sigma, b)).sum(axis=1)
    )
    # Convert scalar array to float.
    return exp(-F[0])


def as_low_level(jitted_function, args_dtype):
    """
    Wrap as SciPy compatible low level C function.
    """
    # Signature:
    # double func(int n, double *xx, void *user_data)
    @nb.cfunc(
        types.float64(
            types.int32, types.CPointer(types.float64), types.CPointer(args_dtype)
        )
    )
    def wrapped(n, xx, user_data_ptr):
        """
        Wrapper to change signature of `jitted_func` to be compatible with SciPy.

        Args:
            n (int): Size of input array (xx).
            xx (array): Array of floats, containing actual data.
            user_data_ptr: Pointer to struct, containing pointers + size of
                arguments to pass to `jitted_func`.
        """
        # Array of structs
        data = carray(user_data_ptr, 1)[0]
        xx = carray(xx, n, dtype=float64)

        # Unpack the data (the arguments to pass to `jitted_function`) from
        # user_data, which is a C level structure.
        x_A = carray(
            address_as_void_pointer(data.x_A_ptr), data.x_A_size, dtype=float64
        )
        x_B = carray(
            address_as_void_pointer(data.x_B_ptr), data.x_B_size, dtype=float64
        )
        x_C = carray(
            address_as_void_pointer(data.x_C_ptr), data.x_C_size, dtype=float64
        )

        mask_A = carray(
            address_as_void_pointer(data.mask_A_ptr), data.mask_A_size, dtype=bool_
        )
        mask_B = carray(
            address_as_void_pointer(data.mask_B_ptr), data.mask_B_size, dtype=bool_
        )
        mask_C = carray(
            address_as_void_pointer(data.mask_C_ptr), data.mask_C_size, dtype=bool_
        )

        a_A_shape = (data.a_A_size, 1)
        a_A = carray(address_as_void_pointer(data.a_A_ptr), a_A_shape, dtype=float64)

        a_B_shape = (data.a_B_size, 1)
        a_B = carray(address_as_void_pointer(data.a_B_ptr), a_B_shape, dtype=float64)

        a_C_shape = (data.a_C_size, 1)
        a_C = carray(address_as_void_pointer(data.a_C_ptr), a_C_shape, dtype=float64)

        c_shape = (data.c_size, 1)
        c = carray(address_as_void_pointer(data.c_ptr), c_shape, dtype=float64)

        W_A_shape = (data.W_A_rows, data.W_A_cols)
        W_A = carray(address_as_void_pointer(data.W_A_ptr), W_A_shape, dtype=float64)

        W_B_shape = (data.W_B_rows, data.W_B_cols)
        W_B = carray(address_as_void_pointer(data.W_B_ptr), W_B_shape, dtype=float64)

        W_C_shape = (data.W_C_rows, data.W_C_cols)
        W_C = carray(address_as_void_pointer(data.W_C_ptr), W_C_shape, dtype=float64)

        V_shape = (data.V_rows, data.V_cols)
        V = carray(address_as_void_pointer(data.V_ptr), V_shape, dtype=float64)

        sigma_shape = (data.sigma_size, 1)
        sigma = carray(
            address_as_void_pointer(data.sigma_ptr), sigma_shape, dtype=float64
        )

        b_shape = (data.b_size, 1)
        b = carray(address_as_void_pointer(data.b_ptr), b_shape, dtype=float64)

        # We have unpacked all the arguments, so they can be passed to
        # `jitted_function`.
        return jitted_function(
            xx,
            x_A,
            x_B,
            x_C,
            mask_A,
            mask_B,
            mask_C,
            a_A,
            a_B,
            a_C,
            c,
            W_A,
            W_B,
            W_C,
            V,
            sigma,
            b,
        )

    return wrapped


# This C structure holds pointers (stored as integers) and memory sizes of:
# - Input variables (triplet of vectors values + triplet of missingness masks).
# - adjustable parameters of the model.
#
# Purpose: SciPy's LowLevelCallable can only receive arguments using a C level
# `user_data` structure. We therefore pack all our data into this struct, and
# unpack it during evaluation (see `as_low_level`).
args_dtype = types.Record.make_c_struct(
    [
        # Original data, for each variable type.
        ("x_A_ptr", types.int64),
        ("x_A_size", types.int64),
        ("x_B_ptr", types.int64),
        ("x_B_size", types.int64),
        ("x_C_ptr", types.int64),
        ("x_C_size", types.int64),
        # Masks that indicate if the value is observed or missing/censored.
        ("mask_A_ptr", types.int64),
        ("mask_A_size", types.int64),
        ("mask_B_ptr", types.int64),
        ("mask_B_size", types.int64),
        ("mask_C_ptr", types.int64),
        ("mask_C_size", types.int64),
        # Model parameters.
        # 1) Vectors (1d).
        ("a_A_ptr", types.int64),
        ("a_A_size", types.int64),
        ("a_B_ptr", types.int64),
        ("a_B_size", types.int64),
        ("a_C_ptr", types.int64),
        ("a_C_size", types.int64),
        ("c_ptr", types.int64),
        ("c_size", types.int64),
        # 2) Matrices (2d).
        ("W_A_ptr", types.int64),
        ("W_A_rows", types.int64),
        ("W_A_cols", types.int64),
        ("W_B_ptr", types.int64),
        ("W_B_rows", types.int64),
        ("W_B_cols", types.int64),
        ("W_C_ptr", types.int64),
        ("W_C_rows", types.int64),
        ("W_C_cols", types.int64),
        ("V_ptr", types.int64),
        ("V_rows", types.int64),
        ("V_cols", types.int64),
        # 3) Also vectors (1d).
        ("sigma_ptr", types.int64),
        ("sigma_size", types.int64),
        ("b_ptr", types.int64),
        ("b_size", types.int64),
    ]
)


def _pack_as_user_data(
    x_A, x_B, x_C, mask_A, mask_B, mask_C, a_A, a_B, a_C, c, W_A, W_B, W_C, V, sigma, b,
):
    """
    Pack arguments as `user_data` low level C structure.

    Purpose: SciPy's LowLevelCallable can only receive arguments using a C level
    `user_data` structure. We therefore pack all our data into this struct, and
    unpack it during evaluation (see `as_low_level`).
    """
    args = (
        # Original data, for each variable type.
        x_A.ctypes.data,  # Pointer to memory address.
        x_A.size,  # Size of memory block.
        x_B.ctypes.data,
        x_B.size,
        x_C.ctypes.data,
        x_C.size,
        # Masks that indicate if the value is observed or missing/censored.
        mask_A.ctypes.data,
        mask_A.size,
        mask_B.ctypes.data,
        mask_B.size,
        mask_C.ctypes.data,
        mask_C.size,
        # Model parameters.
        # 1) Vectors (1d).
        a_A.ctypes.data,
        a_A.size,
        a_B.ctypes.data,
        a_B.size,
        a_C.ctypes.data,
        a_C.size,
        c.ctypes.data,
        c.size,
        # 2) Matrices (2d).
        W_A.ctypes.data,  # Pointer to memory address, size: rows x columns.
        W_A.shape[0],  # Number of rows.
        W_A.shape[1],  # Number of columns.
        W_B.ctypes.data,
        W_B.shape[0],
        W_B.shape[1],
        W_C.ctypes.data,
        W_C.shape[0],
        W_C.shape[1],
        V.ctypes.data,
        V.shape[0],
        V.shape[1],
        # 3) Vectors (1d).
        sigma.ctypes.data,
        sigma.size,
        b.ctypes.data,
        b.size,
    )
    return array(args, dtype=args_dtype)


__c_function_partition_function_i = as_low_level(_partition_function_i, args_dtype)


def _lambda_partition_function_i(
    x_A, x_B, x_C, mask_A, mask_B, mask_C, a_A, a_B, a_C, c, W_A, W_B, W_C, V, sigma, b,
):
    """
    Build SciPy `LowLevelCallable` to reduce Python overhead during integration.

    C level signature:
        double func(int n, double *xx, void *user_data)
    """
    # Pack arguments in C structure.
    user_data = _pack_as_user_data(
        x_A,
        x_B,
        x_C,
        mask_A,
        mask_B,
        mask_C,
        a_A,
        a_B,
        a_C,
        c,
        W_A,
        W_B,
        W_C,
        V,
        sigma,
        b,
    )
    # Pass C structure as user_data argument in Numba compiled C function.
    integrand_func = LowLevelCallable(
        __c_function_partition_function_i.ctypes,
        user_data=user_data.ctypes.data_as(ctypes.c_void_p),
    )
    return integrand_func
