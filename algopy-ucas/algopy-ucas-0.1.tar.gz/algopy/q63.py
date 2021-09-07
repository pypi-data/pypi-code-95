# Find the number of inverse pairs of a given array
# input   :  list A
# output  :  the number of inverse pairs in list A
# Using   :  reverse_count = counting_inversion(list A)


def merge(nums, left, mid, right):
    res = 0  # 逆序对个数
    sorted = []  # 存储归并过程中排好序的数
    i, j = left, mid + 1
    while i <= mid and j <= right:
        if nums[i] > nums[j]:  # 如果左侧的数大于右侧 就将右侧的数赋给sorted 并给res加一
            sorted.append(nums[j])
            res += mid - i + 1
            j += 1
        else:
            sorted.append(nums[i])
            i += 1

    while i <= mid:  # 处理比较结束剩下的数
        sorted.append(nums[i])
        i += 1
    while j <= right:
        sorted.append(nums[j])
        j += 1

    for i in range(len(sorted)):  # 将排好序的数组 对应位置赋值给原数组
        nums[left + i] = sorted[i]
    return res  # 返回归并过程中产生的逆序对个数


def reverse(nums, left, right):
    if left >= right:  # 如果左侧下标大于右侧下标则退出递归
        return 0
    else:
        mid = int(left + (right - left) / 2)  # 找到中间位置的数
        lcount = reverse(nums, left, mid)  # 左侧逆序对个数
        rcount = reverse(nums, mid + 1, right)  # 右侧逆序对个数
        mcount = merge(nums, left, mid, right)  # 归并过程中产生的逆序对个数
        res = lcount + rcount + mcount
        return res


def counting_inversion(a_list):
    return reverse(a_list, 0, len(a_list) - 1)


if __name__ == '__main__':
    print(counting_inversion([1, 3, 2]))
