import sys
from PyQt5.QtWidgets import QApplication
from Input import Input
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout,QHBoxLayout,QGridLayout, QWidget, QScrollArea, QGroupBox, QMainWindow, QScrollBar
import numpy as np

md5 = {
    'msg':['Message','The message that Alice will send to Bob.'],
    'Binary_Massage':['Binary Massage','The binary sequence which is equivalent to the message.'],
    'alice_values':["Alice's Bits", "The bits that are sent by Alice to Bob."],
    'alice_bases':["Alice's Bases","The sequence of bases that Alice uses for sending the bits."],
    'alice_final':["Alice's Final Bits","Alice's bits after dismissing the bits where Alice and Bob didn't choose the same base"],
    'eav_bases':["Eve's Bases",'The sequence of bases that Alice uses for receiving the bits.'],
    'eav_values':["Eve's Bits","The bits that are received by Eve from Alice and are sent to Bob."],
    'bob_bases':["Bob's Bases",'The sequence of bases that Bob uses for receiving the bits.'],
    'bob_values':["Bob's Bits","The bits that are received by Bob from Eve."],
    'bob_values_clean':["Bob's Reduced Bits","Bob's bits after cleaning the bits where Alice and Bob didn't choose the same bases."],
    'bob_final':["Bob's Final Bits","Bob's bits after dismissing the bits where Alice and Bob didn't choose the same base"],
    'safe_channel':['Is the Chanel Safe?',"If 'True' - Eve wasn't detected. If 'False' - Eve was detected."],
    'bob_after_test':['Key',"The bits that are used for encryption (bits that weren't in use for the testing of the presence of Eve)."],
    'enc_msg':['Encrypted Message','The message that Alice sent to Bob after using the key for encrypting the message.'],
    'dyc_msg':['The Decrypted Message','The message that Bob received after using the key for decrypting the message.'],
    'dyc_msg_str':['The Received Message','The message that Bob received after using the key for decrypting the message.'],
    'play':['Start procudre','start botton'],
}


def to_binary(s):
    h = {
        '!': 26,
        '?': 27,
        '+': 28,
        '-': 29,
        '$': 30,
        '₪': 31,
    }
    s = s.upper()
    binary = ''
    for c in s:
        num = ord(c) - ord('A')
        if not 0 <= num <= 25:
            num = h[c]

        binary = binary + '{0:05b}'.format(num)
    return binary

def from_binary(s):
    h = {
        26:'!' ,
        27:'?' ,
        28:'+' ,
        29:'-' ,
        30:'$' ,
        31:'₪'
    }
    ints = []
    chunk = ''
    for bit in s:
        chunk = chunk + str(bit)
        if len(chunk) == 5:
            ints.append(chunk)
            chunk = ''
    ints = [int(aa,2) for aa in ints]
    word = ''
    for n in ints:
        if n in h:
            word = word + h[n]
        else:
            word = word + chr(65+n)

    return word

def basis(arr):
  return ['+' if x else 'x' for x in arr]

def transfer(base1, base2, values):
    new_values = values.copy()
    diff = base1 != base2
    new_values[diff] = rand(np.count_nonzero((diff)))
    return new_values

def transfer_view(base1, base2, values):
    new_values = values.copy()
    new_values[base1!=base2] = 2
    return new_values

def clean(base1, base2, values):
    return np.delete(values, np.argwhere(base1 != base2))

def clean_view(base1, base2, values):
    values_new = values.copy()
    values_new[base1!=base2] = 2
    return values_new

def rand(N):
  return np.random.randint(2, size=int(N))

class Mod(QScrollArea):
    def __init__(self, parent, s=''):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # self.setStyleSheet("""
        #     border: 100px black;
        #     font-size: 22px;
        #     font-weight: bold;
        #     text-align: right;
        #     background-color: rgb(200,200,200);
        #     color: rgb(180,50,50);
        # """)
        self.ws = []
        self.w = w = QWidget()

        self.setWidgetResizable(True)
        self.setWidget(w)
        l = self.l = QVBoxLayout()

        w.setLayout(l)

        lay = QVBoxLayout()
        self.setLayout(lay)

        def reg(val):
            print(val)

        ww = Input(w, 'string', 'message', opts={'on_update':reg, 'def': 'YES!','vertical':'yes', 'center_title':True, 'center_text':True, 'font':20})
        ww.setStyleSheet('background-color: #1ffab2; font-size: 15px; ')
        Input(w, 'bool', 'eav', opts={'def':1,'vertical': 'yes','center_title':True})
        Input(w, 'integer', 'test', opts={'def': 5, 'vertical': 'yes','center_title':True })
        self.play_btn = QPushButton(md5['play'][0])
        self.play_btn.setToolTip(md5['play'][1])
        l.addWidget(self.play_btn)
        self.play_btn.clicked.connect(self.play)
        # self.play()

    def widget(self, w, center = True, big=False):
        if str(w.__class__)=="<class 'PyQt5.QtWidgets.QLabel'>":
            w.setStyleSheet('background-color: #1ffab2; font-size: 15px; ')
        if big:
            w.setStyleSheet(f"font-size: 25px")
        self.ws.append(w)
        if center:
            self.l.addWidget(w, alignment=Qt.AlignCenter)
        else:
            self.l.addWidget(w)

    def play(self):
        for w in self.ws:
            w.deleteLater()
        self.ws = []
        self.Binary_Massage = to_binary(self.w.o['message'])
        self.msg = self.w.o['message']
        self.eav = self.w.o['eav']
        self.check_len = self.w.o['test']
        real_len = len(self.Binary_Massage)
        test_len = max(self.w.o['test'],10)
        sigma = int((real_len + test_len) ** 0.5)
        safe_len = int(2 * (real_len + test_len) + 1 * sigma)
        self.alice_bases = rand(safe_len)
        self.eav_bases = rand(safe_len)
        self.bob_bases = rand(safe_len)
        self.alice_values = rand(safe_len)

        self.eav_values = transfer(self.eav_bases,self.alice_bases, self.alice_values)
        if self.eav:
            self.bob_values = transfer(self.eav_bases, self.bob_bases, self.eav_values)
        else:
            self.bob_values = transfer(self.alice_bases, self.bob_bases, self.alice_values)
        ########## encription ##################
        self.alice_values_clean = clean_view(self.bob_bases,self.alice_bases, self.alice_values)
        self.bob_values_clean = clean_view(self.bob_bases, self.alice_bases, self.bob_values)
        self.bob_final = clean(self.bob_bases, self.alice_bases, self.bob_values)
        self.alice_final = clean(self.bob_bases, self.alice_bases, self.alice_values)

        self.safe_channel = np.array_equal(self.alice_final[-self.check_len:], self.bob_final[-self.check_len:])
        self.bob_after_test = self.bob_final.copy()[:-self.check_len]
        self.alice_after_test = self.alice_final.copy()[:-self.check_len]
        self.real_key_alice = self.alice_after_test[:real_len]
        self.real_key_bob = self.bob_after_test[:real_len]
        # self.long_key = self.alice_values_clean[self.check_len:]

        error = False
        eff_msg = self.Binary_Massage
        if len(self.real_key_bob) < len(self.Binary_Massage):
            error = True
            eff_msg = eff_msg[:len(self.real_key_bob)]

        self.enc_msg = np.bitwise_xor(np.array([int(aa) for aa in eff_msg]) ,self.real_key_alice)
        self.dyc_msg = np.bitwise_xor(self.enc_msg, self.real_key_bob)
        self.dyc_msg_str = from_binary(self.dyc_msg)

        # self.key = self.alice_values_clean[self.check_len:]

        first_line = []
        second_line = []
        labels = {}
        for i, s in enumerate(['msg','Binary_Massage', 'alice_values', 'alice_bases',  'eav_bases', 'eav_values',
                  'bob_bases', 'bob_values', 'bob_values_clean', 'alice_final','bob_final', 'safe_channel', 'bob_after_test','enc_msg', 'dyc_msg', 'dyc_msg_str']):#'remobe different bases','alice_values_clean', 'bob_values_clean','safe_channel', 'long_key', 'real_key','enc_msg', 'dyc_msg']):
            if 'eav' in s and not self.eav:
                continue
            l = QLabel(md5[s][0])
            l.setToolTip(md5[s][1])
            self.widget(l, big=True)
            if s in ['safe_channel']:
                self.widget(QLabel(str(self.safe_channel)), big=True)
                continue
            widget = QWidget(self)
            ll = QGridLayout()
            widget.setLayout(ll)
            arr = []
            labels[s] = arr
            if hasattr(self,s):
                if 'base' in s:
                    text = basis(getattr(self, s))
                else:
                    text = getattr(self, s)

                for j in range(safe_len):
                    color = 'black'
                    if j <= len(text) - 1:
                        char = text[j]
                    else:
                        char = ' '
                    if char == 2:
                        char = ''
                    t = QLabel(str(char))
                    if s in ['msg', 'dyc_msg','real_key','enc_msg', 'bob_final','alice_final', 'bob_after_test', 'dyc_msg_str'] and char == ' ':
                        continue
                    else:
                        if s in ['msg',]:#'dyc_msg'
                            t.setFixedSize(30*5+24, 30)
                        else:
                            t.setFixedSize(30,30)
                    t.setStyleSheet(f'border-color:{color};  border-width: 3px;border-style: solid; text-align: center')
                    t.setAlignment(Qt.AlignCenter)
                    if s == 'msg':
                        first_line.append(t)
                        self.msg_widget = widget
                    if s == 'Binary_Massage':
                        self.fg_widget = widget
                        second_line.append(t)

                    ll.addWidget(t, i, j)
                    arr.append(t)
                if s != 'msg':
                    self.widget(widget)
                else:
                    self.ws.append(widget)
                    self.l.addWidget(widget, alignment=Qt.AlignLeft)
                    widget.move(0,0)

        for i, (a_v, a_b, b_v, b_b) in enumerate(zip(labels['alice_values'], labels['alice_bases'], labels['bob_values'], labels['bob_bases'])):
            if a_b.text() != b_b.text():
                color = 'red'
            elif a_v.text() == b_v.text():
                color = 'green'
            else:
                color = 'orange'
            for col in ['alice_values', 'alice_bases', 'bob_values', 'bob_bases', 'eav_bases', 'eav_values', 'bob_values_clean']:
                if col in labels:
                    labels[col][i].setStyleSheet(f'border-color:{color};  border-width: 3px;border-style: solid; text-align: center')

            # bob.setStyleSheet(f'border-color:{color};  border-width: 3px;border-style: solid; text-align: center')
            # ali.setStyleSheet(f'border-color: {color}')
            # bob.setStyleSheet(f'border-color: {color}')
        if error:
            self.widget(QLabel('key was not long enogth'))

            # self.widget(QLabel(text))
        # break







        # Input(w, 'integer', 'time',opts={'def':1})
        # Input(w, 'float', 'days', opts={'def': 9})
        # for inpt in [
        #     ['rate', [0, 5]],
        #     ['modulation', [0, 1]],
        #     ['spurious', [0, 0.1], 0.01],
        #     ['2 pi omega', [0, 2 * 3.1415927], 1],
        #
        #     ['N', [3, 1000]],
        # ]:
        #     if len(inpt) == 3:
        #         title, minmax, deff = inpt
        #     if len(inpt) == 2:
        #         title, minmax = inpt
        #         deff = None
        #     is_float = not (title in ['N'])
        #     args = {'slide_minmax': minmax, 'float': is_float}
        #     if deff is not None:
        #         args['def'] = deff
        #     Input(w, 'slider', title, opts=args)
        # Input(w, 'radio', 'data to use:',{'radios':['simulated','original'], 'def_index':0})


        # start = QPushButton('start')
        # start.clicked.connect(self.crate_data)
        # l.addWidget(start)
        # full_start = QPushButton('full start')
        # full_start.clicked.connect(partial(self.crate_data, True, True) )
        # l.addWidget(full_start)
        # w.resize(250, 150)
        # w.move(300, 300)
        # w.setWindowTitle('Simple')
        # self.figs = []
        # self.axes = []
        #
        # for name in ['rate', 'main_fit','data', 'fft', 'omegas']:
        #     fig_name = f'{name}_fig'
        #     ax_name = f'{name}_ax'
        #     fig = Figure()
        #     setattr(self, fig_name, fig)
        #     self.figs.append(fig)
        #
        #     ax = fig.subplots()
        #     setattr(self, ax_name, ax)
        #     self.axes.append(ax)
        #
        #
        # self.rate_fig.suptitle('daily rate')
        # data_w = FigureCanvas(self.rate_fig)
        # data_w.setMinimumSize(200, 200)
        # l.addWidget(data_w)
        #
        #
        # self.data_fig.suptitle('fit to data')
        #
        #
        # data_w = FigureCanvas(self.data_fig)
        # data_w.setMinimumSize(200, 200)
        # l.addWidget(data_w)
        #
        # fit_w = FigureCanvas(self.main_fit_fig)
        # fit_w.setMinimumSize(200, 200)
        # # l.addWidget(fit_w)




#
# app = QApplication(sys.argv)
#
# m = QMainWindow()
# m.resize(1000, 1000)
# w= Mod(m)
#
# m.setCentralWidget(w)
# m.show()
#
# sys.exit(app.exec_())
#
