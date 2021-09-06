from pyspark_kernel import PySparkKernel
import findspark

if __name__ == '__main__':
    findspark.init()
    PySparkKernel.run_as_main()