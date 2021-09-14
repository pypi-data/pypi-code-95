from xdl.python.framework.session import Hook

def hook_lambda(ops, func):
    class LambdaHook(Hook):
        def before_run(self, v):
            return ops
        
        def after_run(self, v):
            assert len(ops) == len(v)
            func(v)
    return LambdaHook()