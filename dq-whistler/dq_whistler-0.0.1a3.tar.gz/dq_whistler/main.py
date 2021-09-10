from dq_whistler.analyzer import DataQualityAnalyzer
from pyspark.sql.session import SparkSession

config = [
   {
      "name": "Age",
      "datatype": "number",
      "constraints": [
         {
            "name": "gt_eq",
            "values": 5
         },
         {
            "name": "is_in",
            "values": [1, 23]
         }

      ]
   },
   {
      "name": "Description",
      "datatype": "string",
      "constraints": [
         {
            "name": "regex",
            "values": "([A-Za-z]+)"
         },
         {
            "name": "contains",
            "values": "abc"
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
df = spark.read.option("header", "true").csv("/Users/nareshkumar-mbp/Desktop/sample_data.csv")
output = DataQualityAnalyzer(df, config).analyze()
print(output)
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
