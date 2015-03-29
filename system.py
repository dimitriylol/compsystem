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
            self.queueLock.acquire()
            print "adding task to queue"
            self.queue.put(Task())
            print "END adding task to queue"
            self.queue_lock.release()
            time.sleep(0.001)   # every milliseconds adding some task
        else:
            self.queue_lock.acquire()
            self.done = True


class Processor (Thread):
    def __init__(self, proc_id, power, manage_queue, control_threads, queue):   # management - name function: FIFO and others algorithms
        Thread.__init__(self)
        self.id = proc_id
        self.power = power  # power - number of operations per ms
        self.manage_queue = manage_queue
        self.control = control_threads
        self.queue = queue

    def run(self):
        while True:
            self.manage_queue(self)


class WorkerProcessor (Processor):
    def __init__(self, proc_id, power, manage_queue, control_threads, queue):
        Processor.__init___(self, proc_id, power, manage_queue, control_threads,queue)
        self.busy = False
        self.start()

    def fifo(self):
        """get first task and try execute by self.id_proc"""
        self.control.acquire()
        if not self.queue.empty():
            task = self.queue.get()
            if self.id_proc in task.lst_suitable_proc:
                print "working ", self.id_proc, " processor"
                self.control.release()
                time.sleep(task.number_operations/(self.power*1000))     # sleep() get in seconds, our task in ms
            else:
                self.queue.put(task)
                self.control.release()
                # time.sleep(0.001)       # necessary ???
        else:
            print "Queue empty"
            self.control.release()
            time.sleep(0.001)   # time for wedged to queue by TaskQueue

    def worker_planner(self):   # control is pair of conditional and lock for queue
        """worker_planner just executing task when condition is send"""
        self.control[0].acquire()
        self.control[0].wait()
        self.control[1].acquire()
        print "working ", self.id_proc, " processor"
        self.busy = True
        task = self.queue.get()
        self.control[1].release()
        time.sleep(task.number_operations/(self.power*1000))     # sleep() get in seconds, our task in ms
        self.control[0].release()


class PlanningProcessor (Processor):
    def __init__(self, proc_id, manage_queue, lst_lock, lst_processors, queue):
        Processor.__init__(self, proc_id, 0, manage_queue, lst_lock, queue)
        self.busy = True
        self.lst_processors = lst_processors
        self.start()

    def planner_helper(self, lst_task):   # return True if sends task to processors and False if doesn't
        task_send = False
        for id_suitable_proc in lst_task[0].lst_suitable_proc:
            if not self.lst_processors[id_suitable_proc].busy:
                map(lambda item: self.queue.put(item), self.lst_processors)
                task_send = True
                self.control[id_suitable_proc].acquire()
                self.control[id_suitable_proc].notify()
                self.control[id_suitable_proc].release()
        if not self.workQueue.empty():
            if task_send:
                return True
            else:
                self.planner_helper(lst_task.insert(0, self.queue.get()))
        else:       # if sort out all queue and won't be free suitable processors. HIGHLY UNLIKELY
            map(lambda item: self.queue.put(item), self.lst_processors)
            return False

    def planner(self):      # control is list of conditions and lock for queue
        """planner finds suitable free processors and send condition to work"""
        self.control[len(self.control)-1].acquire()     # acquire queue
        if not self.queue.empty():
            self.planner_helper([self.queue.get()])
            print "done of planning task"
            self.control[len(self.control)-1].release()     # release queue
        else:
            print "Queue empty"
            self.control[len(self.control)-1].release()     # release queue
            time.sleep(0.001)   # time for wedged to queue by TaskQueue


def main_func_planner(lst_power):
    lst_cond = [Condition(Lock()) for x in xrange(5)]      # last lock for queue
    lst_power[lst_power.index(min(lst_power))] = 0
    lst_processors = []
    queue_lock = Lock()
    work_queue = Queue()
    task_queue = TaskQueue(3, queue_lock, work_queue)
    for x in xrange(5):
        if lst_power[x] == 0:
            lst_processors.append(PlanningProcessor(x,
                                                    PlanningProcessor.planner,
                                                    list(set(lst_cond) | set ([queue_lock])),
                                                    lst_processors,     # not sure that in planner will see all threads
                                                    work_queue))
        else:
            lst_processors.append(WorkerProcessor(x,
                                                  lst_power[x],
                                                  WorkerProcessor.worker_planner,
                                                  [lst_cond[x], queue_lock],
                                                  work_queue))
    while not task_queue.done:  # wait for passing 10 seconds
        pass
    print "end of everything!"
    return


def main_func_fifo(lst_power):
    queue_lock = Lock()
    work_queue = Queue()
    lst_processors = []
    task_queue = TaskQueue(3, queue_lock, work_queue)      # will append task to queue for 3 seconds, another my random
    for x in xrange(5):
        lst_processors.append(WorkerProcessor(x,
                                              lst_power[x],
                                              WorkerProcessor.fifo,
                                              queue_lock,
                                              work_queue))
    while not task_queue.done:  # wait for passing 10 seconds
        pass
    print "end of everything!"
    return

# main_func_fifo([2, 4, 6, 8, 10])
# main_func_planner([2, 4, 6, 8, 10])