
from ScheduleResultsAI import *
from ConditionsAI import *

class Schedule:
    """
    A schedule is just a list of tasks for the AI to run.
    A task is the smallest atomic action that an AI character can perform.
    
    The interrupt mask is a bitmask of conditions that will cause the schedule
    to abort.
    
    The schedule/task system can be used to make a wide variety of AI actions.
    """
    
    def __init__(self, tasks = [], interruptMask = COND_TASK_FAILED | COND_NEW_TARGET | COND_SCHEDULE_DONE, failSched = None):
        self.tasks = tasks
        self.interruptMask = interruptMask
        self.currentTask = 0
        self.failSchedule = failSched
        
        self.__newTask = True

    def cleanup(self):
        for task in self.tasks:
            task.cleanup()
        del self.tasks
        del self.interruptMask
        del self.currentTask
        del self.failSchedule
        del self.__newTask

    def reset(self):
        self.currentTask = 0
        self.__newTask = True

    def getFailSchedule(self):
        return self.failSchedule

    def hasFailSchedule(self):
        return self.failSchedule is not None
        
    def getCurrentTask(self):
        return self.currentTask
        
    def getTaskList(self):
        return self.tasks
        
    def getInterruptMask(self):
        return self.interruptMask
        
    def hasInterrupts(self, interrups):
        return (self.interruptMask & interrupts) != 0
        
    def runSchedule(self):
        """
        Runs a task in the schedule.
        
        Returns True when the schedule has completed,
        False if more tasks needs to run.
        """
        
        if self.currentTask >= len(self.tasks):
            # The schedule has run through completely.
            return SCHED_COMPLETE
        
        task = self.tasks[self.currentTask]
            
        if self.__newTask:
            task.startTask()
            self.__newTask = False
            
        run = task.runTask()
        if run == SCHED_COMPLETE:
            # Task has completed
            task.stopTask()
            
            self.currentTask += 1
            self.__newTask = True
        elif run == SCHED_FAILED:
            # Task failed
            return SCHED_FAILED

        return SCHED_CONTINUE
