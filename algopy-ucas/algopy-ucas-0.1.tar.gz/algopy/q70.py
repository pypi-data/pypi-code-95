# Matrix chain multiplication
# calculate the minimum multiply times of a matrices sequence
# input  :  a list of several matrices dimension in order
# output :  Fully parenthesizing to minimize the number of scalar multiplications.
# Using  :
# sample input  :
#                matrix_chain_multiplication([3, 2, 4, 4])
# sample output :
#                ((A)((A)(A)))


def matrix_chain_multiplication(dim_number):
    #  动态规划计算矩阵相乘最优顺序
    #  输入：矩阵维度列表
    #  输出：矩阵最优相乘序列
    matrix_name_list = ['A' for _ in range(len(dim_number) - 1)]
    dp = {}  # 二维 dp[i,j]表示第i个矩阵到第j个矩阵所需的最少相乘次数，防止重复计算
    for i in range(1, len(dim_number)):
        dp[i, i] = 0  # 一个矩阵不需要运算，故运算次数为0

    print(dp)

    location = {}  # 存储最优括号划分，用于回溯
    for l in range(2, len(dim_number)):
        for i in range(1, len(dim_number) - l + 1):
            # 只计算二维矩阵上三角的值即可，i > j时不需要计算
            j = i + l - 1
            dp[i, j] = 1e100  # 设置一个很大的初值
            for k in range(i, j):
                # 计算在k位置加括号时的计算次数
                cal_num = dp[i, k] + dp[k + 1, j] + dim_number[i - 1] \
                    * dim_number[k] * dim_number[j]
                if cal_num < dp[i, j]:
                    dp[i, j] = cal_num  # 更新最少计算次数
                    location[i, j] = k  # 记录最优括号划分

    # 打印矩阵最优乘法顺序
    print(backtrack(0, len(dim_number)-1, location, matrix_name_list))


def backtrack(begin, number, location, matrix_name_list):
    # 回溯，打印矩阵最优乘法顺序，即加括号
    if number < 2:
        return "(" + matrix_name_list[begin] + ")"
    else:
        cut_location = location[begin + 1, begin + number]  # 截断位置
        # 打印左半部分乘法顺序
        left = backtrack(begin, cut_location - begin, location, matrix_name_list)
        # 打印右半部分乘法顺序
        right = backtrack(cut_location, number - (cut_location - begin), location, matrix_name_list)
        return "(" + left + right + ")"


if __name__ == '__main__':
    matrix_chain_multiplication([3, 2, 4, 4])
