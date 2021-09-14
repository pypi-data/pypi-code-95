# -*- coding: UTF-8 -*-
SUMIT_SCRIPT = """
export SPARK_HOME=/data/opt/spark
SPARK_SUBMIT=$SPARK_HOME/bin/spark-submit
export HADOOP_HOME=/usr/hdp/current/hadoop-client
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib/native"
export HADOOP_CONF_DIR=/etc/hadoop/conf
export HADOOP_YARN_DIR=/etc/hadoop/conf
export HADOOP_USER_NAME={user}
$SPARK_SUBMIT --master yarn --name {name} --num-executors={executors} \
              --deploy-mode cluster \
              {files} \
              {pyfiles} \
              {jars} \
              {extra} \
              {main} {name} {scene} {input_path} {output_path}
"""