from dq_whistler.analyzer import DataQualityAnalyzer
from pyspark.sql.session import SparkSession

config = [
   {
      "name": "Year",
      "datatype": "string",
      "constraints":[
         {
            "name": "regex",
            "values": "([A-Za-z]+)"
         },
         {
            "name": "contains",
            "values": "abc"
         }
      ]
   },
   {
      "name": "Values",
      "datatype": "number",
      "constraints":[
         {
            "name": "gt_eq",
            "values": 5
         },
         {
            "name": "is_in",
            "values": [1, 2]
         }
      ]
   }
]


spark = (
   SparkSession
      .builder
      .appName("whistler testing")
      .getOrCreate()
   )
df = spark.read.option("header", "true").csv("data/sample_data.csv")
# pip install toko_dq_shisteler
# import DQA from dqhi
# constriant_output (json -> pandas df) = DataQualityAnalyzer(df, config).analyze()
#
# DataQualityAnalyzer(df, config)
# .ismin("col", "5")
# .ismax("col5", 10)
# .regex("")
# ...
# .run()


(seong, Nathan, Gaurav)

print(constriant_output)