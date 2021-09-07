# Find the length of the longest common subsequence of A and B
# input  : list A, list B   # NOTES : elements of list A and list B should be integers
# output : the length of the longest common subsequence of A and B
# Using  :
#            A = [1, 2, 2, 2, 2, 2, 3]
#            B = [2, 2, 2, 2, 5]
#            lcs = max_common_sub(A, B)


def max_common_sub(A, B):
    lcs = [[0 for _ in range(len(A) + 1)] for _ in range(len(B) + 1)]
    for i in range(1, len(B) + 1):
        for j in range(1, len(A) + 1):
            if A[j - 1] == B[i - 1]:
                lcs[i][j] = lcs[i - 1][j - 1] + 1
            else:
                lcs[i][j] = max(lcs[i - 1][j], lcs[i][j - 1])
    return lcs[len(B)][len(A)]


if __name__ == '__main__':
    A = [1, 2, 2, 2, 2, 2, 3]
    B = [2, 2, 2, 2, 5]
    print(max_common_sub(A, B))
