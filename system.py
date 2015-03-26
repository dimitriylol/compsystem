# coding: utf-8
import time
from Queue import Queue
from threading import Thread
from random import *


class Task ():
    def __init__(self):
        self.lst_suitable_proc = Task.generate_suitable_proc()
        self.number_operations = Task.generate_number_operations()

    @staticmethod
    def generate_suitable_proc():
        lst = []
        for num in xrange(randint(0, 4)):   # if random return 0 -> task empty and won't execute
            lst.append(randint(0, 4))
        return lst

    @staticmethod
    def generate_number_operations(self):   # 200 because 200 ms is max time for execute task,
        return randint(100,200)             # so the dumbest processor will handle it. 100 - just my random


class Processor (Thread):
    def __init__(self, target, args, id, power):
        Thread.__init__(target=target, args=args)
        self.id = id
        self.power = power  # power - number of operations per ms
        self.start()

    def worker(self, task_queue):
        print "start work ", self.id, " processor"
        time.sleep(task_queue.get().number_operations/(self.power*1000)) # sleep() get in seconds, our task in ms
        task_queue.task_done()


# EXAMPLE OF USING QUEUE
def do_stuff(q):
  while True:
    print q.get()
    q.task_done()

q = Queue(maxsize=0)
num_threads = 10

for i in range(num_threads):
  worker = Thread(target=do_stuff, args=(q,))
  worker.setDaemon(True)
  worker.start()

for x in range(20):
  q.put(x)

q.join()
