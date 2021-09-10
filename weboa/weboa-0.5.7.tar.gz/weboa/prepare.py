import pkg_resources

class Package:
    stream = pkg_resources.resource_filename(__name__,"../weboa_res/")
    #stream = pkg_resources.resource_filename(__name__, "weboa_res/")