#!/usr/bin/env python3

from multiprocessing import Process
from multiprocessing import Pool
import time, random
import numpy as np

def task(max_sleep):
    min_sleep = 0.
    time_val = random.randint(min_sleep,max_sleep)+random.random()
    time.sleep(time_val)
    return time_val

class Data():
    val = []

def main():
    num_threads = 4
    # threads = []
    # data = Data()

    # for idx in range(0,num_threads):
    #     thread = Process(target=task,args=(0,2,data,))
    #     thread.start()
    #     threads.append(thread)

    # terminate = False
    # all_done = np.zeros(num_threads)
    # tic = time.time()
    # while not terminate:
    #     for count,thread in enumerate(threads):
    #         if not thread.is_alive():
    #             if not (all_done[count] == 1):
    #                 toc = time.time()
    #                 all_done[count] = 1
    #                 print(f'Thread {count} finished in {toc-tic} seconds!')
        
    #     if np.sum(all_done) == num_threads:
    #         terminate = True

    # print(f'Data: {data.val}')

    p = Pool(num_threads)
    r = p.map(task,[2,2,2,2])
    print(r)

if __name__ == '__main__':
    try:
        main()
    finally:
        pass