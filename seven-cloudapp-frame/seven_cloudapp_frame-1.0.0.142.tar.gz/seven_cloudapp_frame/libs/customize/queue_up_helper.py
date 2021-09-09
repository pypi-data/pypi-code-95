# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-30 09:22:51
@LastEditTime: 2021-09-06 15:24:46
@LastEditors: HuangJianYi
@Description: 排队系统帮助类
"""
from seven_framework import *
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.libs.customize.seven_helper import *


class QueueUpHelper:
    """
    :description: 排队系统帮助类 提供加入排队、退出排队、查询单个排队情况、批量查询排队情况、更新可操作时间、签到等功能
    """
    logger_error = Logger.get_logger_by_name("log_error")

    @classmethod
    def _get_zset_name(self,app_id,queue_name):
        """
        :description: 获取排行集合名称，集合用于排行榜，排第一的优先操作
        :param app_id：应用标识
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        zset_name = "queueup_zset"
        if app_id:
            zset_name += "_" + str(app_id)
        if queue_name:
            zset_name += ":" + str(queue_name)
        return zset_name

    @classmethod
    def _get_count_name(self,app_id, queue_name):
        """
        :description: 获取排队号计数名称
        :param app_id：应用标识
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        count_name = "queueup_count"
        if app_id:
            count_name += "_" + str(app_id)
        if queue_name:
            count_name += ":" + str(SevenHelper.get_now_day_int()) + "_" + str(queue_name)
        return count_name

    @classmethod
    def _get_user_hash_name(self, app_id):
        """
        :description: 获取用户关联队列名称
        :param app_id：应用标识
        :return: 
        :last_editors: HuangJianYi
        """
        hash_name = "queueup_user_list"
        if app_id:
            hash_name += "_" + str(app_id)
        return hash_name

    @classmethod
    def _get_user_zset_name(self,app_id):
        """
        :description: 用户在小程序内的排队次数信息
        :param app_id：应用标识
        :return: 
        :last_editors: HuangJianYi
        """
        zset_name = "queueup_zset_user"
        if app_id:
            zset_name += "_" + str(app_id)
        return zset_name

    @classmethod
    def _get_queue_no(self, app_id, queue_name):
        """
        :description: 获取排队号
        :param app_id：应用标识
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        count_name = self._get_count_name(app_id,queue_name)
        redis_init = SevenHelper.redis_init()
        queue_no = redis_init.incr(count_name, 1)
        redis_init.expire(count_name, 24 * 3600)
        return queue_no

    @classmethod
    def _get_queue_num(self, app_id, queue_name):
        """
        :description: 获取当前排队人数
        :param app_id：应用标识
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        zset_name = self._get_zset_name(app_id,queue_name)
        redis_init = SevenHelper.redis_init()
        return redis_init.zcard(zset_name)

    @classmethod
    def _get_all_queue_num(self, app_id):
        """
        :description: 获取小程序总排队人数
        :param app_id：应用标识
        :return: 
        :last_editors: HuangJianYi
        """
        user_zset_name = self._get_user_zset_name(app_id)
        redis_init = SevenHelper.redis_init()
        return redis_init.zcount(user_zset_name,1,5000)

    @classmethod
    def _delete_user(self, app_id, queue_name):
        """
        :description: 删除第一位未确认的排队者
        :param app_id：应用标识
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if SevenHelper.is_continue_request(f"queue_delete_user:{queue_name}", 200) == True:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起,请200毫秒后再试"
            return invoke_result_data
        try:
            redis_init = SevenHelper.redis_init()
            zset_name = self._get_zset_name(app_id, queue_name)
            value_list = redis_init.zrange(zset_name, 0, 0)
            if len(value_list) > 0:
                data = value_list[0]
                hash_name = self._get_user_hash_name(app_id)
                hash_key = f"userid_{data}_queuename_{queue_name}"
                hash_value = redis_init.hget(hash_name, hash_key)
                if hash_value:
                    hash_value = SevenHelper.json_loads(hash_value)
                    if hash_value["progress_status"] == 0:
                        start_timestamp = TimeHelper.get_now_timestamp()
                        end_timestamp = start_timestamp + int(config.get_value("queue_confirm_time", 8))  #排到第一位确认倒计时时间,单位秒
                        hash_value["progress_status"] = 1
                        hash_value["start_timestamp"] = start_timestamp
                        hash_value["end_timestamp"] = end_timestamp
                        hash_value["start_date"] = TimeHelper.timestamp_to_format_time(start_timestamp)
                        hash_value["end_date"] = TimeHelper.timestamp_to_format_time(end_timestamp)
                        redis_init.hset(hash_name, hash_key, SevenHelper.json_dumps(hash_value))
                    else:
                        now_timestamp = TimeHelper.get_now_timestamp()
                        if now_timestamp > hash_value["end_timestamp"]:
                            redis_init.hdel(hash_name, hash_key)
                            redis_init.zrem(zset_name, data)
                            invoke_result_data.error_code = "del"
                else:
                    redis_init.zrem(zset_name, data)
                    invoke_result_data.error_code = "del"
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【删除未操作的排队信息】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "删除未操作的排队信息失败"
            return invoke_result_data

    @classmethod
    def _delete_and_notice_user(self, app_id, queue_name):
        """
        :description: 删除第一位未确认的排队者并通知下一位开始确认
        :param app_id：应用标识
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = self._delete_user(app_id,queue_name)
        if invoke_result_data.error_code == "del":
            self._delete_user(app_id,queue_name)

    @classmethod
    def queue(self, app_id, queue_name, user_id, user_nick="", queue_length=10, all_queue_limit_num=500):
        """
        :description: 加入排队
        :param app_id：应用标识
        :param queue_name：队列名称
        :param user_id 用户标识
        :param user_nick 用户昵称
        :param queue_length：队列的长度
        :param all_queue_limit_num：小程序内总排队人数上限
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            acquire_lock_name = f"queueup_queue"
            if app_id:
                acquire_lock_name += "_" + str(app_id)
            acquire_lock_name += ":" + str(queue_name)

            acquire_lock_status, identifier = SevenHelper.redis_acquire_lock(acquire_lock_name)
            if acquire_lock_status == False:
                invoke_result_data.success = False
                invoke_result_data.error_code = "acquire_lock"
                invoke_result_data.error_message = "系统繁忙,请稍后再试"
                return invoke_result_data
            redis_init = SevenHelper.redis_init()
            if all_queue_limit_num > 0 and self._get_all_queue_num(app_id) >= all_queue_limit_num:
                SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                invoke_result_data.success = False
                invoke_result_data.error_code = "total_limit"
                invoke_result_data.error_message = "排队失败,排队总人数已达上限"
                return invoke_result_data
            zset_name = self._get_zset_name(app_id,queue_name)
            data = str(user_id)
            expire_time = 7 * 24 * 3600
            if not redis_init.zscore(zset_name, data):
                if self._get_queue_num(app_id,queue_name) >= queue_length:
                    SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "queue_limit"
                    invoke_result_data.error_message = "排队失败,当前排队人数已达上限"
                    return invoke_result_data
                queue_no = self._get_queue_no(app_id,queue_name)
                redis_init.zadd(zset_name, {data: queue_no})
                redis_init.expire(zset_name, expire_time)

                user_zset_name = self._get_user_zset_name(app_id)
                redis_init.zincrby(user_zset_name, 1, data)
                redis_init.expire(user_zset_name, expire_time)

                hash_value = {}
                hash_value["queue_name"] = queue_name  #排队名称
                hash_value["queue_no"] = queue_no  #排队号
                hash_value["user_id"] = data  #用户标识
                hash_value["user_nick"] = user_nick  #用户昵称
                hash_value["queue_date"] = SevenHelper.get_now_datetime()  #入队时间

                queue_index = int(redis_init.zrank(zset_name, data)) + 1
                #进度-1未排队0已排队1已确认2办理中
                if queue_index == 1:
                    start_timestamp = TimeHelper.get_now_timestamp()
                    end_timestamp = start_timestamp + int(config.get_value("queue_confirm_time", 8))  #排到第一位确认倒计时时间,单位秒
                    hash_value["progress_status"] = 1
                    hash_value["start_timestamp"] = start_timestamp
                    hash_value["end_timestamp"] = end_timestamp
                    hash_value["start_date"] = TimeHelper.timestamp_to_format_time(start_timestamp)
                    hash_value["end_date"] = TimeHelper.timestamp_to_format_time(end_timestamp)
                else:
                    hash_value["progress_status"] = 0
                #添加排队信息
                hash_name = self._get_user_hash_name(app_id)
                hash_key = f"userid_{data}_queuename_{queue_name}"
                redis_init.hsetnx(hash_name, hash_key, SevenHelper.json_dumps(hash_value))
                redis_init.expire(hash_name, expire_time)

                result_data = {}
                result_data["queue_no"] = hash_value["queue_no"]  #排队号
                result_data["queue_num"] = self._get_queue_num(app_id,queue_name)  #当前排队人数
                result_data["queue_index"] = queue_index  #当前位置
                result_data["before_num"] = queue_index - 1  #排在前面的人数
                invoke_result_data.data = result_data

                SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                return invoke_result_data
            else:
                SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "该用户已在队列中,请勿重复排队"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【加入排队】" + str(ex))
            SevenHelper.redis_release_lock(acquire_lock_name, identifier)
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "排队失败,请稍后再来"
            return invoke_result_data

    @classmethod
    def pop(self, app_id, queue_name, user_id):
        """
        :description: 退出排队
        :param app_id：应用标识
        :param queue_name：队列名称
        :param user_id 用户标识
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            cache_key = f"queueup_pop"
            if app_id:
                cache_key += "_" + str(app_id)
            cache_key += ":" + str(queue_name) + "_" + str(user_id)
            if SevenHelper.is_continue_request(cache_key, expire=1 * 1000) == True:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "对不起,请1秒后再试"
                return invoke_result_data
            zset_name = self._get_zset_name(app_id,queue_name)
            data = str(user_id)
            redis_init = SevenHelper.redis_init()
            if redis_init.zscore(zset_name, data):
                redis_init.zrem(zset_name, data)
                redis_init.zincrby(self._get_user_zset_name(app_id), -1, data)
                redis_init.hdel(self._get_user_hash_name(app_id), f"userid_{data}_queuename_{queue_name}")
                return invoke_result_data
            else:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "未查到该用户的排队情况,请先排队"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【退出排队】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "退出排队失败"
            return invoke_result_data

    @classmethod
    def query(self, app_id, queue_name, user_id):
        """
        :description: 查询某用户排队情况
        :param app_id：应用标识
        :param queue_name：队列名称
        :param user_id：用户标识
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            redis_init = SevenHelper.redis_init()
            zset_name = self._get_zset_name(app_id,queue_name)
            data = str(user_id)
            #踢掉过期用户并通知下一个用户
            self._delete_and_notice_user(app_id,queue_name)
            #删除用户排队次数小于等于0的数据
            redis_init.zremrangebyscore(self._get_user_zset_name(app_id),-10,0)

            #判断是否存在排队信息
            score = redis_init.zscore(zset_name, data)
            if score:
                query_user = {}
                query_user["queue_name"] = queue_name  #队列名称
                query_user["queue_no"] = int(score)  #排队号
                query_user["total_num"] = self._get_queue_num(app_id,queue_name)  #总排队人数
                query_user["queue_index"] = int(redis_init.zrank(zset_name, data)) + 1  #当前位置
                query_user["before_num"] = query_user["queue_index"] - 1  #排在前面的人数
                hash_value = redis_init.hget(self._get_user_hash_name(app_id), f"userid_{data}_queuename_{queue_name}")
                hash_value = SevenHelper.json_loads(hash_value) if hash_value else {}
                query_user["start_date"] = hash_value["start_date"] if hash_value.__contains__("start_date") else ''
                query_user["end_date"] = hash_value["end_date"] if hash_value.__contains__("end_date") else ''
                query_user["queue_date"] = hash_value["queue_date"] if hash_value.__contains__("queue_date") else ''
                query_user["progress_status"] = 0  #进度-1未排队0已排队1已确认2办理中
                invoke_result_data.data = query_user
                return invoke_result_data
            else:
                query_user = {}
                query_user["queue_name"] = queue_name  #队列名称
                query_user["progress_status"] = -1  #进度-1未排队0已排队1已确认2办理中
                query_user["before_num"] = self._get_queue_num(app_id,queue_name)  #排在前面的人数
                invoke_result_data.data = query_user
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "未查到排队情况,请先排队"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【查询某用户排队情况】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "未查到排队情况,请先排队"
            return invoke_result_data

    @classmethod
    def muti_user_query(self, app_id, user_id):
        """
        :description: 批量查询某用户排队情况 只包含已排队的信息
        :param app_id：应用标识
        :param user_id：用户标识
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = []
        try:
            redis_init = SevenHelper.redis_init()
            hash_name = self._get_user_hash_name(app_id)
            data = str(user_id)
            match_result = redis_init.hscan_iter(hash_name, match=f'userid_{data}_*')
            for item in match_result:
                hash_value = SevenHelper.json_loads(item[1])
                query_invoke_result_data = self.query(app_id,hash_value["queue_name"], user_id)
                if query_invoke_result_data.success == True:
                    invoke_result_data.data.append(query_invoke_result_data.data)
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【批量查询某用户排队情况】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "未查到排队情况,请先排队"
            return invoke_result_data

    @classmethod
    def muti_queue_query(self, app_id, queue_name_list, user_id):
        """
        :description: 批量查询排队情况 包含已排队和未排队的信息
        :param app_id：应用标识
        :param queue_name_list：查询队列集合
        :param user_id：用户标识
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = []
        try:
            for queue_name in queue_name_list:
                query_invoke_result_data = self.query(app_id,queue_name, user_id)
                invoke_result_data.data.append(query_invoke_result_data.data)
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【批量查询排队情况】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "未查到排队情况"
            return invoke_result_data

    @classmethod
    def update_time(self, app_id, queue_name, user_id, operate_time=0):
        """
        :description: 更新可操作时间，用于操作倒计时，时间到则踢出队列
        :param app_id：应用标识
        :param queue_name：队列名称
        :param user_id：用户标识
        :param operate_time：增加的操作时间，单位秒
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            redis_init = SevenHelper.redis_init()
            zset_name = self._get_zset_name(app_id,queue_name)
            data = str(user_id)
            score = redis_init.zscore(zset_name, data)
            if score and operate_time > 0:
                hash_name = self._get_user_hash_name(app_id)
                hash_key = f"userid_{data}_queuename_{queue_name}"
                hash_value = redis_init.hget(hash_name, hash_key)
                if not hash_value:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "更新可操作时间失败"
                    return invoke_result_data
                hash_value = SevenHelper.json_loads(hash_value)
                end_timestamp = TimeHelper.get_now_timestamp() + int(operate_time)
                hash_value["end_timestamp"] = end_timestamp
                hash_value["end_date"] = TimeHelper.timestamp_to_format_time(end_timestamp)
                redis_init.hset(hash_name, hash_key, SevenHelper.json_dumps(hash_value))
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【更新可操作时间】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "更新可操作时间失败"
            return invoke_result_data

    @classmethod
    def sign(self,app_id, queue_name, user_id, quit_other_queue=True):
        """
        :description: 签到操作（证明排队的人做出应答，开始办理业务，更新开始操作时间并且将当前用户在其他队列中踢掉）
        :param app_id：应用标识
        :param queue_name：队列名称
        :param user_id：用户标识
        :param quit_other_queue：是否退出其他正在排队的队列，True是False否
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            redis_init = SevenHelper.redis_init()
            zset_name = self._get_zset_name(app_id,queue_name)
            data = str(user_id)
            #判断是否存在排队信息
            score = redis_init.zscore(zset_name, data)
            if score:
                queue_index = int(redis_init.zrank(zset_name, data)) + 1  #当前位置
                if queue_index != 1:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "前面还有人在排队,请耐心等待"
                    return invoke_result_data
                start_timestamp = TimeHelper.get_now_timestamp()
                end_timestamp = start_timestamp + int(config.get_value("queue_operate_time", 300))  #操作时间，单位秒
                hash_name = self._get_user_hash_name(app_id)
                hash_key = f"userid_{data}_queuename_{queue_name}"
                hash_value = redis_init.hget(hash_name, hash_key)
                if not hash_value:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "未查到排队情况,请先排队"
                    return invoke_result_data
                hash_value = SevenHelper.json_loads(hash_value)
                hash_value["start_timestamp"] = start_timestamp
                hash_value["end_timestamp"] = end_timestamp
                hash_value["start_date"] = TimeHelper.timestamp_to_format_time(start_timestamp)
                hash_value["end_date"] = TimeHelper.timestamp_to_format_time(end_timestamp)
                hash_value["progress_status"] = 2
                redis_init.hset(hash_name, hash_key, SevenHelper.json_dumps(hash_value))
                if quit_other_queue == True:
                    #踢掉在其他队列中的排队
                    match_result = redis_init.hscan_iter(hash_name, match=f'userid_{data}_*')
                    for item in match_result:
                        hash_value = SevenHelper.json_loads(item[1])
                        if hash_value["queue_name"] == queue_name:
                            continue
                        self.pop(app_id,hash_value["queue_name"], data)
                invoke_result_data.data = hash_value
                return invoke_result_data
            else:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "未查到排队情况,请先排队"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【签到操作】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "未查到排队情况,请先排队"
            return invoke_result_data
