#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
import time, random
import numpy as np

def task(min_sleep,max_sleep):
    t = random.randint(min_sleep,max_sleep)+random.random()
    time.sleep(t)
    return t

def main():
    num_threads = 4
    executor = ThreadPoolExecutor(num_threads)
    threads = []
    for idx in range(0,num_threads):
        thread = executor.submit(task, min_sleep = 0, max_sleep = 3)
        threads.append(thread)
    
    terminate = False
    all_done = np.zeros(num_threads)
    tic = time.time()
    while not terminate:
        for count,thread in enumerate(threads):
            if thread.done():
                if not (all_done[count] == 1):
                    toc = time.time()
                    all_done[count] = 1
                    print(f'Thread {count} finished in {toc-tic} seconds with result {thread.result()}!')
        
        if np.sum(all_done) == num_threads:
            terminate = True

if __name__ == '__main__':
    try:
        main()
    finally:
        pass