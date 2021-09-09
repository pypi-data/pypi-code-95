from yamlns import namespace as ns

def erptree(
        id, model,
        expand=None, # dict attribute -> model
        pickName=None, # fk atributes to pick the name
        pickId=None, # fk attributes to pick the id
        anonymize=None, # attributes to anonymize
        remove=None, # attributes to remove
        head=3, tail=3, # chars to leave when anonymizing
):
    """
    Retrieves an object from the erp and some children
    and does some common postprocessing to have
    a namespace that can be dumped as yaml.
    Children attributes are referenced by dot notation.
    - 'model' is the erppeek or ooop model factory.
    - 'expand' should be a dict of relation attributes
    to its erp model so that the tree can be expanded.
    - 'pickId' a list or space separated strings,
    for fk attributes you want to pick the id
    and remove the name.
    - 'pickName' is the counterpart, takes the name.
    - 'anonymize' will take any string attribute
    and will ellipse it but 'tail' chars from the end
    and 'head' chars from the beggining.
    - 'remove' will remove the attribute.
    """

    def processAttributes(attributes):
        for attribute in listify(attributes):
            for context, leaf in  getContext(target, attribute):
                yield context, leaf, attribute

    target = ns(model.read(id))

    for context, leaf, fullname in processAttributes(expand):
        with step("Expanding", fullname):
            submodel = expand[fullname]
            oldvalue = context[leaf]
            if len(oldvalue)==2 and type(oldvalue[1]) == str:
                context[leaf] = ns(submodel.read(context[leaf][0]))
            else:
                context[leaf] = [ ns(x) for x in submodel.read(oldvalue)]

    for context, leaf, fullname in processAttributes(pickName):
        with step("FK as name", fullname):
            context[leaf] = context[leaf][1]

    for context, leaf, fullname in processAttributes(pickId):
        with step("FK as id", fullname):
            context[leaf] = context[leaf][0]

    for context, leaf, fullname in processAttributes(anonymize):
        with step("Anonymizing", fullname):
            val = str(context[leaf])
            context[leaf] = val[:head] + "..." + val[-tail:]

    for context, leaf, fullname in processAttributes(remove):
        with step("Removing", fullname):
            if type(context) == list:
                for x in context:
                    del x[leaf]
            else:
                del context[leaf]

    return target

from contextlib import contextmanager

@contextmanager
def step(doing, attribute):
    print(doing, attribute)
    try:
        yield
    except Exception as e:
        print("Error while", doing, attribute)
        raise

def listify(attributes):
    if not attributes: return []
    if type(attributes) == str:
        return sorted(attributes.split())
    return sorted(attributes)

def getContext(o, attribute):
    steps = attribute.split('.')
    if len(steps) == 1:
        yield o, attribute
        return
        for item in o:
            yield item, attribute
        return
    if type(o) == list:
        for item in o:
            yield from getContext(item, attribute)
        return
    nextSteps = '.'.join(steps[1:])
    yield from getContext(o[steps[0]], nextSteps)



