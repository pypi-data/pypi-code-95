from jinjafy import jinjafy_comment
import numpy as np

#"<jinja1>"
#\begin{tabular}{ {{cc}} }
# {% if bookstabs %}\toprule{% endif %}
# {% if vvlabels %}
#   {% for vl in vvlabels %}
#       {% if loop.index > 1 %} & {% endif %}  \multicolumn{ {{vl[0]}} }{ {{vl[2]}} }{ {{vl[1]}} }
#   {% endfor %} \\
#   {% for vl in vvlabels %}
#       {% if vl[3] %}
# 	     \cmidrule(r){ {{vl[3]}} }
#       {% endif %}
#   {% endfor %}
# {% endif %}
# {% for row in X %}
# {% if bookstabs and loop.index == 2%}\midrule{% endif %}
# {% for c in row %}
# {% if loop.index > 1 %} & {% endif %} {{ c['tex'] }} {% if loop.index == W %} \\ {% endif %}
# {% endfor %}
# {% endfor %}
# {% if bookstabs %}\bottomrule{% endif %}
#\end{tabular}
#</jinja1>
# Convert a matrix to a table super quickly
def mat2table(X,vlabels=None,hlabels=None,file_out = None, bookstabs=True, vvlabels=None,plot=False,pdf_out=None, standalone=False):
    X, Xx, Xerr,Xdl = fmat_X2dict(X)
    if pdf_out: plot = True
    #%%
    if plot:
        import matplotlib.pyplot as plt
        #plt.style.use('ggplot')
        plt.style.use('seaborn')
        fig = plt.figure()
        ax = fig.gca()
        #ax = plt.gca()
        ls = []
        for j in range(X.shape[0]):
            ls.append(ax.plot(Xx[j, :]).pop() )

            if Xerr[j]:
                plt.errorbar(range(X.shape[1]), Xx[j,:], yerr=Xerr[j], color=ls[j].get_color())

            for i in range( X.shape[1] ):
                if 'xs' in X[j,i]:
                    plt.plot([i]*len(X[j,i]['xs']), X[j,i]['xs'], '.', color=ls[j].get_color())

        if vlabels:
            plt.legend(ls, vlabels, bbox_to_anchor=(1.04, 1), loc="upper left")
        if hlabels:
            plt.xticks(range(X.shape[1]), hlabels[1:])
        #plt.subplots_adjust(right=0.5)
        plt.tight_layout(rect=[0, 0, 1, 1])
        plt.show()
        #if pdf_out:
        #    fig.savefig(pdf_out, bbox_inches='tight')


    if vlabels:
        vltex =  [{'tex': v} for v in vlabels]
        for i in range(len(Xdl)):
            Xdl[i] = [vltex[i]] + Xdl[i]

    if hlabels:
        Xdl = [ [{'tex': h} for h in hlabels] ] + Xdl

    if vvlabels:
        cc = 1
        for i in range(len(vvlabels)):
            if len(vvlabels[i]) < 3:
                vvlabels[i].append("c")
            dl = vvlabels[i][0]
            if dl == 1:
                a = None
            else:
                a = "%i-%i"%(cc, cc+dl-1)
            cc = cc + dl
            vvlabels[i] = vvlabels[i] + [a]

    H = len(Xdl)
    W = len(Xdl[0])
    cc = ["c" for i in range(W)]
    if vlabels:
        cc[0] = "l"
    cc = "".join(cc)

    def fmat(x):
        if isinstance(x, int):
            x = str(x)
        if isinstance(x, float):
            x = "%2.3f"%x
        return x

    #X = [ [fmat(x) for x in row] for row in X]

    data = {'X' : Xdl, 'hlabels': hlabels, 'vlabels': vlabels, 'cc': cc, 'H':H, 'W': W, 'bookstabs': bookstabs,
            'vvlabels': vvlabels}

    from jinjafy.jinjafy import jinjafy_comment
    s = jinjafy_comment(data,jinja_tag="jinja1")
    if file_out:
        print("Writing to: " + file_out)

        if standalone:
            s = jinjafy_comment({"s": s}, jinja_tag="jinja3")

        with open(file_out, 'w') as f:
            f.write(s)
        if standalone:

            from slider import latexmk
            latexmk(file_out)


    return s
# "<jinja3>"
# \documentclass[crop]{standalone}
# \usepackage{booktabs}
# \usepackage{siunitx}
# \begin{document}
# {{s}}
# \end{document}
# </jinja3>

def fmat_X2dict(X):
    X = np.asarray(X, dtype=np.object)
    if len(X.shape) > 2:
        X2 = np.ndarray(X.shape[:2], dtype=np.object)
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                X2[i, j] = X[i, j, :].squeeze()
        X = X2
    X = np.reshape(X, X.shape[:2])

    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            dx = X[i,j]
            if isinstance(dx, (list, np.ndarray)):
                dx = [x for x in np.ravel(dx)]

            if not isinstance(dx, dict):
                dx = {'x': dx}
            elif not isinstance(dx['x'], str):
                x = dx['x']
                # if isinstance(x, np.ndarray):
                if 'tex' not in dx:
                    dx['std'] = np.std(x)
                    dx['std_mean'] = np.std(x) / np.sqrt( len(x))
                    dx['xs'] = x
                    dx['x'] = np.mean(x)
                    x2, u2 = mround( dx['x'], dx['std_mean'] )

                    dx['tex'] = '\\SI{%g\\pm %.2f}{}'%(x2, u2)

            if 'tex' not in dx:
                dx['tex'] = dx['x']

            X[i,j] = dx

    Xerr = [None] * X.shape[0]
    Xx = np.zeros(X.shape)

    for i in range(X.shape[0]):
        if "std" in X[0,0]:
            Xerr[i] = [dx['std_mean'] for dx in X[i]]

        for j in range(X.shape[1]):
            Xx[i,j] = X[i,j]['x']

    Xdl = []
    for i in range(X.shape[0]):
        dx = []
        for j in range(X.shape[1]):
            dx.append(X[i,j])
        Xdl.append(dx)


    return X,Xx,Xerr,Xdl

import math
def mround(x,u):
    n = np.floor(np.log10(x)+1)
    dx = np.round(x / np.power(10.0, n), 2)
    du = np.round(u / np.power(10.0, n), 2)
    return dx * np.power(10, n), du * np.power(10.0,n)

