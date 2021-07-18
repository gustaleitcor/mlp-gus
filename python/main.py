#! /usr/bin/python3

import time
from read import *
from random import randint
import math

EPSILON = 0.00000000000001

SWAP        = 0
TWO_OPT     = 1
REINSERTION = 2
OR_OPT_2    = 3
OR_OPT_3    = 4

n, m = get_instance_info()

W = "W"
T = "T"
C = "C"

improv_flag = None

def subseq_info_fill(n):
    matrix = {
            W:[],
            T:[],
            C:[]
            }

    for i in range(n+1):
        matrix[W].append([])
        matrix[T].append([])
        matrix[C].append([])
        for j in range(n+1):
            matrix[W][i].append(0.0)
            matrix[T][i].append(0.0)
            matrix[C][i].append(0.0)

    return matrix

def construction(alpha):
    s = [0]
    c_list = []
    for i in range(1, n):
        c_list.append(i)

    r = 0
    while len(c_list) > 0:

        i = int(len(c_list)*alpha) + 1

        c_list = sorted(c_list, key = lambda n : m[n][r], reverse=False)

        c = c_list[randint(0, i-1)]
        s.append(c)
        r = c
        c_list.remove(c)

    s.append(0)

    return s

def subseq_info_load(sol, seq):
    i = 0
    d = n + 1
    while i < d:
        k = 1 - i - int(not i)

        seq[T][i][i] = 0.0
        seq[C][i][i] = 0.0
        seq[W][i][i] = int(not (i == 0))

        j = i + 1
        while j < d:
            a = j - 1

            seq[T][i][j] = m[sol[a]][sol[j]] + seq[T][i][a]
            seq[C][i][j] = seq[T][i][j] + seq[C][i][a]
            seq[W][i][j] = j + k

            seq[T][j][i] = seq[T][i][j]
            seq[C][j][i] = seq[C][i][j]
            seq[W][j][i] = seq[W][i][j]

            j += 1

        i += 1

def swap(s, i, j):
    s[i], s[j] = s[j], s[i]

def reverse(s, i, j):
    s[i:j+1] = s[i:j+1][::-1]

def reinsert(s, i, j, pos):
    if i < pos:
        s[pos:pos] = s[i:j+1]
        s[:] = s[:i] + s[j+1:]
    else:
        sub = s[i:j+1]
        s[:] = s[:i] + s[j+1:]
        s[pos:pos] = sub


def search_swap(s, seq):
    cost_best = float('inf')
    I = None
    J = None

    for i in range(1, (n-1) ):
        i_prev = i - 1
        i_next = i + 1

        total = seq[T][0][i_prev] + m[s[i_prev]][s[i_next]]

        cost = seq[C][0][i_prev] + seq[W][i][i_next] * (total) + m[s[i_next]][s[i]]
        cost += seq[W][i_next+1][n] * (total + seq[T][i][i_next] + m[s[i]][s[i_next+1]]) + seq[C][i_next+1][n]

        if cost < cost_best:
            cost_best = cost - EPSILON
            I = i
            J = i_next

        #if i == n-2:
        #    continue

        for j in range(i_next+1, (n)):
            j_next = j + 1
            j_prev = j - 1

            total_1 = seq[T][0][i_prev] + m[s[i_prev]][s[j]]
            total_2 = total_1 + m[s[j]][s[i_next]]
            total_3 = total_2 + seq[T][i_next][j_prev] + m[s[j_prev]][s[i]]
            total_4 = total_3 + m[s[i]][s[j_next]]

            cost = seq[C][0][i_prev] + total_1 + seq[W][i_next][j_prev] * total_2 + seq[C][i_next][j_prev] + total_3 + seq[W][j_next][n] * total_4 + seq[C][j_next][n]
            if cost < cost_best:
                cost_best = cost - EPSILON
                I = i
                J = j


    if cost_best < seq[C][0][n] - EPSILON:
        swap(s, I, J)
        subseq_info_load(s, seq)
        global improv_flag
        improv_flag = True

def search_two_opt(s, seq):
    cost_best = float('inf')

    for i in range(1, n-1):
        i_prev = i - 1
        for j in range(i+2, n):
            j_next = j + 1

            total = seq[T][0][i_prev] + m[s[j]][s[i_prev]]

            cost = seq[C][0][i_prev] + seq[W][i][j] * total + sum([seq[T][x][j] for x in range(i, j)])
            cost += seq[W][j_next][n] * (total + seq[T][i][j] + m[s[j_next]][s[i]]) + seq[C][j_next][n]

            if cost < cost_best:
                cost_best = cost - EPSILON
                I = i
                J = j

    if cost_best < seq[C][0][n] - EPSILON:
        reverse(s, I, J)
        subseq_info_load(s, seq)
        global improv_flag
        improv_flag = True


def search_reinsertion(s, seq, OPT):
    cost_best = float('inf')
    I = None
    J = None
    POS = None
    opt = OPT - 1 

    for i in range(1, n - opt + 1):
        j = opt + i - 1

        j_next = j+1
        i_prev = i-1

        for k in range(0, i_prev):
            k_next = k+1

            total_1 = seq[T][0][k] + m[s[k]][s[i]]
            total_2 = total_1 + seq[T][i][j] + m[s[j]][s[k_next]]

            cost = seq[C][0][k] + seq[W][i][j] * total_1 + seq[C][i][j]
            cost += seq[W][k_next][i_prev] * total_2 + seq[C][k_next][i_prev]
            cost += seq[W][j_next][n] * (total_2 + seq[T][k_next][i_prev] + m[s[i_prev]][s[j_next]]) + seq[C][j_next][n]

            if cost < cost_best:
                cost_best = cost - EPSILON
                I = i
                J = j
                POS = k

        for k in range(i+opt, n - opt - 1):
            k_next = k+1

            total_1 = seq[T][0][i_prev] + m[s[i_prev]][s[j_next]]
            total_2 = total_1 + seq[T][j_next][k] + m[s[k]][s[i]]

            cost = seq[C][0][i_prev] + seq[W][j_next][k] * total_1 + seq[C][j_next][k]
            cost += seq[W][i][j] * total_2 + seq[C][i][j]
            cost += seq[W][k_next][n] * (total_2 + seq[T][i][j] + m[s[j]][s[k_next]]) + seq[C][k_next][n]

            if cost < cost_best:
                cost_best = cost - EPSILON
                I = i
                J = j
                POS = k



    if cost_best < seq[C][0][n] - EPSILON:
        reinsert(s, I, J, POS+1)
        subseq_info_load(s, seq)
        global improv_flag
        improv_flag = True

def RVND(s, subseq):

    neighbd_list = [SWAP, TWO_OPT, REINSERTION, OR_OPT_2, OR_OPT_3]

    while len(neighbd_list) > 0:
        i = randint(0, len(neighbd_list)-1)
        neighbd = neighbd_list[i]

        global improv_flag
        improv_flag = False

        if neighbd == SWAP:
            search_swap(s, subseq)
        elif neighbd == TWO_OPT:
            search_two_opt(s, subseq)
        elif neighbd == REINSERTION:
            search_reinsertion(s, subseq, REINSERTION)
        elif neighbd == OR_OPT_2:
            search_reinsertion(s, subseq, OR_OPT_2)
        elif neighbd == OR_OPT_3:
            search_reinsertion(s, subseq, OR_OPT_3)


        if improv_flag == True:
            neighbd_list.clear()
            neighbd_list = [SWAP, TWO_OPT, REINSERTION, OR_OPT_2, OR_OPT_3]
        else:
            neighbd_list.pop(i)

    return s

def perturb(sl):
    s = sl.copy()
    A_start, A_end = 1, 1
    B_start, B_end = 1, 1

    size_max = math.floor(len(s)/10) if math.floor(len(s)/10) >= 2 else 2
    size_min = 2

    while (A_start <= B_start and B_start <= A_end) or (B_start <= A_start and A_start <= B_end):
        A_start = randint(1, len(s) - 1 - size_max)
        A_end = A_start + randint(size_min, size_max)

        B_start = randint(1, len(s) - 1 - size_max)
        B_end = B_start + randint(size_min, size_max)

    if A_start < B_start:
        reinsert(s, B_start, B_end-1, A_end)
        reinsert(s, A_start, A_end-1, B_end )
    else:
        reinsert(s, A_start, A_end-1, B_end)
        reinsert(s, B_start, B_end-1, A_end )


    return s

def GILS_RVND(Imax, Iils, R):

    cost_best = float('inf')
    s_best = []

    subseq = subseq_info_fill(n)

    for i in range(Imax):
        alpha = R[randint(0, len(R)-1)]

        print("[+] Local Search {}".format(i+1))
        print("\t[+] Constructing Inital Solution..")
        s = construction(alpha)
        subseq_info_load(s, subseq)
        #print(subseq[C][0][n])
        #exit(1)
        sl = s.copy()
        rvnd_cost_best = subseq[C][0][n] - EPSILON

        print("\t[+] Looking for the best Neighbor..")
        iterILS = 0
        while iterILS < Iils:
            RVND(s, subseq)
            rvnd_cost_crnt  = subseq[C][0][n] - EPSILON
            if rvnd_cost_crnt < rvnd_cost_best:
                rvnd_cost_best = rvnd_cost_crnt
                #print("cost best ", rvnd_cost_best)
                sl = s.copy()
                #print("   SL ", sl)
                iterILS = 0

            s = perturb(sl)
            #print("   Perturb", s)
            subseq_info_load(s, subseq)
            #print("   ", subseq[C][0][n])
            iterILS += 1


        #print(i, " Iteracoes")
        subseq_info_load(sl, subseq)
        sl_cost = subseq[C][0][n] - EPSILON
        #print("Sl cost", sl_cost)

        if sl_cost < cost_best:
            s_best = sl
            cost_best = sl_cost

        print("\tCurrent best solution cost: ", cost_best)

    print("COST: ", cost_best)




def main():

    R = [0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.25]

    Imax = 10
    Iils = min(n, 100)
    #Iils = int(n/2) if n >= 150 else n

    GILS_RVND(Imax, Iils, R)

start = time.time()
main()
print("TEMPO %s " % (time.time() - start))