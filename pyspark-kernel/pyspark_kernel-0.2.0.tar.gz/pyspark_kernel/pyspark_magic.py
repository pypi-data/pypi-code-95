"""Metakernel magic for evaluating cell code using PySaprk."""
from __future__ import absolute_import, division, print_function

import os
from metakernel import ExceptionWrapper
from metakernel import Magic
from metakernel import MetaKernel
from metakernel import option
from metakernel.process_metakernel import TextOutput
from tornado import ioloop, gen
from textwrap import dedent

class PySparkMagic(Magic):
    """Line and cell magic that supports PySpark code execution.
    Attributes
    ----------
    TODO
    """
    def __init__(self, kernel):
        super(PySparkMagic, self).__init__(kernel)
        self.magic_called = False
        self.sc = None

    def _initializeOptions(self):
        # AppName
        if self.options['app_name']:
            self.ss = self.ss.appName(self.options['app_name'])

        if self.options['master']:
            self.ss = self.ss.master(self.options['master'])

        # Adding configs as needed.
        if "config" in self.options:
            for config in self.options['config']:
                self.ss = self.ss.config(config, self.options['config'][config])
        
        # Adding warehouse option for Hive
        if self.options['warehouse']:
            if 'hive_warehosue' not in self.options:
                from os.path import abspath
                warehouse_location = abspath("spark-warehouse")
            else:
                warehouse_location = self.options['hive_warehouse']
            self.ss = self.ss.config("spark.sql.warehouse.dir", warehouse_location)
        
        # Enabling Hive option
        if self.options['hive']:
            self.ss = self.ss.enableHiveSupport()

        
    def _initiliaze_pyspark(self, initialize=False):
        """Initializing pyspark. This includes the SparkContext
        """
        if 'ss' not in dir(self)  or initialize:
            self.kernel.Display(TextOutput("Intitializing PySpark ..."))
            from pyspark.sql import SparkSession
            
            if 'ss' in dir(self):
                self.ss.stop()

            self.ss = SparkSession.builder
            
            # Passing options to session.
            if 'options' in dir(self):
                self._initializeOptions()

            # Initializing the session.
            self.ss = self.ss.getOrCreate()
            self.sc = self.ss.sparkContext

            self.kernel.cell_magics['python'].env['spark'] = self.ss
            self.kernel.cell_magics['python'].env['sc'] = self.sc

            # Display information about the Spark session from PySpark
            self.kernel.Display(TextOutput(dedent("""\
                Spark Web UI available at {webui}
                SparkContext available as 'sc' (version = {version}, master = {master}, app id = {app_id})
                SparkSession available as 'spark'
                """.format(
                    version=self.sc.version,
                    master=self.sc.master,
                    app_id=self.sc.applicationId,
                    webui=self.sc.uiWebUrl
                )
            )))

        return self.sc

    @option(
        "-m", "--master", action="store", type="string", default="",
        help="Master node URL"  
    )
    @option(
         "-a", "--app_name", action="store", type="string", default="",
        help="Sets a name for the application, which will be shown in the Spark Web UI"
    )
    @option(
         "-h", "--hive", action="store_true", default=False,
        help="Boolean telling the libary to activate enable Hive in session."
    )
    @option(
         "-w", "--warehouse", action="store_true", default=False,
        help="If true, it will try to set the 'spark.sql.warehouse.dir' to default location if 'hive_warehouse' is not set."
    )
    @option(
         "-H", "--hive_warehouse", action="store", type="string", default="",
        help="Directory for Hive if you dont want to use default."
    )
    @option(
         "-o", "--options", action="store", type="string", default="",
        help="Options to pass to session"
    )
    def line_pyspark_initialize_kernel(self, master="", app_name="", options="", hive=False, warehouse=False, hive_warehouse=""):
        self.options = {}
        if master != "":
            self.options["master"] = master
        
        if app_name != "":
            self.options["app_name"] = app_name

        if options != "":
            self.options["options"] = options
        
        if hive != "":
            self.options["hive"] = hive

        if hive_warehouse != "":
            self.options["hive_warehouse"] = hive_warehouse

        if warehouse != "":
            self.options["warehouse"] = warehouse

        self._initiliaze_pyspark(initialize=True)

    def line_pyspark(self, *args):
        """%pysprak - Prints out the args passed after magic command
        Parameters
        ----------
        *args : list of string
            Line magic arguments joined into a single-space separated string
        Examples
        --------
        %pysaprk test string
        """
        self.kernel.Print(args)

    # Use optparse to parse the whitespace delimited cell magic options
    # just as we would parse a command line.
    @option(
        "-e", "--eval_output", action="store_true", default=False,
        help="Evaluate the return value from the Scala code as Python code"  
    )
    @option(
         "-b", "--blah", action="store", type="string", default="",
        help="Testing blah"
    )
    def cell_pyspark(self, eval_output=False, blah=""):
        """%%pyspark - Evaluate contents of cell.
        This cell magic will take content of a cell and perform some
        manipulation to it.
        Examples
        --------
        %%pyspark
        testing
        """
        self.magic_called = True
        self.kernel.Print(self.code)
        self.kernel.Print(eval_output)
        self.kernel.Print(blah)
        
    def line_pyspark_interactive_datatable(self, dataframe):
        python_magic = self.kernel.line_magics['python']
        df = python_magic.eval(dataframe+".toPandas()")
        
        import ipydatatable
        table = ipydatatable.InteractiveTable()
        table.table = df
        self.kernel.Display(table)
          
    def line_pyspark_add_to_cell(self, text):
        self.kernel.payload.append({"source": "set_next_input",
                                        "text": text,
                                        "replace": True}) 

    def post_process(self, retval):
        """Processes the output of one or stacked magics.
        Parameters
        ----------
        TODO
        Returns
        -------
        TODO
        """
        self.magic_called = False
        self.kernel.Print("Magic Completed")
