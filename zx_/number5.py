def combination_sum(nums, n, target):
    result = []
    nums.sort()  # 排序是为了提高搜索效率
    backtrack(nums, n, target, 0, [], result)
    return result


def backtrack(nums, n, target, start, path, result):
    if target == 0 and len(path) == n:
        result.append(path.copy())
        return
    if target < 0 or len(path) >= n:
        return

    for i in range(start, len(nums)):
        # 避免重复选择相同的元素
        if i > start and nums[i] == nums[i - 1]:
            continue
        path.append(i)
        backtrack(nums, n, target - nums[i], i + 1, path, result)
        path.pop()


# 示例输入
nums = [3, 2, 4, 5, 7]
n = 3
target = 10

result = combination_sum(nums, n, target)
print(result)
