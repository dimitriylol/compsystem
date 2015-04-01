# coding: utf-8
import time
from Queue import Queue
from threading import *
from random import *


def unique(lst):
    tmp = []
    for x in lst:
        if x not in tmp:
            tmp.append(x)
    return tmp


class Task ():
    def __init__(self, *args):
        self.lst_suitable_proc = Task.generate_suitable_proc(args)
        self.number_operations = Task.generate_number_operations(args)

    @staticmethod
    def generate_suitable_proc(args):
        lst = []
        for num in xrange(5):
            lst.append(randint(0, 4))
        return unique(lst)

    @staticmethod
    def generate_number_operations(args):   # 200 because 200 ms is max time for execute task,
        return randint(100, 200)             # so the dumbest processor will handle it. 100 - just my random


class TaskQueue(Thread):
    def __init__(self, time_for_filling, queue, queue_lock):
        Thread.__init__(self)
        self.start_time = time.time()
        self.fill_time = time_for_filling      # in seconds
        self.done = False
        self.queue = queue
        self.queue_lock = queue_lock
        self.start()

    def pass_time(self, time_work):
        return time_work - self.start_time

    def run(self):  # fill TaskQueue
        while self.fill_time > self.pass_time(time.time()):
            self.queue_lock.acquire()
            print "lock queue by Task"
            print "adding task to queue"
            if randint(0, 1):
                self.queue.put(Task())
            else:
                print "task wasn't added"
            self.queue_lock.release()
            time.sleep(0.001)   # every milliseconds adding some task
        else:
            self.queue_lock.acquire()
            self.done = True


class Processor (Thread):
    def __init__(self, proc_id, power, manage_queue, queue_lock, cond, queue):
        Thread.__init__(self)
        self.id = proc_id
        self.power = power  # power - number of operations per ms
        self.manage_queue = manage_queue
        self.queue_lock = queue_lock
        self.control = cond
        self.queue = queue
        self.done_operations = 0
        self.daemon = True

    def run(self):
        while True:
            self.manage_queue(self)


class WorkerProcessor (Processor):
    def __init__(self, proc_id, power, manage_queue, queue_lock, cond, queue):
        Processor.__init__(self, proc_id, power, manage_queue, queue_lock, cond, queue)
        self.task = False
        self.start()

    def fifo(self):
        """get first task and try execute by self.id_proc"""
        self.queue_lock.acquire()
        if not self.queue.empty():
            task = self.queue.get()
            if self.id in task.lst_suitable_proc:
                print "working ", self.id, " processor. Suitable are", task.lst_suitable_proc
                self.queue_lock.release()
                self.done_operations += task.number_operations
                time.sleep(task.number_operations/(self.power*1000))     # sleep() get in seconds, our task in ms
            else:
                self.queue.put(task)
                self.queue_lock.release()
        else:
            # print "Queue empty"
            self.queue_lock.release()

    def worker_planner(self):   # control is pair of conditional and lock for queue
        """worker_planner just executing task when condition is send"""
        print "Lock cond for worker %s" % self.id
        self.control.acquire()
        self.control.wait()
        print "GET NOTIFY in worker", self.id
        print "task is", self.task
        self.done_operations += self.task.number_operations
        time.sleep(self.task.number_operations/(self.power*1000))     # sleep() get in seconds, our task in ms
        self.task = False
        self.control.release()


class PlanningProcessor (Processor):
    def __init__(self, proc_id, manage_queue, queue_lock, lst_cond, lst_processors, queue):
        Processor.__init__(self, proc_id, 0, manage_queue, queue_lock, lst_cond, queue)
        self.task = True
        self.lst_processors = lst_processors
        self.start()

    def planner_helper(self, lst_task):   # return True if sends task to processors and False if doesn't
        task_send = False
        print "list of tasks", lst_task
        print "begin planner helper; finding suitable proc in", lst_task[0].lst_suitable_proc
        for id_suitable_proc in lst_task[-1].lst_suitable_proc:
            if not self.lst_processors[id_suitable_proc].task:
                self.lst_processors[id_suitable_proc].task = lst_task.pop()
                task_send = True
                map(lambda item: self.queue.put(item), lst_task)
                print "find not busy processor", id_suitable_proc, " and sending notify to worker"
                self.control[id_suitable_proc].acquire()
                self.control[id_suitable_proc].notify()
                self.control[id_suitable_proc].release()
                break
            else:
                print "This processor is busy", id_suitable_proc
        if not self.queue.empty():
            if task_send:
                return True
            else:
                print "not find free processor for that task"
                lst_task.append(self.queue.get())
                self.planner_helper(lst_task)
        else:       # if sort out all queue and won't be free suitable processors. HIGHLY UNLIKELY
            print "Queue has task only for busy processors"
            map(lambda item: self.queue.put(item), lst_task)
            return False

    def planner(self):      # control is list of conditions and lock for queue
        """planner finds suitable free processors and send condition to work"""
        self.queue_lock.acquire()
        print "lock queue by planner"
        if not self.queue.empty():
            task = self.queue.get()
            if isinstance(task, Task):          # left for debug
                self.planner_helper([task])
            else:
                print "Fucking bug! task is", task
            print "unlock queue by planner"
            self.queue_lock.release()     # release queue
            time.sleep(0.001)
        else:
            print "Queue empty"
            print "unlock queue by planner"
            self.queue_lock.release()     # release queue
            time.sleep(0.001)   # time for wedged to queue by TaskQueue


def main_func_planner(lst_power):
    lst_cond = [Condition(Lock()) for x in xrange(5)]
    index_min_elem = lst_power.index(min(lst_power))
    lst_power[index_min_elem] = 0
    lst_processors = []
    queue_lock = Lock()
    work_queue = Queue()
    task_queue = TaskQueue(1, work_queue, queue_lock)
    queue_lock.acquire()
    for x in xrange(5):
        if lst_power[x] == 0:
            lst_processors.append(PlanningProcessor(x,
                                                    PlanningProcessor.planner,
                                                    queue_lock,
                                                    lst_cond,
                                                    lst_processors,
                                                    work_queue))
        else:
            lst_processors.append(WorkerProcessor(x,
                                                  lst_power[x],
                                                  WorkerProcessor.worker_planner,
                                                  queue_lock,
                                                  lst_cond[x],
                                                  work_queue))
    queue_lock.release()
    while not task_queue.done:  # wait for passing 10 seconds
        pass
    print "end of everything!"
    result_operations = 0
    for x in lst_processors:
        result_operations += x.done_operations
    print "Result is", result_operations
    return


def main_func_fifo(lst_power):
    queue_lock = Lock()
    work_queue = Queue()
    lst_processors = []
    task_queue = TaskQueue(1, work_queue, queue_lock)      # will append task to queue for 3 seconds, another my random
    for x in xrange(5):
        lst_processors.append(WorkerProcessor(x,
                                              lst_power[x],
                                              WorkerProcessor.fifo,
                                              queue_lock,
                                              None,
                                              work_queue))
    while not task_queue.done:  # wait for passing 10 seconds
        pass
    print "end of everything!"
    result_operations = 0
    for x in lst_processors:
        result_operations += x.done_operations
    print "Result is", result_operations
    return


# main_func_fifo([2, 4, 6, 8, 10])
# main_func_planner([2, 4, 6, 8, 10])