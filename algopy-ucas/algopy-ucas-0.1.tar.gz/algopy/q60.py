# Greatest Common Divisor
# input   :  int A, int B
# output  :  greatest common divisor of A and B
# Using   :  gcd_result = gcd(A, B)


def gcd(A, B):
    if A is 0 or B is 0:
        return max(A, B)

    else:
        if A < B:
            A, B = B, A

        while A % B:
            temp = A % B
            A = B
            B = temp

        return B


if __name__ == "__main__":
    print(gcd(A=15, B=45))
