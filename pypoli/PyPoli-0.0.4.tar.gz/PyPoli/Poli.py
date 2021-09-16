# coding:gbk
import jr_jr
import qq_JZ
import weather_api
import baid_dr
import sj_pz
import Hello
import Time
import calculation
import open_url_exe
import qq_tx_mz
import chp
import LT
import kgmv
import xh
import lishi
import twqh
import tgrj
import djt
import rkl
import sao_hua
import sjyy
import yq
import fy
import gen
from RandomKey import key as k

HELLO = ['hello']
AGE = ['多大了', '年龄']
XZ_TIME = ['现在时间']
ADDITION_JIA = ['帮我算一下加法']
MULTIPLICATION = ['帮我算一下乘法']
DIVISION = ['帮我计算一下除法']
OPEN_URL_EXE = ['帮我打开']
JR_JR = ['今天是什么日子']
QQ_JZ = ['QQ价值检测']
WEATHER_API = ['查询天气']
BAIDU_RS = ['百度热搜']
SJ_PZ = ['手机配置查询']
QQ_TX_MZ = ['查询QQ头像']
CHP = ['夸我']
KGMV = ['歌曲mv']
XH = ['笑话']
LS_SJ = ['今日历史事件']
TWQH = ['土味情话']
TGRJ = ['舔狗日记']
DJT = ['毒鸡汤']
RKL = ['绕口令']
SAO = ['骚话']
SJYY = ['随机一言']
YQ = ['查询疫情']
FY = ['翻译']
GEN = ['梗百科']

KEY_letter = '生成一个字母密码'
KEY_str = '生成一个字符串密码'
YK_LT = '优客api聊天'
TL_BOT = '图灵机器人'
List_PRINT = (
    HELLO,
    AGE,
    XZ_TIME,
    ADDITION_JIA,
    MULTIPLICATION,
    DIVISION,
    OPEN_URL_EXE,
    JR_JR,
    QQ_JZ,
    WEATHER_API,
    BAIDU_RS,
    SJ_PZ,
    XH,
    LS_SJ,
    TWQH,
    TGRJ,
    DJT,
    RKL,
    SAO,
    SJYY,
    YQ,
    FY,
    GEN,
)
str_PRINT = (KEY_letter, KEY_str, YK_LT, TL_BOT)
while True:
    message = input("USER:")
    h = Hello.PoliRobot_Hello('Poli', '1', '你有什么想说的呢？')
    '''hello'''
    if message in HELLO:
        h.Hello()
        # h.Poilage()
        h.Poilmessage()
        continue

    '''年龄'''
    if message in AGE:
        h.Poilage()
        continue
    '''现在时间'''
    if message in XZ_TIME:
        Time.xz_time()
        continue
    '''计算加法'''
    if message in ADDITION_JIA:
        calculation.addition()
        continue
    '''计算乘法'''
    if message in MULTIPLICATION:
        calculation.multiplication()
        continue
    '''计算除法'''
    if message in DIVISION:
        calculation.division()
        continue
    '''open打开'''
    if message in OPEN_URL_EXE:
        open_url_exe.open_url_exe()
        continue
    '''大小写字母密码生成'''
    if message == KEY_letter:
        sl = int(input("请输入要生成密码位数："))
        k.key_letter(sl)
        continue
    '''字符串密码生成'''
    if message == KEY_str:
        num = int(input("请输入要生成几位："))
        k.key_str(num)
        continue
    '''今日节日'''
    if message in JR_JR:
        jr_jr.jr_jr()
        continue
    '''QQ价值'''
    if message in QQ_JZ:
        qq_JZ.qq_JZ()
        continue
    '''天气查询'''
    if message in WEATHER_API:
        weather_api.weather_api()
        continue
    '''百度热搜'''
    if message in BAIDU_RS:
        baid_dr.baidu_rs()
        continue
    '''手机配置查询'''
    if message in SJ_PZ:
        sj_pz.sj_pz()
        continue
    '''QQ头像名字查询'''
    if message in QQ_TX_MZ:
        qq_tx_mz.qq_tx_mz()
        continue
    '''夸我'''
    if message in CHP:
        chp.chp()
        continue
    '''优客API聊天'''
    if message == YK_LT:
        print("已打开优客api聊天")
        print("输入q退出！")
        LT.LT()
        continue
    '''图灵机器人'''
    if message == TL_BOT:
        print("输入q退出")
        from tl_bot import bot

        continue
    '''酷狗mv'''
    if message in KGMV:
        kgmv.gn()
        continue
    '''笑话'''
    if message in XH:
        xh.XH()
        continue
    '''历史上今天'''
    if message in LS_SJ:
        lishi.ls_sj()
        continue
    '''土味情话'''
    if message in TWQH:
        twqh.twqh()
        continue
    '''舔狗日记'''
    if message in TGRJ:
        tgrj.tgrj()
        continue
    '''毒鸡汤'''
    if message in DJT:
        djt.djt()
        continue
    '''绕口令'''
    if message in RKL:
        rkl.rkl()
        continue
    '''骚话'''
    if message in SAO:
        sao_hua.SAO()
        continue
    '''随机一言'''
    if message in SJYY:
        sjyy.yi()
        continue
    '''疫情'''
    if message in YQ:
        yq.yq()
        continue
    '''翻译'''
    if message in FY:
        fy.fy()
        continue
    '''梗百科'''
    if message in GEN:
        gen.gen()
        continue
    '''help'''
    if message == 'help':
        for i in List_PRINT:
            print(i)
        for i in str_PRINT:
            print(i)
        continue
    '''quit'''
    if message == 'q' or message == 'quit':
        print("再见主人！")
        break
    else:
        print("\n未识别到此命令！")
        print("输入help，查询指令\n")
        sjyy.yi()
        print("\n")
        continue
