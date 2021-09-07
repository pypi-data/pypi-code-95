eventMap = {}
class event:
    @staticmethod
    def register(name,fun):
        if name not in eventMap:
            eventMap[name] = []
        eventMap[name].append(fun)
    @staticmethod
    def dispatch(event,params):
        if event in eventMap.keys():
            for i in eventMap[event]:
                i(params)