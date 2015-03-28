# coding: utf-8
import time
from Queue import Queue
from threading import *
from random import *

queueLock = Lock()
workQueue = Queue(0)


def unique(lst):
    tmp = []
    for x in lst:
        if x not in tmp:
            tmp.append(x)
    return tmp


class Task ():
    def __init__(self):
        self.lst_suitable_proc = Task.generate_suitable_proc()
        self.number_operations = Task.generate_number_operations()

    @staticmethod
    def generate_suitable_proc():
        lst = []
        for num in xrange(5):   # if random return 0 -> task empty and won't execute
            if randint(0, 1):
                lst.append(randint(0, 4))
        return unique(lst)

    @staticmethod
    def generate_number_operations():   # 200 because 200 ms is max time for execute task,
        return randint(100, 200)             # so the dumbest processor will handle it. 100 - just my random


class TaskQueue(Thread):
    def __init__(self, time_for_filling):
        Thread.__init__(self)
        self.start_time = time.time()
        self.fill_time = time_for_filling      # in seconds
        self.done = False
        self.start()

    def pass_time(self, time_work):
        return time_work - self.start_time

    def run(self):  # fill TaskQueue
        while self.fill_time > self.pass_time(time.time()):
            queueLock.acquire()
            print "adding task to queue"
            workQueue.put(Task())
            print "END adding task to queue"
            queueLock.release()
            time.sleep(0.001)   # every milliseconds adding some task
        else:
            queueLock.acquire()
            self.done = True


class Processor (Thread):
    def __init__(self, proc_id, power, manage_queue):   # management - name function: FIFO and others algorithms
        Thread.__init__(self)
        self.id = proc_id
        self.power = power  # power - number of operations per ms
        self.manage_queue = manage_queue
        self.start()

    def run(self):
        while True:
            self.manage_queue(self.id, self.power)


def fifo(id_proc, power):
    "get first task and try execute by id_proc"
    queueLock.acquire()
    if not workQueue.empty():
        task = workQueue.get()
        if id_proc in task.lst_suitable_proc:
            print "working ", id_proc, " processor"
            queueLock.release()
            time.sleep(task.number_operations/(power*1000))     # sleep() get in seconds, our task in ms
        else:
            workQueue.put(task)
            queueLock.release()
    else:
        print "Queue empty"
        queueLock.release()
        time.sleep(0.001)   # time for wedged to queue by another processor


def main_func_fifo():
    lst_processors = []
    power = 2       # just my stupid decision, that power of processor will be 2, 4, 6, 8, 10
    task_queue = TaskQueue(3)      # will append task to queue for 10 seconds, another my random
    for x in xrange(5):
        lst_processors.append(Processor(x, power, fifo))
        power += 2
    while not task_queue.done:  # wait for passing 10 seconds
        pass
    print "end of everything!"
    return

main_func_fifo()
