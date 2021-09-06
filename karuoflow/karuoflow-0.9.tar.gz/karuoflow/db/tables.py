# -*- encoding: utf-8 -*-
'''
@文件    :tables.py
@说明    :
@时间    :2020/09/02 11:46:41
@作者    :caimmy@hotmail.com
@版本    :0.1
'''

from datetime import datetime, date

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum, DateTime, TEXT, JSON, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import and_

Base = declarative_base()

def property2Dict(self, hashid_properties=[]):
    """
    对模型的属性遍历并转换到字典
    :param self:
    :param hashid_properties: 针对列表的属性，需要做hashids
    :return:
    """
    ret_dict = {}
    for c in self.__table__.columns:
        if c.name in ('create_ip', 'status', 'creater'):
            continue
        elif isinstance(getattr(self, c.name, ""), (datetime, date)):
            ret_dict.setdefault(c.name, str(getattr(self, c.name, "")))
        else:
            ret_dict.setdefault(c.name, getattr(self, c.name, ""))
    return ret_dict

if not hasattr(Base, "property2Dict"):
    Base.property2Dict = property2Dict

class TblFlowRule(Base):
    __tablename__ = "karuo_flow_rule"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    prev_id         = Column(Integer, nullable=False, comment="前序节点规则编号")
    icon            = Column(String(512), default="", comment="流程的ICON")
    publisher       = Column(String(128), default="", comment="发布者")
    catalog         = Column(String(128), nullable=False, comment="审批类型")
    subflow         = Column(String(128), default="", comment="子流程，用于应对特殊流程的变形形式")
    name            = Column(String(128), nullable=False, comment="审批名称")
    node_label      = Column(String(64), nullable=False, comment="节点标识")
    method          = Column(String(10), default='or', comment="多人审批方式 or或签 joint会签")
    reviewer        = Column(JSON, comment="决策者列表 json array")
    version         = Column(Integer, default=1, comment="审核流程版本")
    ext_prop        = Column(JSON, comment="附加规则字段，供扩展使用")
    status          = Column(Enum('0', '1', name="e_fr_status"), default='1', comment="审批流程是否启用")
    memo            = Column(String(128), default="", comment="流程的备注信息")
    create_tm       = Column(DateTime, default=datetime.now)

    def rules_pipeline(self, db_session):
        """
        返回类别和版本号都相同的流程链
        """
        return db_session.query(TblFlowRule).filter(and_(
            TblFlowRule.catalog == self.catalog,
            TblFlowRule.subflow == self.subflow,
            TblFlowRule.version == self.version,
            TblFlowRule.status == '1'
        )).order_by(TblFlowRule.prev_id.asc()).all()


class TblFlowJob(Base):
    __tablename__ = "karuo_flow_job"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    flow_index_id   = Column(Integer, nullable=False, comment="审批规则起始节点编号")
    catalog         = Column(String(128), nullable=False, comment="审批类型，冗余记录")
    subflow         = Column(String(128), default="", comment="子流程，用于应对特殊流程的变形形式")
    apply_user      = Column(String(128), nullable=False, comment="申请人编号")
    stage           = Column(Integer, default=0, comment="当前流程所处的阶段")
    reviewer        = Column(JSON, comment="当前阶段的审核人编号")
    submit_tm       = Column(DateTime, default=datetime.now, comment="提出申请时间")
    closed          = Column(Enum('0', '1', name="e_fj_closed"), default='0', comment="流程是否结束")
    recalled        = Column(Enum('0', '1', name="e_fj_recall"), default='0', comment="是否由发起人撤回")
    close_tm        = Column(DateTime, comment="流程结束时间")
    result          = Column(Enum('0', '1', name="e_fj_result"), default='0', comment="流程结果， 0：未通过；1：通过")
    ext_data        = Column(JSON, comment="流程发起时的额外数据，供信息扩展使用")
    apply_rules     = Column(JSON, comment="创建申请任务时的审批流定义")
    rel_prikey      = Column(Integer, index=True, default=0, comment="关联表的主键编号")

    def TurnClosed(self):
        self.closed = '1'
        self.close_tm = datetime.now()

    def IsClosed(self):
        """
        判断任务是否已经关闭
        """
        return '1' == self.closed

    def TransferNextStage(self) -> bool:
        '''
        切换到下一个阶段或者关闭
        :return bool True切入下一个阶段，False流程就此结束
        '''
        ret_next = False
        if not self.IsClosed():
            self.stage += 1
            if self.stage < len(self.apply_rules):
                # 流程尚未结束，需要往下一阶段路由
                # 更新审批任务，添加路由节点
                self.reviewer = self.apply_rules[self.stage].get("reviewer")
                ret_next = True
            else:
                self.TurnClosed()
                # 设置审批任务为通过
                self.result = '1'
                ret_next = False

        return ret_next

class TblFlowRecords(Base):
    __tablename__ = "karuo_flow_records"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    job_id          = Column(Integer, ForeignKey("karuo_flow_job.id"), index=True, comment="申请单号")
    userid          = Column(String(128), nullable=False, comment="用户编号")
    submit_tm       = Column(DateTime, default=datetime.now, comment="提交时间")
    lunch_stage     = Column(Enum('0', '1', name="e_fr_lunch"), default='0', comment="该记录标识是否是流程的发起记录")
    decide_stage    = Column(Integer, default=0, comment="决策阶段")
    decision        = Column(Enum('0', '1', name="e_fr_decision"), default='0', comment="决策结果")
    autograph       = Column(TEXT, default='', comment="手写签名，可以存放base64编码图片")
    description     = Column(TEXT, default='', comment="备注")

    Job             = relationship("TblFlowJob", foreign_keys=[job_id], backref="flow_list")

def InitKaruoflowTables(host, port, db, user, password):
    """
    初始化数据表
    """
    from karuoflow.datadef import DbConfig
    from karuoflow.db.session import createDbSession
    from sqlalchemy.schema import CreateTable
    session = createDbSession(DbConfig(host, db, user, password, port), True)
    print("开始初始化 karuoflow 数据表")
    for table in list(Base.metadata.tables.values()):
        if not session.bind.has_table(table.name):
            create_expr = CreateTable(table)
            session.execute(create_expr)
            print(f"{table.name} 创建成功")
        else:
            print(f"{table.name} 已经存在")
    return True


if "__main__" == __name__:
    import os, sys
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    sys.path.append(root_path)
    InitKaruoflowTables('localhost', 3306, 'duoneng', 'root', 'Ss2018$Ms0802')