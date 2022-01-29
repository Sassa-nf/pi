#long maxnum = 10000000;
#
#int minSumOfLengths(vector<int>& arr, long target) {
#    vector<long> chains_end;
#    chains_end.resize(arr.size(), -1);
#
#    long len_best = maxnum;
#    vector<long> len2_best(arr.size() + 1, maxnum);
#
#    long sum = 0;
#    long jbeg = 0;
#    for (long i = 0; i < arr.size(); ++i) {
#        bool f_passed = false;
#        for (long j = jbeg; j < arr.size(); ++j) {
#            sum += arr[j];
#
#            if (sum == target) {
#                chains_end[i] = j;
#            }
#
#            if (sum >= target) {
#                jbeg = j;
#                sum -= arr[i] + arr[j];
#                f_passed = true;
#                break;
#            }
#        }
#
#        if (!f_passed) jbeg = arr.size();
#    }
#
#    for (long i = chains_end.size() - 1; i >= 0; --i){
#        if (chains_end[i] >= 0) {
#            long ch_len = chains_end[i] - i + 1;
#
#            long len = ch_len + len2_best[chains_end[i] + 1];
#            if (len < len_best) len_best = len;
#
#            if (ch_len < len2_best[i]) len2_best[i] = ch_len;
#        }
#
#        if(len2_best[i] > len2_best[i + 1]) len2_best[i] = len2_best[i + 1];
#    }
#
#    return (len_best < maxnum) ? len_best : -1;
#}

maxnum = 10000000

def minSumOfLengths(arr, target):
    chains_end = [-1] * len(arr)

    len_best = maxnum
    len2_best = [maxnum] * (len(arr) + 1)

    sum = 0
    jbeg = 0
    for i in range(len(arr)):
        f_passed = False
        for j in range(jbeg, len(arr)):
            sum += arr[j]

            if sum == target:
                chains_end[i] = j

            if sum >= target:
                jbeg = j
                sum -= arr[i] + arr[j]
                f_passed = True
                break

        if not f_passed:
           jbeg = len(arr)

    i = len(chains_end) - 1
    while i >= 0:
        if chains_end[i] >= 0:
            ch_len = chains_end[i] - i + 1

            llen = ch_len + len2_best[chains_end[i] + 1]
            if llen < len_best:
               len_best = llen

            if ch_len < len2_best[i]:
               len2_best[i] = ch_len

        if len2_best[i] > len2_best[i + 1]:
           len2_best[i] = len2_best[i + 1]
        i -= 1

    return len_best if len_best < maxnum else -1

i = [4, 1, 1, 2, 2]
t = 4
print(minSumOfLengths(i, t))

#i = [1000] * 1000000 + [1, 999] + [1000] * 499999
#t = 500000000

i = [4] * 6 + [1, 1] + [2] * 9
t = 20
print(minSumOfLengths(i, t))
