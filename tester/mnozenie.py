import os
import subprocess
import sys

file = "test16.txt"

def calc_res(v0, v1):
    process=subprocess.Popen(['./maszyna_wirtualna/maszyna-wirtualna', f'output/{file}'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    string = str(v0) + "\n" + str(v1) + "\n"
    arr = bytes(string, 'utf-8')
    out, _ = process.communicate(input=arr)
    s = str(out).split("\\n")
    res = int(s[3][6:].replace(" ", ""))
    cost = int(s[4][49:].split("\\")[0].replace(" ", ""))
    return res, cost

if __name__ == "__main__":
    # print(calc_res(1000000, 550000))
    sum_cost = 0
    for i in range(20):
        for j in range(20):
            res, cost = calc_res(i, j)
            act_res = i * j
            if res != act_res:
                print("BLAD DLA i=" + str(i) + " j=" + str(j))
            sum_cost += cost
    lis = [(2, 1000000), (0, 1000000), (10000000, 0), (1000000, 10000000), (20, 200000), (100, 100), (5000, 5000)]
    for i, j in lis:
        res, cost = calc_res(i, j)
        act_res = i * j
        if res != act_res:
            print("BLAD DLA i=" + str(i) + " j=" + str(j))
        sum_cost += cost
    print("cost: " + str(sum_cost))