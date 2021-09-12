from cnvrg.helpers.logger_helper import log_error
from itertools import groupby
loaded = False


def __load_matplotlib():
    global loaded
    if loaded: return
    try:
        import matplotlib.pyplot as plt
        loaded = True
    except Exception as e:
        log_error(e)



def show_chart(chart, with_legend=True, legend_loc=4):
    __load_matplotlib()
    import matplotlib.pyplot as plt
    fig = plt.figure()
    plt.title(chart.get("key"))
    plt.xlabel(chart.get("x_axis"))
    plt.ylabel(chart.get("y_axis"))
    legends = []
    for key, values in groupby(chart.get("values"), lambda x: x.get("group")):
        legends.append(key or "Default")
        list_values = [x.get("value") for x in values]
        plt.plot(range(0, len(list_values)), list_values)
    if with_legend: plt.legend(legends, loc=legend_loc)


