Bank Robbery
============

The problem is here:

https://gist.github.com/mboes/040b60baa2b0e24ce668b6171db909c5


The discussion is here:

https://juan-gandhi.dreamwidth.org/5035606.html

Basically, we have a map of detectors, and need to find a path from the middle of the bottom to the middle of the top of the square with
minimal probability of detection. Each detector's probability of detection along 1 metre of path is a function of distance:

exp(-(pi * D / L)^2)

It is a little unclear in the problem description what this means. Our discussion indicates it probably means that if you travel along
an arc at the same distance D from the detector, the detector will detect with that probability.

The expression doesn't immediately look like Poisson distribution, so we make some assumptions about the meaning of the probability of
detection. We can make some sense of it, if this is the probability of being detected at least once. But to solve the problem, we need
the probability of non-detection, which we get like this:

From assumption that this is Poisson distribution, the probability of non-detection is:

exp(-lambda) = 1 - P(probability of detection at least once)

So we can compute: exp(-lambda) = 1 - exp(-(pi * D / L)^2)

Then the probability of non-detection along a small dx of the path is exp(-lambda * dx). If we choose dx to be very small, we can assume
that we are moving along a small arc, and the D remains constant.

Then the probability of non-detection by any of the detectors is the product of such probabilities, and the probability of non-detection
along the entire path is one more level of products. Instead of exponentiating and computing products, we can take a logarithm, and work
with sums. The nice property is that for the entire space split into small cells of size dx, dx is going to be a common multiplier for all
exponents, so to maximize non-detection we just maximize the sum.
