def iterate(vec, fn):
    i, hi = 0, len(vec)
    while i < hi:
        fn(vec[i])
        i += 1
    pass

# def iterate(vec, fn):
#     i, hi = 0, len(vec)
#     if (n := length(fn)) == 1:
#         while i < hi:
#             fn(vec[i])
#             i += 1
#     elif n == 2:
#         while i < hi:
#             fn(vec[i], i)
#             i += 1
#     pass
