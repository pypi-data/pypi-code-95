import re
import sys

# 控制仓数据
# 25(起始位)00(仓位数据)ttttpppppppphhhh(温湿度大气压模块传感器数据)xxxxyyyyzzzzxxxxyyyyzzzzRRRRPPPPYYYYxxxxyyyyzzzz(九轴数据)DDDDcccc(声呐数据)WWWWdddd(水深传感器)0000(奇偶校验位)FFFF(结束位)

class base_parser():
    
    def __init__(self):
        self.re_ = None
        self.pattern = None

    def parse(self, sentence):

        match = self.pattern.match(sentence)
        if not match:
            print('unregular sentence')
            sys.exit()
        sentence_dict_hex = match.groupdict()
        print(sentence_dict_hex)
        sentence_dict_dec = {}
        for key, value in sentence_dict_hex.items():
            sentence_dict_dec[key] = int(value, 16)
        print(sentence_dict_dec)
        return sentence_dict_hex, sentence_dict_dec

class up_parser(base_parser):

    def __init__(self):
        
        super().__init__()
        self.re_ = '(?P<起始位>25)' \
                  '(?P<仓位>00|01)' \
                  '(?P<温度>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<气压>([0-9]|[a-f]|[A-F]){8})' \
                  '(?P<湿度>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<加速度Ax>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<加速度Ay>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<加速度Az>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<角速度Wx>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<角速度Wy>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<角速度Wz>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<角度Roll>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<角度Pitch>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<角度Yaw>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<磁场Hx>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<磁场Hy>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<磁场Hz>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<声呐>([0-9]|[a-f]|[A-F]){8})' \
                  '(?P<声呐确信度>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<水温>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<水深>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<确认位>([0-9]|[a-f]|[A-F]){2})' \
                  '(?P<结束位>([0-9]|[a-f]|[A-F]){4})' 

        self.pattern = re.compile(self.re_)

    # def parse(self, sentence):

    #     match = self.pattern.match(sentence)
    #     if not match:
    #         print('unregular sentence')
    #         sys.exit()
    #     sentence_dict_hex = match.groupdict()
    #     print(sentence_dict_hex)
    #     sentence_dict_dec = {}
    #     for key, value in sentence_dict_hex.items():
    #         sentence_dict_dec[key] = int(value, 16)
    #     print(sentence_dict_dec)
    #     return sentence_dict_dec 

# 起始位	前进后退		旋转或侧推		垂直		灯光		云台		传送		机械臂1		机械臂2		机械臂3		机械臂4		机械臂5		机械臂6		预留PWM		模式开关	验证位	结束位
# 0x25	500-2500		500-2500		500-2500		500-2500		500-2500		500-2500		500-2500		500-2500		500-2500		500-2500		500-2500		500-2500		500-2500				0x21
# 0	1	2	3	4	5	6	7	8	9	10	11	12	13	14	15	16	17	18	19	20	21	22	23	24	25	26	27	28	29



class down_parser(base_parser):

    def __init__(self):
        
        self.re_ = '(?P<起始位>25)' \
                  '(?P<前进后退>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<旋转或侧推>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<垂直>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<灯光>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<云台>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<传送>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<机械臂1>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<机械臂2>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<机械臂3>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<机械臂4>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<机械臂5>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<机械臂6>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<预留PWM>([0-9]|[a-f]|[A-F]){4})' \
                  '(?P<模式开关>([0-9]|[a-f]|[A-F]){2})' \
                  '(?P<验证位>([0-9]|[a-f]|[A-F]){2})' \
                  '(?P<结束位>21)' 

        self.pattern = re.compile(self.re_)

    # def parse(self, sentence):

    #     match = self.pattern.match(sentence)
    #     if not match:
    #         print('unregular sentence')
    #         sys.exit()
    #     sentence_dict_hex = match.groupdict()
    #     print(sentence_dict_hex)
    #     sentence_dict_dec = {}
    #     for key, value in sentence_dict_hex.items():
    #         sentence_dict_dec[key] = int(value, 16)
    #     print(sentence_dict_dec)


if __name__ == '__main__':
    x = up_parser()
    x.parse('25001234123456780bcddddaaaacccceeeeffff99990000777755554444ccccaaaaaaaacccc1111dddd00FFFFeeeee')
    y = down_parser()
    y.parse('2505DC05DC05DC05DC05DC05DC05DC05DC05DC05DC05DC05DC05DC080021')
