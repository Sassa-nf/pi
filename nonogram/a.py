# https://www.codewars.com/kata/5a5519858803853691000069/train/python
#
# given clues, work out the answer:
#
# suppose, there is a matrix of cells, each containing a 1 or 0. work out what this matrix is, given 
# clues for all rows and columns.
#
# clues tell you how many contiguous cells are 1, there is at least one 0 between contiguous runs of 1s.
# there is only one answer. find it.

def get_puzzles():

    v_clues = ((1, 1, 1),(2,))
    h_clues = ((1,), (), (1,), (), (1,), (2,), (), ())
    args = ((v_clues, h_clues), len(v_clues), len(h_clues))

    ans = ((1,0),
           (0,0),
           (1,0),
           (0,0),
           (0,1),
           (1,1),
           (0,0),
           (0,0))
    
    t0 = (args, ans, '1 x 5 puzzle')




    v_clues = ((1, 1), (4,), (1, 1, 1), (3,), (1,))
    h_clues = ((1,), (2,), (3,), (2, 1), (4,))
    args = ((v_clues, h_clues), 5, 5)

    ans = ((0, 0, 1, 0, 0),
           (1, 1, 0, 0, 0),
           (0, 1, 1, 1, 0),
           (1, 1, 0, 1, 0),
           (0, 1, 1, 1, 1))
    
    t1 = (args, ans, '5 x 5 puzzle')



    v_clues = ((3,), (4,), (2, 2, 2), (2, 4, 2), (6,), (3,))
    h_clues = ((4,), (6,), (2, 2), (2, 2), (2,), (2,), (2,), (2,), (), (2,), (2,))
    args = ((v_clues, h_clues), 6, 11)
    
    ans = ((0, 1, 1, 1, 1, 0),
           (1, 1, 1, 1, 1, 1),
           (1, 1, 0, 0, 1, 1),
           (1, 1, 0, 0, 1, 1),
           (0, 0, 0, 1, 1, 0),
           (0, 0, 0, 1, 1, 0),
           (0, 0, 1, 1, 0, 0),
           (0, 0, 1, 1, 0, 0),
           (0, 0, 0, 0, 0, 0),
           (0, 0, 1, 1, 0, 0),
           (0, 0, 1, 1, 0, 0))

    t2 = (args, ans, '6 x 11 puzzle')
    
    
    
    v_clues = ((1, 1, 3), (3, 2, 1, 3), (2, 2), (3, 6, 3),
               (3, 8, 2), (15,), (8, 5), (15,),
               (7, 1, 4, 2), (7, 9,), (6, 4, 2,), (2, 1, 5, 4),
               (6, 4), (2, 6), (2, 5), (5, 2, 1),
               (6, 1), (3, 1), (1, 4, 2, 1), (2, 2, 2, 2))
    h_clues = ((2, 1, 1), (3, 4, 2), (4, 4, 2), (8, 3),
               (7, 2, 2), (7, 5), (9, 4), (8, 2, 3),
               (7, 1, 1), (6, 2), (5, 3), (3, 6, 3),
               (2, 9, 2), (1, 8), (1, 6, 1), (3, 1, 6),
               (5, 5), (1, 3, 8), (1, 2, 6, 1), (1, 1, 1, 3, 2))
    args = ((v_clues, h_clues), 20, 20)
    
    ans = ((1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
           (0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1),
           (1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0),
           (0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0),
           (0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1),
           (0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1),
           (0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0),
           (0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0),
           (0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0),
           (0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0),
           (0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0),
           (0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1),
           (1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1),
           (1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0),
           (1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0),
           (0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0),
           (0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0),
           (0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0),
           (0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1),
           (0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1))
    
    t3 = (args, ans, '20 x 20 puzzle')
    
    tests = [t2, t0, t1, t2, t3]
    return tests

#

def solve(clues, width, height):
    # append a fake column and row, so a series of ones always starts with a 0
    solution = [[(0,0,0,0)] * (width + 1)] + [[(0,0,0,0)] + ([0] * width) for _ in range(height)]
    vclues, hclues = clues
    hclues = [[0]] + [[0] + list(hclue) for hclue in hclues]
    vclues = [[0]] + [[0] + list(vclue) for vclue in vclues]

    c = 1
    fits = True
    while c <= width:
        fits = fit_v(solution, c, vclues, hclues, fits)
        c += 1 if fits else -1

    # strip the fake row and column added at the beginning
    solution = [[1 if hl < hclue[hr] else 0 for _, _, hr, hl in s[1:]] for s, hclue in zip(solution[1:], hclues[1:])]
    return tuple([tuple(r) for r in solution])

def fit_v(solution, c, vclues, hclues, fits):
    width = len(solution[0])
    height = len(solution)
    vclue = vclues[c]
    r = 1 if fits else height - solution[-1][c][1] - 1
    while r > 0:
        #print_sol(solution, vclues, hclues, c, r, 0)
        #print('try col %d row %d' % (c, r))
        vr, vl = solution[r-1][c][:2]
        #print(' vr=%d, %d' % (vr, vl))
        if vr < len(vclue) and vl < vclue[vr] or vr + 1 == len(vclue) or not fits:
            vl += 1
            #print(' try extend %d %d: %s' % (vr, vl, vclue))
        else:
            vr += 1
            # check that the remaining ones can still fit in the remaining rows
            vc = vclue[vr:]
            min_len = sum(vc)+len(vc)-1
            #print(' try next run %d: %s\n min_len: %d' % (vr, vclue[vr], min_len))
            if r + min_len > height:
                #print(' the remainder does not fit; redo; %d+%d-1+%d >= %d' % (sum(vc), len(vc), r, height))
                r -= vl+1
                #print_sol(solution, vclues, hclues, c, r, vl+1)
                #if r > 0:
                #    vl = solution[r-1][c][1]
                #    r -= vl
                #    print_sol(solution, vclues, hclues, c, r, vl)
                fits = False
                continue

            vl = 0

        isOne = vl < vclue[vr]
        hr, hl = solution[r][c-1][2:]
        hclue = hclues[r]
        fits = False
        #print(' hr=%d, %d: %s' % (hr, hl, hclue))
        if isOne:
            if hl < hclue[hr]:
                hl += 1
                fits = hl < hclue[hr]
                #print(' try extend ones %d: %s; fits: %s' % (hr, hclue, fits))
            else:
                hr += 1
                hl = 0
                fits = hr < len(hclue)
                #print(' try next run %d: fits: %s' % (hr, fits))
                # check that the remaining ones can still fit in the remaining columns
                if fits:
                    hc = hclue[hr:]
                    min_len = sum(hc)+len(hc)-1
                    fits = c + min_len <= width
                    #print(' try min_len %d: fits: %s' % (min_len, fits))
        else:
            hl += 1
            fits = hl >= hclue[hr]
            #print(' try extend zeros %d: %s; fits: %s' % (hr, hclue, fits))

        if fits:
            solution[r][c] = (vr, vl, hr, hl)
            r += 1
            if r == height:
                #print('-----------------')
                #print('fits: %s' % ([s[c] for s in solution[:r]],))
                return True
        else:
            r -= vl
            #print(' does not fit; fall back to row %d: back %d' % (r, vl))
            #print_sol(solution, vclues, hclues, c, r, vl)
        #print('-----------------')
    return False

def print_sol(solution, vclues, hclues, c, r, vl):
  print('---------------')

  def f(xs, l, ch):
    ys = ['1' if xs[i][1] < vclues[i][xs[i][0]] else '0' for i in range(len(xs))]
    return ys + [ch] + (['-'] * (l-len(xs)))

  ss = ([f(row[:c+1], len(row), '-') for row in solution[:r]] +
        [f(row[:c], len(row), 'X') for row in solution[r:r+vl]] +
        [f(row[:c], len(row), '-') for row in solution[r+vl:]])
  for row in ss:
    print(' '.join(row))

for args, ans, n in get_puzzles():
    a = solve(*args)
    if a != ans:
      print('%s: fail\ngot: %s\nwant: %s' % (n, a, ans))

print('Done')
