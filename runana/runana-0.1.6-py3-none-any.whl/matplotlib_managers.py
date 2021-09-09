from __future__ import print_function

from contextlib import contextmanager
from os import getcwd, rename
from os.path import splitext, abspath, split
from os.path import join as pjoin

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure

from runana.run import makedir


class IndivFiles(object):
    """ Keeps track of png or svg files in a directory
    """
    def __init__(self, outfile, *args, **kwargs):
        basedir, file_ext = splitext(outfile)
        basedir = abspath(pjoin(getcwd(), basedir))
        makedir(basedir)
        self.cwd = getcwd()
        self.outfile = outfile
        self.basedir = basedir
        self.file_ext = file_ext
        self.args = args
        self.kwargs = kwargs
        self.page = 1
        if self.file_ext == ".png":
            self.canvas_func = FigureCanvas
        elif self.file_ext == ".svg":
            self.canvas_func = FigureCanvasSVG
        else:
            raise ValueError("File extension {} is not known".format(self.file_ext))

    def savefig(self, figure, **kwargs):
        try:
            fname = pjoin(self.basedir, "{}{}".format(self.page,
                                                      self.file_ext))
            if self.page == 1:
                fname = pjoin(self.cwd, self.outfile)
            elif self.page == 2:
                rename(pjoin(self.cwd, self.outfile),
                       pjoin(self.basedir, "{}{}".format(1,
                                                          self.file_ext)))
            orig_canvas = figure.canvas
            figure.canvas = self.canvas_func(figure)
            figure.savefig(fname, format=self.file_ext[1:], **kwargs)
            self.page += 1
        finally:
            figure.canvas = orig_canvas

    def get_pagecount(self):
        return self.page

    def close(self):
        """ No clean up needed """
        pass


class webmMovie(IndivFiles):

    def __init__(self, outfile, *args, **kwargs):
        self.outfile_video = outfile
        self.bitrate = kwargs.pop("bitrate", "1M")
        self.reverse = kwargs.pop("reverse", False)
        __, file_ext = splitext(self.outfile_video)
        self.file_ext_video = file_ext
        for file_ext in [".webm", ".mp4"]:
            outfile = outfile.replace(file_ext, ".png")
        super(webmMovie, self).__init__(outfile, *args, **kwargs)

    def print_args(self, args, fname, mode="w"):
        with open(pjoin(self.basedir, fname), mode) as file_:
            file_.write(" ".join(args+["\n"]))

    def close(self):
        from subprocess import call
        outfile_video = self.outfile_video
        if self.file_ext_video == ".webm":
            options = ["-y", "-c:v", "libvpx-vp9", "-b:v", self.bitrate]
        elif self.file_ext_video == ".mp4":
            options = ["-y", "-c:v", "libx264", "-b:v", self.bitrate]
            options += ["-pix_fmt", "yuv420p"]
        else:
            raise ValueError("Unsupported file_ext: " + self.file_ext_video)
        args = ["ffmpeg"]
        args.extend(["-i", pjoin(self.basedir, "%d.png")])
        # lines = []
        # filenames = []
        nfiles = self.page-1
        for i in range(nfiles):
            filename = pjoin(self.basedir, "{}.png".format(i+1))
            if self.reverse:
                filename2 = pjoin(self.basedir, "{}.png".format(2*nfiles-i))
                from os import remove
                from shutil import copy
                from runana.run import ignored
                with ignored(OSError):
                    remove(filename2)
                copy(filename, filename2)
        # filenames = []
        # for i in range(self.page-1):
        #     filename = pjoin(self.basedir, "{}.png".format(i+1))
        #     filenames.append(filename)
        #     lines.append("file '{}'\n".format(filename))
        # if self.reverse:
        #     filenames += reversed(filenames)
        # input_files = pjoin(self.basedir, "input_files.txt")
        # with open(input_files, "w") as file_:
        #     file_.write("".join(lines))
        #     if self.reverse:
        #         file_.write("".join(reversed(lines)))
        # args.extend(["-f", "concat",  "-i", input_files])
        # nested_list = [["-i", filename] for filename in filenames]
        # args.extend([arg for filename in filenames
        #              for arg in ["-i", filename]])
        # args.extend([item for sub in nested_list for item in sub])
        args.extend(options)
        args.append(outfile_video)
        self.print_args(args, "ffmpeg_args.txt")
        call(args)
        # with open(pjoin(self.basedir, "ffmpeg_args.txt"), "w") as file_:
        #     file_.write(" ".join(args+["\n"]))
        # if self.reverse:
        #     reverse_fname = "reverse.webm"
        #     args = ["ffmpeg", "-i", outfile_video,
        #             "-vf", "reverse"]
        #     args.extend(options)
        #     args.append(reverse_fname)
        #     call(args)
        #     self.print_args(args, "ffmpeg_args.txt", mode="aw")
        #     video_list = pjoin(self.basedir, "video_list.txt")
        #     self.print_args(["file", outfile_video], video_list, mode="w")
        #     self.print_args(["file", reverse_fname], video_list, mode="aw")
        #     args = ["ffmpeg", "-f", "concat",
        #             "-i", video_list,
        #             reverse_fname]
        #     # args.extend(options)
        #     args.extend(options)
        #     args.append("reverse_combined.webm")
        #     call(args)
        #     self.print_args(args, "ffmpeg_args.txt", mode="aw")


class plot_manager(object):
    """ Creates pdf file using :func:`matplotlib.backends.backend_pdf.PdfPages`
 and returns the handle to this pdf.

    `*args` and `*kwargs` are passed to `PdfPages`
    """
    def __init__(self, outfile, print_outfile=True, *args, **kwargs):
        self.outfile = outfile
        self.print_outfile = print_outfile
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        _, file_ext = splitext(self.outfile)
        if file_ext == ".pdf":
            self.pp = PdfPages(self.outfile, *self.args, **self.kwargs)
        elif file_ext == ".svg" or file_ext == ".png":
            self.pp = IndivFiles(self.outfile, *self.args, **self.kwargs)
        elif file_ext == ".webm" or file_ext == ".mp4":
            self.pp = webmMovie(self.outfile, *self.args, **self.kwargs)
        else:
            raise ValueError("Unknown file extension {}".format(file_ext))
        return self.pp

    def __exit__(self, type, value, traceback):
        self.pp.close()
        if self.print_outfile:
            print(self.outfile)


class single_fig_manager(object):
    """ Create a :class:`matplotlib.figure.Figure`

    `args` and `kwargs` are passed to the :class:`Figure` constructor

    :param matplotlib.backends.backend_pdf.PdfPages pp: handle that has a
        savefig method
    """
    def __init__(self, pp, *args, **kwargs):
        self.pp = pp
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        self.fig = Figure(*self.args, **self.kwargs)
        FigureCanvas(self.fig)
        return self.fig

    def __exit__(self, type, value, traceback):
        self.pp.savefig(self.fig, transparent=True)
        # self.pp.savefig(self.fig, transparent=True, bbox_inches="tight")
        self.fig.clear


class single_ax_manager(single_fig_manager):
    """ Create an axis with a single subplot in a `Figure` object.

    Subclassed from :class:`single_fig_manager`, and all the arguments are the
    same
    """
    def __enter__(self):
        self.fig = super(single_ax_manager, self).__enter__()
        ax = self.fig.add_subplot(1, 1, 1)
        return ax


@contextmanager
def plot_ax_manager(outfile, *args, **kwargs):
    """ Create a pdf with name `outfile` containing one plot"""
    with plot_manager(outfile, *args, **kwargs) as pp:
        with single_ax_manager(pp) as ax:
            yield ax
