import os
import subprocess
import sys

file = "test19.txt"

def calc_res(v0):
    process=subprocess.Popen(['./maszyna_wirtualna/maszyna-wirtualna', f'output/{file}'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    string = str(v0) + "\n"
    arr = bytes(string, 'utf-8')
    out, _ = process.communicate(input=arr)
    s = str(out).split("\\n")
    res = int(s[3][4:].replace(" ", ""))
    cost = int(s[4][49:].split("\\")[0].replace(" ", ""))
    return res, cost

if __name__ == "__main__":
    # print(calc_res(1000000, 550000))
    sum_cost = 0
    for i in range(500):
        res, cost = calc_res(i)
        act_res = 1 // i if i != 0 else 0
        if res != act_res:
            print("BLAD DLA i=" + str(i))
        sum_cost += cost
    for i in range(500, 1000000, 5000):
        res, cost = calc_res(i)
        act_res = 1 // i if i != 0 else 0
        if res != act_res:
            print("BLAD DLA i=" + str(i))
        sum_cost += cost
    print("cost: " + str(sum_cost))