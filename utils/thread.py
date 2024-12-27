from threading import Thread
from typing import Callable


class ExceptionalThread(Thread):
    """Custom implementation of Thread that handles exceptions and raises to main thread
    """
    def __init__(self, target: Callable, args: tuple = (), kwargs: dict = {}):
        """A simple initialiser for a thread with a target functiom, args and kwargs to execute target

        Args:
            target (_type_): is the callable object to be invoked by the run()
        method.
            args (tuple, optional): is a list or tuple of arguments for the target invocation. Defaults to ().
            kwargs (dict, optional): _descriptis a dictionary of keyword arguments for the target
        invocationion_. Defaults to {}.
        """
        super().__init__()
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self._exception = None
    
    def run(self):
        """Function that invokes the target callable when thread.start() in invoked. Handles the exception and stores it as object variable.
        """
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        except Exception as e:
            self._exception = e
        
    def join(self, timeout=None):
        """Function that joins the thread with main thread once execution is complete. Overridden to raise exception handled by run() method.

        Args:
            timeout (_type_, optional): Optional timeout to join thread. Defaults to None.

        Raises:
            self._exception: Exception handled during the execution of target callable.
        """
        super().join(timeout)
        if self._exception:
            raise self._exception
