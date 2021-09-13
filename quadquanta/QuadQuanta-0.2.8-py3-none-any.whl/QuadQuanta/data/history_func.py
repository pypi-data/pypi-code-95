# 分钟级别数据保存，按日保存
# elif frequency in ['min', 'minute']:
#     code_list = list(set(query_clickhouse(start_time=start_time, end_time=end_time)['code']))
#     code_list.sort()
#     for i in tqdm(range(len(code_list))):
#         exist_max_datetime = query_exist_max_datetime(
#             code_list[i], frequency, client)[0][0]
#         if str(exist_max_datetime) > config.start_date:  # 默认'2014-01-01'
#             _start_time = str(exist_max_datetime +
#                               datetime.timedelta(hours=18))
#         else:
#             if start_time <= config.start_date:  # 默认'2014-01-01'
#                 start_time = config.start_date + ' 9:00:00'
#             _start_time = start_time
#         try:
#             if _start_time <= end_time:
#                 insert_clickhouse(
#                     get_jq_bars(code_list[i], _start_time, end_time,
#                                 frequency), frequency, client)
#             else:
#                 logger.debug(f"{code_list[i]}:当前日期段数据已保存")
#         # TODO log输出
#         except Exception as e:
#             logger.warning(f"{code_list[i]}:error:{e}")
#             # raise Exception('Insert minute data error', code_list[i])
#             continue