def removeDuplicates(nums: list[int]) -> int:
    comp = 0
    pos = 1
    for i in range(1, len(nums)):
        if nums[comp] != nums[i]:
            nums[pos], nums[i] = nums[i], nums[pos]
            comp = pos
            pos += 1
    return len(set(nums))


print(removeDuplicates([0, 0, 1, 1, 1, 2, 2, 3, 3, 4]))
