# import from evey possible location
try:
    from Encrypt_Lab.Input import Input
except:
    from Input import Input
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QGridLayout, QWidget, QScrollArea
import numpy as np

# text labels
md5 = {
    'top label': 'Enter your message below',
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

# translate char to binary
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

# translate from binary
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

# convert boolean (0\1) into basis (+\x)
def basis(arr):
  return ['+' if x else 'x' for x in arr]

# simulating transerfing if data between two bases with random choice when bases are different
def transfer(base1, base2, values):
    new_values = values.copy()
    diff = base1 != base2
    new_values[diff] = rand(np.count_nonzero((diff)))
    return new_values

# mark the unmatched values
def transfer_view(base1, base2, values):
    new_values = values.copy()
    new_values[base1!=base2] = 2
    return new_values

# remove the unmatched values
def clean(base1, base2, values):
    return np.delete(values, np.argwhere(base1 != base2))

# mark the unmatched values
def clean_view(base1, base2, values):
    values_new = values.copy()
    values_new[base1!=base2] = 2
    return values_new

# generate random sequence of length N
def rand(N):
    return np.random.randint(2, size=int(N), dtype=bool)

# calculating statical properties of the distribution
def statistics(num):
    safe_len = int(num)
    alice_bases = rand(safe_len)
    eav_bases = rand(safe_len)
    bob_bases = rand(safe_len)
    alice_values = rand(safe_len)
    eav_values = transfer(eav_bases, alice_bases, alice_values)
    bob_values = transfer(eav_bases, bob_bases, eav_values)
    alice_values_clean = clean_view(bob_bases, alice_bases, alice_values)
    bob_values_clean = clean_view(bob_bases, alice_bases, bob_values)
    bob_final = clean(bob_bases, alice_bases, bob_values)
    alice_final = clean(bob_bases, alice_bases, alice_values)

    h = {'Bits count': safe_len, 'Matching bases count': len(alice_final),
         'Matching values count': np.count_nonzero(alice_final == bob_final),
         'Mismatching values count': np.count_nonzero(alice_final != bob_final)} # the actual return dictionary
    h['Disagreement ratio'] = h['Mismatching values count'] / h['Matching bases count']
    return h


# the gui class with PyQt5
class Mod(QScrollArea):
    def __init__(self, parent, s=''):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.ws = []
        self.w = w = QWidget()

        self.setWidgetResizable(True)
        self.setWidget(w)
        l = self.l = QVBoxLayout()

        w.setLayout(l)

        lay = QVBoxLayout()
        self.setLayout(lay)


        # make sure only valid chars enter the textline
        def reg(value):
            import re
            value = value.upper()
            allowed = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','Q','W','Y','Z','!','?','+','-','$']
            return ''.join(c for c in value if c in allowed)

        # Input will create gui inputs and link them to o dictionary
        ww = Input(w, 'string', 'message', opts={'filter':reg,'title':md5['top label'], 'def': 'Y','vertical':'yes', 'center_title':True, 'center_text':True, 'font':20})
        ww.setStyleSheet('background-color: #1ffab2; font-size: 15px; ')
        Input(w, 'bool', 'eav', opts={'title':'is Eve present','def':1,'vertical': 'yes','center_title':True})
        Input(w, 'integer', 'test', opts={'title':'number of test bits','def': 5, 'vertical': 'yes','center_title':True })
        self.play_btn = QPushButton(md5['play'][0])
        self.play_btn.setToolTip(md5['play'][1])
        l.addWidget(self.play_btn)
        self.play_btn.clicked.connect(self.play)

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
        flag = True
        while flag:
            try:
                self.play_real()
                flag = False
            except:
                pass

    def play_real(self):
        for w in self.ws:
            w.deleteLater()
        self.ws = []
        self.Binary_Massage = to_binary(self.w.o['message'])
        self.msg = self.w.o['message']
        self.eav = self.w.o['eav']
        self.check_len = self.w.o['test']
        real_len = len(self.Binary_Massage)
        test_len = max(self.w.o['test'],1)
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

        first_line = []
        second_line = []
        labels = {}
        # print every step in that array
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
                    try:
                        text = getattr(self, s).astype(int) # from bool to int
                    except:
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
                            t.setFixedSize(30, 30)
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
                    self.widget(widget) # add another widget
                else:
                    self.ws.append(widget) # add another widget
                    self.l.addWidget(widget)
                    widget.move(0,0) # move to begging

        # color similar columns
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

        if error:
            self.widget(QLabel('key was not long enough'))
