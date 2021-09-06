# -*- encoding: utf-8 -*-
'''
@文件    :flowapp.py
@说明    :
@时间    :2020/09/02 14:27:13
@作者    :caimmy@hotmail.com
@版本    :0.1
'''
import copy
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy import and_
from .db.session import createDbSession
from .db.tables import TblFlowRule, TblFlowJob, TblFlowRecords
from .flowmodelagent import FlowModelsAgent
from .datadef import DbConfig, OperResult, FlowCustomRuleNode, QueryParams
from .error_code import KaruoFlowErrors
from .db.tables import InitKaruoflowTables
from .initflow import InitializeFlowsFromConfigure

class KaruoFlow:
    def __init__(self):
        self.db_config = None
        self.db_session = None
        self.flows_agent = None

    @classmethod
    def InitTables(cls, host, port, db, user, password):
        return InitKaruoflowTables(host, port, db, user, password)

    @classmethod
    def CreateModel(cls, dbconfig: DbConfig=None, session: Session=None):
        _instance = cls()
        if session:
            # 优先按照session参数实例化类
            _instance.db_session = session
        elif dbconfig:
            # 初始化数据库连接
            _instance.db_session = createDbSession(dbconfig)
        _instance.flows_agent = FlowModelsAgent(_instance.db_session)
        return _instance

    def BuildAllFlowsFromConfigure(self, config_path: str):
        """
        通过配置文件定义流程
        """
        return InitializeFlowsFromConfigure(config_path, self.db_session)

    def QueryFlow(self, flow_catalog:str, subflow:str=0, version:int = 1):
        """
        查询流程
        返回流程的详细定义
        """
        flow_item = self.db_session.query(TblFlowRule).filter(and_(
            TblFlowRule.catalog == flow_catalog,
            TblFlowRule.version == version,
            TblFlowRule.subflow == subflow,
            TblFlowRule.status == '1'
        )).order_by(TblFlowRule.prev_id.asc()).all()
        if flow_item:
            return KaruoFlowErrors.SUCCESS, [t.property2Dict() for t in flow_item]
        else:
            return KaruoFlowErrors.ERR_DATA_NOT_FOUND, None

    def QueryLastFlow(self, flow_catalog:str, subflow:str=0):
        """
        查询最新的流程
        按照version倒序排列
        """
        flow_item = self.db_session.query(TblFlowRule).filter(and_(
            TblFlowRule.catalog==flow_catalog,
            TblFlowRule.subflow==subflow,
            TblFlowRule.status=='1'
        )).order_by(TblFlowRule.version.desc()).limit(1).first()
        return self.QueryFlow(flow_catalog, flow_item.version) if flow_item else []

    def QueryAllEnabledFlowRules(self):
        """
        获取所有可以使用的审批流程
        @return list
        """
        flow_rules = self.db_session.query(TblFlowRule).filter(and_(
            TblFlowRule.prev_id==0,
            TblFlowRule.status=='1',
        )).all()
        return [_flow.property2Dict() for _flow in flow_rules] 

    # ======================= querys

    def _QueryApplySets(self, user_id: str, catalog:str = None, subflow:str=None, closed_label: str=None, result=None, page=1, size=30):
        """
        根据close字段来查询某个ID作为发起人的审核流程
        catalog: 审批类别
        close_label: 关闭字段内容, ['0', '1']
        result: 审核结果, 0审核驳回；1审核通过；
        page: int 当前页
        size: int 分页大小
        """
        # 对分区参数做安全性校验
        if page < 1: page = 1
        if size < 1: size = 30
        _common_query = self.db_session.query(TblFlowJob).filter(TblFlowJob.apply_user==user_id)
        if catalog:
            _common_query = _common_query.filter(TblFlowJob.catalog==catalog)
        if subflow:
            _common_query = _common_query.filter(TblFlowJob.subflow==subflow)
        if closed_label and closed_label in ['0', '1']:
            _common_query = _common_query.filter(TblFlowJob.closed==closed_label)
        if result and result in ['0', '1']:
            _common_query = _common_query.filter(TblFlowJob.result==result)
        _total = _common_query.count()
        _skip = (page - 1) * size
        match_items = _common_query.order_by(TblFlowJob.id.desc()).offset(_skip).limit(size).all()
        return {
            "total": _total,
            "page": page,
            "size": size,
            "sets": [mi.property2Dict() for mi in match_items]
        }

    def _query_condition(self, session, tbl_obj, condition:QueryParams):
        """
        构造复杂查询
        :param session db_session(sqlalchemy)
        :param tbl_obj table
        :param condition 查询条件
        :return session
        """
        if condition.matches:
            for _match_key in condition.matches:
                session = session.filter(getattr(tbl_obj, _match_key)==condition.matches[_match_key])
        if condition.contains:
            for _contain_key in condition.contains:
                session = session.filter(getattr(tbl_obj, _contain_key).like(f"%{condition.contains[_contain_key]}%"))
        if condition.in_:
            for _ins_key in condition.in_:
                if isinstance(condition.in_[_ins_key], list):
                    session = session.filter(getattr(tbl_obj, _ins_key).in_(condition.in_[_ins_key]))
        return session

    def QueryApplyDecidedByUser(self, user_id: str, catalog: str=None, agree=None, job_condition:QueryParams=None, record_condition:QueryParams=None, page=0, size=0):
        """
        查询用户审批过的记录
        :param user_id str 用户编号
        :param catalog str 审批类型
        :param agree str 是否同意 '0', '1'
        :param condition dict 附加条件
        :param page 页号
        :param size 页大小
        """
        if page < 1: page = 1
        if size < 1: size = 30

        _common_query = self.db_session.query(TblFlowJob, TblFlowRecords).filter(and_(
            TblFlowRecords.lunch_stage=='0',
            TblFlowRecords.userid==user_id,
            TblFlowJob.id==TblFlowRecords.job_id
        ))
        if catalog:
            _common_query = _common_query.filter(TblFlowJob.catalog==catalog)

        if agree and agree in ['0', '1']:
            _common_query = _common_query.filter(TblFlowRecords.decision==agree)
        
        # 针对任务主记录的附加查询
        if job_condition:
            _common_query = self._query_condition(_common_query, TblFlowJob, job_condition)
        # 针对审批流程的附加查询
        if record_condition:
            _common_query = self._query_condition(_common_query, TblFlowRecords, record_condition)
        _total = _common_query.count()
        _skip = (page -1 ) * size
        match_items = _common_query.order_by(TblFlowJob.id.desc()).offset(_skip).limit(size).all()
        return {
            "total": _total,
            "page": page,
            "size": size,
            "sets": [mi[0].property2Dict() for mi in match_items]
        }
        

    def QueryApplyListInDoing(self, user_id, catalog: str=None, subflow: str=None, page=0, size=0):
        """
        查询用户发起的正在进行中的审批记录
        """
        return self._QueryApplySets(user_id, catalog, subflow, '0', None, page, size)

    def QueryApplyListClosed(self, user_id, catalog: str=None, subflow: str=None, page=0, size=0):
        """
        查询用户发起的已经结束的审批记录
        """
        return self._QueryApplySets(user_id, catalog, subflow, '1', None, page, size)

    def QueryApplyListSuccessed(self, user_id, catalog: str=None, subflow: str=None, page=0, size=0):
        """
        查询用户发起的已经流转完成，并审核批准的申请记录
        :param user_id 申请人编号
        :param catalog 申请类别
        """
        return self._QueryApplySets(user_id, catalog, subflow, '1', '1', page, size)

    def QueryApplyListRefused(self, user_id, catalog: str=None, subflow: str=None, page=0, size=0):
        """
        查询用户发起的已经流转完成，并审核拒绝的申请记录
        :param user_id 申请人编号
        :param catalog 申请类别
        """
        return self._QueryApplySets(user_id, catalog, subflow, '1', '0', page, size)


    def QueryReviewTodoList(self, user_id, catalog:str=None, subflow:str=None):
        """
        查询用户正在审批的记录
        """
        _common_query = self.db_session.query(TblFlowJob).filter(and_(
            TblFlowJob.closed=='0',
            # TblFlowJob.reviewer.contains(user_id)
            # 避免contains模糊检索
            func.json_contains(TblFlowJob.reviewer, f'"{user_id}"') == 1
        ))
        if catalog:
            _common_query = _common_query.filter(TblFlowJob.catalog==catalog)
        if subflow:
            _common_query = _common_query.filter(TblFlowJob.subflow==subflow)
        _common_query.order_by(TblFlowJob.id.desc())
        return [j.property2Dict() for j in _common_query.all()]



    # ======================= operations

    def InsertSign(self, jobid:int, reviewer:list, memo:str="", ext_prop:dict=None, method="or", oper_uid=0):
        """
        插入当前节点之前的加签
        :param oper_uid 插入加签的用户编号
        """
        _result = OperResult()
        job_item = self.db_session.query(TblFlowJob).get(jobid)
        if job_item:
            if job_item.IsClosed() or job_item.stage < 1 or job_item.stage >= len(job_item.apply_rules):
                _result.setErrorInfor(KaruoFlowErrors.ERR_FLOW_STAGE_ERROR, KaruoFlowErrors.errorMsg(KaruoFlowErrors.ERR_FLOW_STAGE_ERROR))
            else:
                _apply_rules_copy = copy.deepcopy(job_item.apply_rules)
                if isinstance(_apply_rules_copy, list):
                    # 把加签人插入到当前阶段之前
                    _apply_rules_copy.insert(job_item.stage, {
                        "id": 0,
                        "icon": "",
                        "memo": memo,
                        "name": _apply_rules_copy[0]["name"],
                        "catalog": _apply_rules_copy[0]["catalog"],
                        "subflow": _apply_rules_copy[0]["subflow"],
                        "ext_prop": ext_prop,
                        "reviewer": reviewer,
                        "method": method,
                        "create_tm": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "node_label": f"insertsign by {oper_uid}"
                    })
                job_item.apply_rules = _apply_rules_copy
                job_item.reviewer = reviewer
                try:
                    self.db_session.commit()
                    _result.setSuccess()
                except Exception as e:
                    print(str(e))
                    self.db_session.rollback()
                finally:
                    self.db_session.close()
        else:
            _result.setNotExists()

        return _result

    def AddSign(self, jobid:int, reviewer:list, memo:str="", ext_prop:dict=None, method="or", oper_uid=0):
        """
        对未结束的流程进行加签(实际是转签)
        """
        _result = OperResult()
        job_item = self.db_session.query(TblFlowJob).get(jobid)
        if job_item:
            if job_item.IsClosed() or job_item.stage < 1 or job_item.stage >= len(job_item.apply_rules):
                _result.setErrorInfor(KaruoFlowErrors.ERR_FLOW_STAGE_ERROR, KaruoFlowErrors.errorMsg(KaruoFlowErrors.ERR_FLOW_STAGE_ERROR))
            else:
                _apply_rules_copy = copy.deepcopy(job_item.apply_rules)
                if isinstance(_apply_rules_copy, list):
                    # 追加加签序号是当前处理阶段的下一阶段。
                    # 即，把加签人加到下一个阶段。
                    _insert_sign_stage = job_item.stage + 1
                    _apply_rules_copy.insert(_insert_sign_stage, {
                        "id": 0,
                        "icon": "",
                        "memo": memo,
                        "name": _apply_rules_copy[0]["name"],
                        "catalog": _apply_rules_copy[0]["catalog"],
                        "subflow": _apply_rules_copy[0]["subflow"],
                        "ext_prop": ext_prop,
                        "reviewer": reviewer,
                        "method": method,
                        "create_tm": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "node_label": f"addsign by {oper_uid}"
                    })
                job_item.apply_rules = _apply_rules_copy
                try:
                    self.db_session.commit()
                    _result.setSuccess()
                except Exception as e:
                    print(str(e))
                    self.db_session.rollback()
                finally:
                    self.db_session.close()
        else:
            _result.setNotExists()
        return _result

    def QueryJob(self, jobid):
        """
        查询审批流程任务信息
        """
        _result = OperResult()
        job_item = self.db_session.query(TblFlowJob).get(jobid)
        if job_item:
            _flow_records = job_item.flow_list
            _result.setSuccess({
                "job": job_item.property2Dict(),
                "rules": job_item.apply_rules,
                "flow_records": [_f.property2Dict() for _f in _flow_records]
            })
        else:
            _result.setNotExists()

        return _result

    def ApplyCustom(self, userid: str, catalog: str, desc: str, rules:list, subflow: str="", ext_data:dict={}, rel_prikey=0):
        """
        发起自由流程
        审核参数由业务传入

        """
        job_id = 0
        ret_code = KaruoFlowErrors.ERR_UNKOWN

        _current_stage = 1
        try:
            # 首先创建一个任务，然后初始化流程
            _job = TblFlowJob()
            _job.flow_index_id = 0
            _job.catalog = catalog
            _job.subflow = subflow
            _job.apply_user = userid
            _job.ext_data = ext_data
            _job.stage = _current_stage  # 位于流程的第1个审批阶段
            _job.reviewer = rules[_current_stage].reviewer
            _job.apply_rules = [_r.toDict() for _r in rules]
            _job.rel_prikey = rel_prikey
            self.db_session.add(_job)
            self.db_session.flush()

            _record = TblFlowRecords()
            _record.job_id = _job.id
            _record.lunch_stage = '1'
            _record.userid = userid
            _record.description = desc
            self.db_session.add(_record)

            self.db_session.commit()
            job_id = _job.id
            ret_code = KaruoFlowErrors.SUCCESS
        except Exception as e:
            print(e)
            self.db_session.rollback()
        finally:
            self.db_session.close()

        return ret_code, job_id


    def Apply(self, userid: str, catalog: str, desc: str, subflow:str="", ext_data:dict={}, rel_prikey=0, reviewer_rule:list=None, version:int = 1):
        """
        发起流程
        通过流程类别来发起
        :param catalog str 流程类别
        :param userid str 发起者编号
        :param desc str 流程说明
        :param ext_data 附加信息
        :param version int 流程版本号
        """
        job_id = 0
        ret_code = KaruoFlowErrors.ERR_UNKOWN
        flow_start_node = self.db_session.query(TblFlowRule).filter(and_(
            TblFlowRule.catalog == catalog,
            TblFlowRule.subflow == subflow,
            TblFlowRule.version == version,
            TblFlowRule.status == '1'
        )).order_by(TblFlowRule.prev_id.asc()).first()
        _custom_reviewer_rule_ok = False
        if flow_start_node:
            flow_full_route = flow_start_node.rules_pipeline(self.db_session)
            _current_defined_flow_rules = [_flow_node.property2Dict() for _flow_node in flow_full_route]
            # 判断len(flow_item_list) > 1的目的是确保流程具备审核节点
            if len(flow_full_route) > 1:
                if isinstance(reviewer_rule, list) and (len(flow_full_route) - 1) == len(reviewer_rule):
                    # 额外指定了审核人
                    # 如果要指定审批人员，则应该与审批阶段一致，
                    # 审核人的定义次数应该比流程总阶段数少1，因为审核流程的第一个阶段级提出申请阶段不需要审核
                    for _i in range(len(reviewer_rule)):
                        _current_defined_flow_rules[_i+1]["reviewer"] = reviewer_rule[_i]
                    _custom_reviewer_rule_ok = True
                if None == reviewer_rule or _custom_reviewer_rule_ok:
                    # 没有传入指定审批规则或传入指定审批规则节点满足流程定义
                    _current_stage = 1
                    # 当前阶段，指申请提交后
                    try:
                        # 首先创建一个任务，然后初始化流程
                        _job = TblFlowJob()
                        _job.flow_index_id = flow_start_node.id
                        _job.catalog = catalog
                        _job.subflow = subflow
                        _job.apply_user = userid
                        _job.ext_data = ext_data
                        _job.stage = _current_stage  # 位于流程的第1个审批阶段
                        _job.reviewer = _current_defined_flow_rules[_current_stage]["reviewer"]
                        _job.apply_rules = _current_defined_flow_rules
                        _job.rel_prikey = rel_prikey
                        self.db_session.add(_job)
                        self.db_session.flush()

                        _record = TblFlowRecords()
                        _record.job_id = _job.id
                        _record.userid = userid
                        _record.lunch_stage = '1'
                        _record.description = desc
                        self.db_session.add(_record)

                        self.db_session.commit()
                        job_id = _job.id
                        ret_code = KaruoFlowErrors.SUCCESS
                    except Exception as e:
                        self.db_session.rollback()
                    finally:
                        self.db_session.close()
                else:
                    ret_code = KaruoFlowErrors.ERR_FLOW_INFOR_ERROR

            else:
                ret_code = KaruoFlowErrors.ERR_FLOW_STATUS_INVALID
        else:
            ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND
        return ret_code, job_id
        
    def Recall(self, jobid:int, user_id: str):
        """
        撤回一个审批申请
        1、该申请尚未结束；
        2、该申请是由本人发起
        """
        ret_code = KaruoFlowErrors.ERR_UNKOWN
        _job = self.db_session.query(TblFlowJob).get(jobid)
        if _job:
            if _job.apply_user == user_id:
                if _job.closed == '0':
                    try:
                        _job.recalled = '1'
                        _job.result = '0'
                        _job.TurnClosed()
                        self.db_session.commit()
                        ret_code = KaruoFlowErrors.SUCCESS
                    except Exception as _:
                        self.db_session.rollback()
                        ret_code = KaruoFlowErrors.ERR_DB_EXCEPTION
                    finally:
                        self.db_session.close()
                else:
                    ret_code = KaruoFlowErrors.ERR_FLOW_CLOSED
            else:
                ret_code = KaruoFlowErrors.ERR_FLOW_OWNER_INVALID
        else:
            ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND
        return ret_code
    
    def ExamineCoherent(self, jobid: int, user_id: str, agree: bool, desc: str):
        """
        申请人连续审批
        :param jobid 申请编号
        :param user_id 审批者编号
        :param agree 通过或拒绝
        :param desc 备注信息
        """
        ret_code = KaruoFlowErrors.ERR_UNKOWN
        apply_job = self.db_session.query(TblFlowJob).filter(TblFlowJob.id==jobid).first()
        if apply_job:
            if user_id in apply_job.reviewer:
                if apply_job.closed == '0':
                    if agree:
                        ret_code = self.flows_agent.AgreeJobFlowCoherent(apply_job, user_id, desc)
                    else:
                        ret_code = self.flows_agent.RefuseJobFlow(apply_job, user_id, desc)
                else:
                    ret_code = KaruoFlowErrors.ERR_FLOW_CLOSED
            else:
                ret_code = KaruoFlowErrors.ERR_FLOW_OWNER_INVALID
        else:
            ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND
        return ret_code

    def Examine(self, jobid:int, user_id:str, agree:bool, desc:str):
        """
        审批一项申请
        :param jobid 申请编号
        :param user_id 审批者编号
        :param agree 通过或拒绝
        :param desc 备注信息
        """
        ret_code = KaruoFlowErrors.ERR_UNKOWN
        apply_job = self.db_session.query(TblFlowJob).filter(TblFlowJob.id==jobid).first()
        if apply_job:
            if user_id in apply_job.reviewer:
                if apply_job.closed == '0':
                    if agree:
                        ret_code = self.flows_agent.AgreeJobFlow(apply_job, user_id, desc)
                    else:
                        ret_code = self.flows_agent.RefuseJobFlow(apply_job, user_id, desc)
                else:
                    ret_code = KaruoFlowErrors.ERR_FLOW_CLOSED
            else:
                ret_code = KaruoFlowErrors.ERR_FLOW_OWNER_INVALID
        else:
            ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND
        return ret_code

    def ExamineStageCoherent(self, jobid: int, user_id: str, agree: bool, desc: str, autograph: str): 
        """
        对申请进行阶段审批（同一审批人进行连续审批）
        :param jobid 申请编号
        :param user_id 审批者编号
        :param agree 通过或拒绝
        :param desc 备注信息
        :param autograph 手写签名信息
        """
        ret_code = KaruoFlowErrors.ERR_UNKOWN
        apply_job = self.db_session.query(TblFlowJob).filter(TblFlowJob.id==jobid).first()
        if apply_job:
            if user_id in apply_job.reviewer:
                if apply_job.closed == '0':
                    if agree:
                        ret_code = self.flows_agent.AgreeJobFlow_V2Coherent(apply_job, user_id, desc, autograph)
                    else:
                        ret_code = self.flows_agent.RefuseJobFlow_V2(apply_job, user_id, desc)
                else: ret_code = KaruoFlowErrors.ERR_FLOW_CLOSED
            else: ret_code = KaruoFlowErrors.ERR_FLOW_OWNER_INVALID
        else: ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND

        return ret_code


    def ExamineStage(self, jobid: int, user_id:str, agree:bool, desc:str, autograph:str):
        """
        对申请进行阶段审批
        ** 该函数支持会签操作
        :param jobid 申请编号
        :param user_id 审批者编号
        :param agree 通过或拒绝
        :param desc 备注信息
        :param autograph 手写签名信息
        """
        ret_code = KaruoFlowErrors.ERR_UNKOWN
        apply_job = self.db_session.query(TblFlowJob).filter(TblFlowJob.id==jobid).first()
        if apply_job:
            if user_id in apply_job.reviewer:
                if apply_job.closed == '0':
                    if agree:
                        ret_code = self.flows_agent.AgreeJobFlow_V2(apply_job, user_id, desc, autograph)
                    else:
                        ret_code = self.flows_agent.RefuseJobFlow_V2(apply_job, user_id, desc)
                else: ret_code = KaruoFlowErrors.ERR_FLOW_CLOSED
            else: ret_code = KaruoFlowErrors.ERR_FLOW_OWNER_INVALID
        else: ret_code = KaruoFlowErrors.ERR_DATA_NOT_FOUND

        return ret_code
        
    def TransferNextStage(self, jobid: int):
        """
        对申请强行转入下一个阶段
        :param jobid 申请编号
        :param user_id 审批者编号
        """
        _result = OperResult()
        apply_job = self.db_session.query(TblFlowJob).filter(TblFlowJob.id==jobid).first()
        if apply_job:
            if not apply_job.IsClosed():
                try:
                    transed = apply_job.TransferNextStage()
                    self.db_session.commit()
                    _result.setSuccess({
                        "closed": not transed       # 流程是否结束
                    })
                except SQLAlchemyError as e:
                    self.db_session.rollback()
                    _result.setErrorInfor(KaruoFlowErrors.ERR_DB_EXCEPTION, KaruoFlowErrors.errorMsg(KaruoFlowErrors.ERR_DB_EXCEPTION))
                finally:
                    self.db_session.close()
            else: _result.setErrorInfor(KaruoFlowErrors.ERR_FLOW_CLOSED, KaruoFlowErrors.errorMsg(KaruoFlowErrors.ERR_FLOW_CLOSED))
        else: _result.setErrorInfor(KaruoFlowErrors.ERR_DATA_NOT_FOUND, KaruoFlowErrors.errorMsg(KaruoFlowErrors.ERR_DATA_NOT_FOUND))
        
        return _result