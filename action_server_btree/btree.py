class NodeStatus:
    def __init__(self) -> None:
        pass

    def success(self) :
        pass

    def failure(self) :
        pass

    def running(self) :
        pass

class ControlFlowNode:
    def __init__(self) -> None:
        pass

    def sequence(self, subtree) :
        "->"
        pass

    def fallback(self, condition):
        ''' ? '''
        pass
        
    def parallel(self):
        pass

    def decorator(self):
        pass

class ExecutionNode:
    def __init__(self) -> None:
        pass

    def action(self):
        pass

    def condition(self):
        pass
