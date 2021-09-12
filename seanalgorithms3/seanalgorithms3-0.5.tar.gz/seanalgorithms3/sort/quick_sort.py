def partition(A, start, end):
    pivot = A[end]
    partition_index = start
    for i in range(start, end):
        if A[i] <= pivot:
            A[i], A[partition_index] = A[partition_index], A[i]
            partition_index += 1
    A[end], A[partition_index] = A[partition_index], A[end]
    
    return partition_index

def quick_sort(A, start, end):
    if start >= end: return 
    partition_index = partition(A, start, end)
    quick_sort(A, start, partition_index - 1)
    quick_sort(A, partition_index + 1, end)

    return A

def quickSort(ar):

    # Base case
    if len(ar) <= 1:
        return ar

        # Let us choose middle element a pivot
    else:
        mid = len(ar)//2
        pivot = ar[mid]

        # key element is used to break the array
        # into 2 halves according to their values
        smaller,greater = [],[]

        # Put greater elements in greater list,
        # smaller elements in smaller list. Also,
        # compare positions to decide where to put.
        for indx, val in enumerate(ar):
            if indx != mid:
                if val < pivot:
                    smaller.append(val)
                elif val > pivot:
                    greater.append(val)

                    # If value is same, then considering
                # position to decide the list.
                else:
                    if indx < mid:
                        smaller.append(val)
                    else:
                        greater.append(val)
        return quickSort(smaller)+[pivot]+quickSort(greater)

