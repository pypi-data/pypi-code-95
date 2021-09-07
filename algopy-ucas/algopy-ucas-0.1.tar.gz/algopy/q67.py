# Calculate the multiplication of two given matrices
# Method  :  divide and conquer
# input   :  first line :  dimension of two matrices A and B
#            eg         :  if A is mxn and B is nxp, then you should input m n p
#            following lines : elements of matrices A and B correspondingly
# output  :  the multiplication result of given matrices A and B
# sample input  :
#           call mul_matrix()
#               2 2 3      # A is 2x2, B is 2x3
#               4 2        # A
#               0 5        # A
#               4 7 1      # B
#               2 3 0      # B
#
# sample output :
#               20 34 4
#               10 15 0


def division(A):
    n = int(len(A)/2)

    A11 = [[0 for i in range(n)] for j in range(n)]
    A12 = [[0 for i in range(n)] for j in range(n)]
    A21 = [[0 for i in range(n)] for j in range(n)]
    A22 = [[0 for i in range(n)] for j in range(n)]

    for i in range(n):
        for j in range(n):
            A11[i][j] = A[i][j]
            A12[i][j] = A[i][j+n]
            A21[i][j] = A[i+n][j]
            A22[i][j] = A[i+n][j+n]

    return (A11, A12, A21, A22)


# Add two matrices
# if key = 1 return A add B
# else return A sub B
def matrix_add_or_sub(A, B, key):
    C = [[0 for i in range(len(A))] for j in range(len(A))]
    if key == 1:
        for i in range(len(A)):
            for j in range(len(A)):
                C[i][j] = A[i][j] + B[i][j]
    else:
        for i in range(len(A)):
            for j in range(len(A)):
                C[i][j] = A[i][j] - B[i][j]
    return C


# Combine the four blocks of the matrix
def matrix_combination(A11, A12, A21, A22):
    n = len(A11)
    A = [[0 for i in range(n*2)] for j in range(n*2)]
    for i in range(n*2):
        for j in range(n*2):
            if i < n and j < n:
                A[i][j] = A11[i][j]
            elif i < n and j >= n:
                A[i][j] = A12[i][j-n]
            elif i >= n and j < n:
                A[i][j] = A21[i-n][j]
            else:
                A[i][j] = A22[i-n][j-n]

    return A


def matrix_multiplication(A, B):
    C = [[0 for i in range(len(A))] for j in range(len(A))]
    if(len(A) == 1):
        C[0][0] = A[0][0] * B[0][0]
    else:
        (A11, A12, A21, A22) = division(A)
        (B11, B12, B21, B22) = division(B)
        (C11, C12, C21, C22) = division(C)
        P1 = matrix_multiplication(A11, matrix_add_or_sub(B12, B22, 0))
        P2 = matrix_multiplication(matrix_add_or_sub(A11, A12, 1), B22)
        P3 = matrix_multiplication(matrix_add_or_sub(A21, A22, 1), B11)
        P4 = matrix_multiplication(A22, matrix_add_or_sub(B21, B11, 0))
        P5 = matrix_multiplication(matrix_add_or_sub(
            A11, A22, 1), matrix_add_or_sub(B11, B22, 1))
        P6 = matrix_multiplication(matrix_add_or_sub(
            A12, A22, 0), matrix_add_or_sub(B21, B22, 1))
        P7 = matrix_multiplication(matrix_add_or_sub(
            A11, A21, 0), matrix_add_or_sub(B11, B12, 1))
        C11 = matrix_add_or_sub(matrix_add_or_sub(
            matrix_add_or_sub(P4, P5, 1), P6, 1), P2, 0)
        C12 = matrix_add_or_sub(P1, P2, 1)
        C21 = matrix_add_or_sub(P3, P4, 1)
        C22 = matrix_add_or_sub(matrix_add_or_sub(
            matrix_add_or_sub(P1, P5, 1), P3, 0), P7, 0)
        C = matrix_combination(C11, C12, C21, C22)
    return C


# Calculate the multiplication of two matrices with grade-school algorithm.
def matrix_multiplication_3r(A, B):
    C = [[0 for i in range(len(B[0]))] for j in range(len(A))]
    for i in range(len(A)):
        for j in range(len(B[0])):
            for k in range(len(B)):
                C[i][j] = C[i][j] + A[i][k]*B[k][j]
    return C


def mul_matrix():
    [a, b, c] = list(map(int, input().split()))
    mmax = max(max(a, b), c)

    if mmax > 50:
        A = [[0 for i in range(b)] for j in range(a)]
        B = [[0 for i in range(c)] for j in range(b)]
        for i in range(a):
            A[i] = [int(j) for j in input().split()]
        for i in range(b):
            B[i] = [int(j) for j in input().split()]
        C = matrix_multiplication_3r(A, B)
        for i in range(a):
            print(" ".join(str(i) for i in C[i]))
    else:
        n = 1
        while(mmax > n):
            n = n * 2
        A = [[0 for i in range(n)] for j in range(n)]
        B = [[0 for i in range(n)] for j in range(n)]
        for i in range(a):
            A[i] = [int(j) for j in input().split()]
            A[i] = A[i] + [0]*(n-len(A[i]))
        for i in range(b):
            B[i] = [int(j) for j in input().split()]
            B[i] = B[i] + [0]*(n-len(B[i]))
        C = matrix_multiplication(A, B)
        for i in range(len(C)):
            C[i] = C[i][:c]
        for i in range(a):
            print(" ".join(str(i) for i in C[i]))


if __name__ == '__main__':
    mul_matrix()
