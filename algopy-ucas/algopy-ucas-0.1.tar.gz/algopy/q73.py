# RNA Secondary Structure Prediction
# input  : string s
# output : An integer represents the maximum number of matches
# Using  : rna_ssp(s='UGUACCGGUUAGUACA')

def rna_ssp(s):
    n = len(s)
    opt = [[0 for _ in range(n+1)] for _ in range(n+1)]
    l = 6
    while l <= n:
        i = 1
        while i <= n - l + 1:
            j = i + l - 1
            max_match_at_j = 0
            k = i
            while k < j - 4:
                match_score = 0
                if ((s[j-1] == 'A' and s[k-1] == 'U') or
                        (s[j-1] == 'U' and s[k-1] == 'A') or
                        (s[j-1] == 'C' and s[k-1] == 'G') or
                        (s[j-1] == 'G' and s[k-1] == 'C')):
                    match_score = 1 + opt[i][k-1] + opt[k + 1][j - 1]
                max_match_at_j = max(match_score, max_match_at_j)
                k += 1
            opt[i][j] = max(opt[i][j-1], max_match_at_j)
            i += 1
        l += 1
    print(opt[1][n])


if __name__ == '__main__':
    rna_ssp(s='UGUACCGGUUAGUACA')