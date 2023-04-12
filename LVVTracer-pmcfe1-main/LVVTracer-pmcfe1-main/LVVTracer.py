import sys
from types import TracebackType, FrameType
from typing import Type, Optional, Dict, Any, Callable


def is_internal_error(exc_tp, exc_value, exc_traceback):
    return exc_tp or exc_value or exc_traceback


class LVVTracer():
    def __init__(self, target_func):
        self.target_func = target_func
        self.func_copy_name = self.target_func
        self.lvv_map = {}

    def __enter__(self) -> Any:
        self.lvv_map.clear()
        self.target_func = sys.gettrace()
        sys.settrace(self.counter_vars)
        return self

    def counter_vars(self, frame: FrameType, event: str, arg: Any):
        if event == 'line':
            co = frame.f_code
            if co.co_name == self.func_copy_name:
                var_names = co.co_varnames[:co.co_argcount + co.co_nlocals]
                for i, var_name in enumerate(var_names):
                    if var_name not in self.lvv_map:
                        self.lvv_map[var_name] = 0
                    else:
                        if var_name == co.co_varnames.__getitem__(i):
                            self.lvv_map[var_name] += 1
                print(self.lvv_map)
        return self.counter_vars

    def __exit__(self, exc_tp: Type, exc_value: BaseException,
                 exc_traceback: TracebackType) -> Optional[bool]:
        # Note: we must return a non-True value here,
        # such that we re-raise all exceptions
        if is_internal_error(exc_tp, exc_value, exc_traceback):
            return False  # internal error
        else:
            sys.settrace(None)
            return None  # all ok

    def getLVVmap(self) -> dict:
        return self.lvv_map
