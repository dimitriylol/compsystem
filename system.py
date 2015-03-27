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
    def __generate_suitable_proc():
        lst = []
        for num in xrange(5):   # if random return 0 -> task empty and won't execute
            if randint(0, 1):
                lst.append(randint(0, 4))
        return unique(lst)

    @staticmethod
    def __generate_number_operations(self):   # 200 because 200 ms is max time for execute task,
        return randint(100, 100)             # so the dumbest processor will handle it. 100 - just my random


class TaskQueue(Thread):
    def __init__(self, time_for_filling):
        Thread.__init__()
        self.start_time = time.time()
        self.fill_time = time_for_filling      # in seconds
        self.done = False
        self.start()

    @staticmethod
    def __pass_time(time_work):
        return time_work - TaskQueue.start_time

    def run(self):  # fill TaskQueue
        while self.fill_time > self.pass_time(time.time()):
            queueLock.acquire()
            workQueue.put(Task())
            queueLock.release()
            time.sleep(0.001)   # every milliseconds adding some task
        else:
            queueLock.acquire()
            self.done = True


class Processor (Thread):
    def __init__(self, proc_id, power, manage_queue):   # management - name function: FIFO and others algorithms
        Thread.__init__()
        self.__id = proc_id
        self.__power = power  # power - number of operations per ms
        self.__manage_queue = manage_queue
        self.start()

    def run(self):
        print "start work ", self.id, " processor"
        while True:
            self.manage_queue(self.__id, self.__power)
        print "end work ", self.id, " processor"


def fifo(id_proc, power):
    "get first task and try execute by id_proc"
    queueLock.acquire()
    if not workQueue.empty():
        task = workQueue.get()
    if id_proc in task.lst_suitable_proc:
        queueLock.release()
        time.sleep(task.number_operations/(power*1000))     # sleep() get in seconds, our task in ms
    else:
        workQueue.put(task)
        queueLock.release()
        time.sleep(0.001)   # time for wedged to queue by another processor


def main_func_fifo():
    lst_processors = []
    power = 2       # just my stupid decision, that power of processor will be 2, 4, 6, 8, 10
    task_queue = TaskQueue(10)      # will append task to queue for 10 seconds, another my random
    for x in xrange(5):
        lst_processors.append(Processor(x, power, fifo))
        power += 2
    while not task_queue.done:  # wait for passing 10 seconds
        pass
