def largestDivisibleSet(nums):
   nums.sort()
   divs = [[n for n in nums[i:] if n % nums[i] == 0] for i in range(len(nums))]
   divs.reverse()
