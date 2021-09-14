import os
import sys
import subprocess
import logging

HADOOP_BIN = "hadoop"
JJA_CLUSTER = "jjalhcluster"
DP_CLUSTER = "dplhcluster"
QW_CLUSTER = "qwlhcluster"
EU_CLUSTER = "bigo-eu"


def hdfs_distcp(src, dest):
    logging.info("distcp from : {} to {}".format(src, dest))
    return subprocess.Popen(
        (HADOOP_BIN, "distcp", "-p=bcaxt", "-bandwidth=1000",
         src, dest),
        stdout=sys.stdout,
        stderr=sys.stdout,
    )

def sync_to_eu_local_hdfs(src, src_name):
    logging.info("sync sources src is {}".format(src))
    # hadoop distcp存在失败可能，允许重试一次（distcp太耗时所以只有一次重试）
    chance = {
        EU_CLUSTER: 2,
    }
    done = {
        EU_CLUSTER: False,
    }
    while not all(done.values()) and any(chance.values()):
        round_ = 1
        p_map = {}
        for dest in filter(lambda x: not done[x], done):
            if chance[dest]:
                proc = hdfs_distcp(src, src.replace(src_name, dest))
                p_map.update({dest: proc})
        for dest in p_map:
            if p_map[dest].wait() == 0:
                done[dest] = True
                chance[dest] = 0
            else:
                chance[dest] -= 1
        logging.info("[chance_map round_{}]{}".format(round_, chance))
        logging.info("[done_map round_{}]{}".format(round_, done))
        round_ += 1

    return all(done.values())

def sync_to_hk_local_hdfs(src, src_name):
    logging.info("sync sources src is {}".format(src))
    # hadoop distcp存在失败可能，允许重试一次（distcp太耗时所以只有一次重试）
    chance = {
        JJA_CLUSTER: 2,
        DP_CLUSTER: 2,
        QW_CLUSTER: 2,
    }
    done = {
        JJA_CLUSTER: False,
        DP_CLUSTER: False,
        QW_CLUSTER: False,
    }
    while not all(done.values()) and any(chance.values()):
        round_ = 1
        p_map = {}
        for dest in filter(lambda x: not done[x], done):
            if chance[dest]:
                proc = hdfs_distcp(src, src.replace(src_name, dest))
                p_map.update({dest: proc})
        for dest in p_map:
            if p_map[dest].wait() == 0:
                done[dest] = True
                chance[dest] = 0
            else:
                chance[dest] -= 1
        logging.info("[chance_map round_{}]{}".format(round_, chance))
        logging.info("[done_map round_{}]{}".format(round_, done))
        round_ += 1

    return all(done.values())
