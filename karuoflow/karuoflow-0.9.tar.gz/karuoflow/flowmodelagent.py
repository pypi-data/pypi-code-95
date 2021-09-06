# -*- encoding: utf-8 -*-
'''
@文件    :flowapp.py
@说明    :
@时间    :2020/09/02 14:27:13
@作者    :caimmy@hotmail.com
@版本    :0.1
'''
from datetime import datetime
from .db.tables import TblFlowJob, TblFlowRule, TblFlowRecords
from sqlalchemy import and_
from .datadef import SIGN_METHOD_JOINT
from .error_code import KaruoFlowErrors

class FlowModelsAgent():
    def __init__(self, db_session):
        self.db = db_session


    def RefuseJobFlow(self, job_item, user_id:str, reason:str):
        """
        拒绝一项审批
        job_id: 
        user_id
        """
        ret_code = KaruoFlowErrors.ERR_UNKOWN
        if job_item:
            _flow_rules = job_item.apply_rules
            current_flow = _flow_rules[job_item.stage]
            if job_item.stage < len(_flow_rules):
                try:
                    if user_id in current_flow["reviewer"]:
                        # 关闭审批任务
                        job_item.result = '0'
                        job_item.TurnClosed()
                        # 追加审批流
                        job_item.flow_list.append(TblFlowRecords(
                            job_id = job_item.id,
                            userid = user_id,
                            submit_tm = datetime.now(),
                            decision = '0',
                            description = reason
                        ))
                        self.db.commit()
                        ret_code = KaruoFlowErrors.SUCCESS
                    else:
                        ret_code = KaruoFlowErrors.ERR_FLOW_OWNER_INVALID
                except Exception as _:
                    self.db.rollback()
                    ret_code = KaruoFlowErrors.ERR_DB_EXCEPTION
                finally:
                    self.db.close()
            else:
                ret_code = KaruoFlowErrors.ERR_FLOW_STAGE_ERROR
        else:
            ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND
        return ret_code

    def RefuseJobFlow_V2(self, job_item, user_id:str, reason:str):
        """
        拒绝一项审批
        v2 支持会签，更新审批流程的decide_stage字段，标记审批记录对应的阶段
        @date: 20210521
        job_id: 
        user_id
        """
        ret_code = KaruoFlowErrors.ERR_UNKOWN
        if job_item:
            _flow_rules = job_item.apply_rules
            current_flow = _flow_rules[job_item.stage]
            if job_item.stage < len(_flow_rules):
                _had_decided = self.db.query(TblFlowRecords).filter(and_(
                    TblFlowRecords.decide_stage==job_item.stage,
                    TblFlowRecords.userid==user_id,
                    TblFlowRecords.job_id==job_item.id
                )).exists()
                if not self.db.query(_had_decided).scalar():
                    # 本人没有对该审批项当前阶段做过决策
                    try:
                        if user_id in current_flow["reviewer"]:
                            # 关闭审批任务
                            job_item.result = '0'
                            job_item.TurnClosed()
                            # 追加审批流
                            job_item.flow_list.append(TblFlowRecords(
                                job_id = job_item.id,
                                userid = user_id,
                                decide_stage = job_item.stage,
                                submit_tm = datetime.now(),
                                decision = '0',
                                description = reason
                            ))
                            self.db.commit()
                            ret_code = KaruoFlowErrors.SUCCESS
                        else:
                            ret_code = KaruoFlowErrors.ERR_FLOW_OWNER_INVALID
                    except Exception as _:
                        self.db.rollback()
                        ret_code = KaruoFlowErrors.ERR_DB_EXCEPTION
                    finally:
                        self.db.close()
                else:
                    ret_code = KaruoFlowErrors.ERR_FLOW_STAGE_RIGHTS
            else:
                ret_code = KaruoFlowErrors.ERR_FLOW_STAGE_ERROR
        else:
            ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND
        return ret_code

    def AgreeJobFlowCoherent(self, job_item, user_id: str, reason: str):
        """
        审批人连续通过一项审批流程
        当一个审批流连续N个阶段都有当前审批人，则一次性通过该审批人所在的所有流程
        """
        ret_code = KaruoFlowErrors.ERR_UNKOWN

        if job_item:
            _flow_rules = job_item.apply_rules
            _agree_flag = False
            if job_item.stage < len(_flow_rules):
                try:
                    while job_item.stage < len(_flow_rules):
                        # 流程的当前阶段没有超过定义的阶段数量
                        current_flow = _flow_rules[job_item.stage]
                        if user_id in current_flow.get("reviewer"):
                            flow_record = TblFlowRecords(
                                job_id = job_item.id,
                                userid = user_id,
                                submit_tm = datetime.now(),
                                decision = '1',
                                description = reason
                            )
                            job_item.flow_list.append(flow_record)
                            # 流程往下流转一次
                            job_item.stage += 1
                            if job_item.stage < len(_flow_rules):
                                # 流程尚未结束，需要往下一阶段路由
                                # 更新审批任务，添加路由节点
                                job_item.reviewer = job_item.apply_rules[job_item.stage].get("reviewer")
                            else:
                                job_item.TurnClosed()
                                # 设置审批任务为通过
                                job_item.result = '1'
                            self.db.flush()
                            _agree_flag = True
                        else:
                            # 当前审批人不在审批列表中
                            if not _agree_flag:
                                ret_code = KaruoFlowErrors.ERR_FLOW_OWNER_INVALID
                            break
                    if _agree_flag:
                        self.db.commit()
                        ret_code = KaruoFlowErrors.SUCCESS
                except Exception as e:
                    self.db.rollback()
                    print(e)
                    ret_code = KaruoFlowErrors.ERR_DB_EXCEPTION
                finally:
                    self.db.close()
            else:
                ret_code = KaruoFlowErrors.ERR_FLOW_STAGE_ERROR
        else:
            ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND
        return ret_code

    def AgreeJobFlow(self, job_item, user_id:str, reason:str):
        """
        通过一项审批流程
        """
        ret_code = KaruoFlowErrors.ERR_UNKOWN

        if job_item:
            _flow_rules = job_item.apply_rules
            if job_item.stage < len(_flow_rules):
                # 流程的当前阶段没有超过定义的阶段数量
                current_flow = _flow_rules[job_item.stage]
            
                if user_id in current_flow.get("reviewer"):
                    try:
                        flow_record = TblFlowRecords(
                            job_id = job_item.id,
                            userid = user_id,
                            submit_tm = datetime.now(),
                            decision = '1',
                            description = reason
                        )
                        job_item.flow_list.append(flow_record)
                        # 流程往下流转一次
                        job_item.stage += 1
                        if job_item.stage < len(_flow_rules):
                            # 流程尚未结束，需要往下一阶段路由
                            # 更新审批任务，添加路由节点
                            job_item.reviewer = job_item.apply_rules[job_item.stage].get("reviewer")
                        else:
                            job_item.TurnClosed()
                            # 设置审批任务为通过
                            job_item.result = '1'
                        self.db.commit()
                        ret_code = KaruoFlowErrors.SUCCESS
                    except Exception as e:
                        self.db.rollback()
                        print(e)
                        ret_code = KaruoFlowErrors.ERR_DB_EXCEPTION
                    finally:
                        self.db.close()
                else:
                    ret_code = KaruoFlowErrors.ERR_FLOW_OWNER_INVALID
            else:
                ret_code = KaruoFlowErrors.ERR_FLOW_STAGE_ERROR
        else:
            ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND
        return ret_code

    def _current_stage_completed_with_joint_method(self, job_id: int, current_stage: int, current_flow: dict) -> bool:
        ret_result = False
        if "method" in current_flow and SIGN_METHOD_JOINT == current_flow["method"]:
            _passed_list = []
            for _reviewer in current_flow["reviewer"]:
                # 判断是否每个审核人都已经做出了同意的决定
                _exists_query = self.db.query(TblFlowRecords).filter(and_(
                    TblFlowRecords.job_id==job_id,
                    TblFlowRecords.decide_stage==current_stage,
                    TblFlowRecords.userid==_reviewer,
                    TblFlowRecords.decision=='1'
                )).exists()
                _passed_list.append(self.db.query(_exists_query).scalar())
            ret_result = len(_passed_list) > 0 and all(_passed_list)
        else:
            ret_result = True
        return ret_result


    def AgreeJobFlow_V2(self, job_item, user_id:str, reason:str, autograph:str=''):
        """
        通过一项审批流程
        v2 支持会签，更新审批流程的decide_stage字段，标记审批记录对应的阶段
        @date: 20210521
        """
        ret_code = KaruoFlowErrors.ERR_UNKOWN

        if job_item:
            _flow_rules = job_item.apply_rules
            if job_item.stage < len(_flow_rules):
                # 流程的当前阶段没有超过定义的阶段数量
                current_flow = _flow_rules[job_item.stage]
            
                if user_id in current_flow.get("reviewer"):
                    _had_decided = self.db.query(TblFlowRecords).filter(and_(
                        TblFlowRecords.decide_stage==job_item.stage,
                        TblFlowRecords.userid==user_id,
                        TblFlowRecords.job_id==job_item.id
                    )).exists()
                    if not self.db.query(_had_decided).scalar():
                        # 本人没有对该审批项当前阶段做过决策
                        try:
                            flow_record = TblFlowRecords(
                                job_id = job_item.id,
                                userid = user_id,
                                decide_stage = job_item.stage,
                                submit_tm = datetime.now(),
                                decision = '1',
                                description = reason,
                                autograph = autograph
                            )
                            job_item.flow_list.append(flow_record)
                            self.db.flush()
                            # 判断当前流程是否已经结束
                            if self._current_stage_completed_with_joint_method(job_item.id, job_item.stage, current_flow):
                                # 流程转移到下一个阶段
                                job_item.stage += 1
                                if job_item.stage < len(_flow_rules):
                                    # 流程尚未结束，需要往下一阶段路由
                                    # 更新审批任务，添加路由节点
                                    job_item.reviewer = job_item.apply_rules[job_item.stage].get("reviewer")
                                else:
                                    job_item.TurnClosed()
                                    # 设置审批任务为通过
                                    job_item.result = '1'
                            self.db.commit()
                            ret_code = KaruoFlowErrors.SUCCESS
                        except Exception as e:
                            self.db.rollback()
                            print(e)
                            ret_code = KaruoFlowErrors.ERR_DB_EXCEPTION
                        finally:
                            self.db.close()
                    else:
                        ret_code = KaruoFlowErrors.ERR_FLOW_STAGE_RIGHTS
                else:
                    ret_code = KaruoFlowErrors.ERR_FLOW_OWNER_INVALID
            else:
                ret_code = KaruoFlowErrors.ERR_FLOW_STAGE_ERROR
        else:
            ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND
        return ret_code

    def AgreeJobFlow_V2Coherent(self, job_item, user_id:str, reason:str, autograph:str=''):
        """
        连续审批通过一项审批流程
        v2 支持会签，更新审批流程的decide_stage字段，标记审批记录对应的阶段
        @date: 20210521
        """
        ret_code = KaruoFlowErrors.ERR_UNKOWN

        if job_item:
            _flow_rules = job_item.apply_rules
            _agree_flag = False
            if job_item.stage < len(_flow_rules):
                try:
                    while job_item.stage < len(_flow_rules):
                        # 流程的当前阶段没有超过定义的阶段数量
                        current_flow = _flow_rules[job_item.stage]
                    
                        if user_id in current_flow.get("reviewer"):
                            _had_decided = self.db.query(TblFlowRecords).filter(and_(
                                TblFlowRecords.decide_stage==job_item.stage,
                                TblFlowRecords.userid==user_id,
                                TblFlowRecords.job_id==job_item.id
                            )).exists()
                            if not self.db.query(_had_decided).scalar():
                                # 本人没有对该审批项当前阶段做过决策
                                flow_record = TblFlowRecords(
                                    job_id = job_item.id,
                                    userid = user_id,
                                    decide_stage = job_item.stage,
                                    submit_tm = datetime.now(),
                                    decision = '1',
                                    description = reason,
                                    autograph = autograph
                                )
                                job_item.flow_list.append(flow_record)
                                # 判断当前流程是否已经结束
                                if self._current_stage_completed_with_joint_method(job_item.id, job_item.stage, current_flow):
                                    # 流程转移到下一个阶段
                                    job_item.stage += 1
                                    if job_item.stage < len(_flow_rules):
                                        # 流程尚未结束，需要往下一阶段路由
                                        # 更新审批任务，添加路由节点
                                        job_item.reviewer = job_item.apply_rules[job_item.stage].get("reviewer")
                                    else:
                                        job_item.TurnClosed()
                                        # 设置审批任务为通过
                                        job_item.result = '1'
                                self.db.flush()
                                _agree_flag = True
                            else:
                                # 决策人针对当前阶段已经进行过决策
                                ret_code = KaruoFlowErrors.ERR_FLOW_STAGE_RIGHTS
                        else:
                            # 决策人无权审核当前节点
                            ret_code = KaruoFlowErrors.ERR_FLOW_OWNER_INVALID
                            break
                    if _agree_flag:
                        self.db.commit()
                        ret_code = KaruoFlowErrors.SUCCESS
                except Exception as e:
                    self.db.rollback()
                    print(e)
                    ret_code = KaruoFlowErrors.ERR_DB_EXCEPTION
                finally:
                    self.db.close()
            else:
                ret_code = KaruoFlowErrors.ERR_FLOW_STAGE_ERROR
        else:
            ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND
        return ret_code

    def NextFlowNode(self, flow_rule_id:int):
        """
        获取下一个流程节点
        """
        next_flow_node = self.db.query(TblFlowRule).filter(
            and_(
                TblFlowRule.prev_id==flow_rule_id,
                TblFlowRule.status=='1'
            )
        ).first()
        return next_flow_node


    