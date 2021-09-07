# Knaspack using Dynamic Programming
# input   : int weight limit
#           list weights : weight of each package
#           list costs   : value of each package correspondingly
# output  : the index of package that maximize the total value
# warning : index start from 1 instead of 0
# Using   :
# sample input :
#               weight = 11
#               weights = [1, 2, 5, 6, 7]
#               values = [1, 6, 18, 22, 28]
#               knapsack(weight, weights, values)
# sample output :
#               3
#               4


# 动态规划计算背包问题
def knapsack(weight, weights, costs):
    """
        动态规划，时间复杂度O(weight * count), 空间复杂度O(weight)
        count: 物品数量
        weight: 背包最大能装的重量
        weights: 每件物品的重量
        costs: 每件物品的价值
        dp 动态规划数组，方便回溯选择的物品
    """
    count = len(weights)
    dp = [[-1 for _ in range(weight + 1)] for _ in range(count + 1)]
    for j in range(weight + 1):
        dp[0][j] = 0
    for i in range(1, count + 1):
        for j in range(1, weight + 1):
            dp[i][j] = dp[i - 1][j]
            if j >= weights[i - 1] and dp[i][j] < dp[i - 1][j - weights[i - 1]] + costs[i - 1]:
                dp[i][j] = dp[i - 1][j - weights[i - 1]] + costs[i - 1]
    return show(weight, weights, dp)


# 根据结果回溯出物品选择
def show(weight, weights, dp):
    """
        时间复杂度O(count)
        weight: 背包最大能装的重量
        weights: 每件物品的重量
        dp 动态规划数组，方便回溯选择的物品
    """
    n = len(weights)
    x = [False for _ in range(n)]
    j = weight
    for i in range(n, 0, -1):
        if dp[i][j] > dp[i - 1][j]:
            x[i-1] = True
            j -= weights[i-1]
    for i in range(n):
        if x[i]:
            print(i + 1)


if __name__ == '__main__':
    weight = 11
    weights = [1, 2, 5, 6, 7]
    values = [1, 6, 18, 22, 28]
    knapsack(weight, weights, values)

