# Interval Scheduling
# input   : a list whose elements are list also
#           each element represent a task in format of [start_point, end_point, benefit]
# outputs :
#          index for all chosen tasks, which is sorted as an ascending array.
#          index start from 1 instead of 0
#
# Using   :
#         acts = [[0, 6, 2], [1, 4, 1], [3, 5, 3], [3, 8, 6],
#                 [4, 7, 8], [5, 9, 5], [6, 10, 6], [8, 11, 3]]
#         print(intervalSchedule(acts))

# Activity类，存储一个活动的输入标号id，开始时间s，结束时间f，收益w
class Activity:
    def __init__(self, id=0, start=0, finish=0, weight=0):
        self.id = id
        self.s = start
        self.f = finish
        self.w = weight


def intervalSchedule(act_list):
    # 列表acts存储所有Activity类的对象
    acts = []
    i = 1
    for act in act_list:
        acts.append(Activity(i, act[0], act[1], act[2]))
        i += 1
    # 所有活动按结束时间f从小到大排序
    acts = sorted(acts, key=lambda x:x.f)

    # pre[i]存储和acts[i]不冲突的活动中结束时间最晚的活动
    pre = [-1 for i in range(len(acts))]
    for i in range(0, len(acts)):
        for j in range(i-1, -1, -1):
            if acts[i].s >= acts[j].f:
                pre[i] = j
                break
    # 动态规划
    # 状态转移方程：dp[i] = max(dp[i-1], dp[pre[i]] + A[i].w)
    dp = [0 for i in range(len(acts))]
    dp[0] = acts[0].w
    for i in range(1, len(acts)):
        dp_pre = 0
        if pre[i] >= 0:
            dp_pre = dp[pre[i]]
        dp[i] = max(dp[i-1], dp_pre + acts[i].w)
    # 回溯
    # res存储算法所选中活动输入时的原标号id
    res = []
    n = len(acts) - 1
    while n > -1:
        if dp[n] != dp[n-1]:
            res.append(acts[n].id)
            n = pre[n]
        else:
            n -= 1
    return sorted(res)


if __name__ == '__main__':
    acts = [[0, 6, 2], [1, 4, 1], [3, 5, 3], [3, 8, 6],
            [4, 7, 8], [5, 9, 5], [6, 10, 6], [8, 11, 3]]
    print(intervalSchedule(acts))