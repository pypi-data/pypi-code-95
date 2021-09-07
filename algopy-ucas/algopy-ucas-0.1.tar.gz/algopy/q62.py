# QuickSort Method
# input     :  list A
# output    :  sorted list in increasing order
# function  :  Sorted list A using QuickSort Method
# Warning   :  original list A has been changed
# Using     :  sorted_list = quick_sort(list_A)


def split(array, left, right):
    pivot = array[left]
    while left < right:
        while left < right and array[right] >= pivot:
            right -= 1
        array[left] = array[right]
        while left < right and array[left] <= pivot:
            left += 1
        array[right] = array[left]
    array[left] = pivot
    return left


def quickSort(array, left, right):
    if left <= right:
        pos = split(array, left, right)
        quickSort(array, left, pos - 1)
        quickSort(array, pos + 1, right)


def quick_sort(list_A):
    quickSort(list_A, 0, len(list_A) - 1)
    return list_A


if __name__ == '__main__':
    array = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    new_array = quick_sort(array)
    print(new_array)