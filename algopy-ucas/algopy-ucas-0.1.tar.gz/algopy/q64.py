# Selection  :  select the k-th smallest number in a given list
# input  :  list a_list, int k
# output :  the k-th smallest number in a_list
# Using  :  k_result = get_kth(a_list, k)


def findKth(s, low, high, k):  # 递归寻找第k小的数
    mid = partition(s, low, high)
    if mid == len(s) - k:
        return s[mid]
    elif mid < len(s) - k:  # 当第k小的数在右侧时 查找右侧
        return findKth(s, mid + 1, high, k)
    else:  # 当第k小的数在左侧时 查找左侧
        return findKth(s, low, mid - 1, k)


def partition(s, low, high):  # 利用pivot对数组进行划分
    pivot, j = s[low], low
    for i in range(low + 1, high + 1):  # 小于pivot的放左边 大于pivot的放右边
        if s[i] >= pivot:
            j += 1
            s[i], s[j] = s[j], s[i]
    s[j], s[low] = s[low], s[j]
    return j  # 返回新的下标，同时也是第j小的数的位置


def get_kth(a_list, k):
    return findKth(a_list, 0, len(a_list) - 1, k)


if __name__ == '__main__':
    print(get_kth(a_list=[1, 2, 3, 4, 5], k=2))
