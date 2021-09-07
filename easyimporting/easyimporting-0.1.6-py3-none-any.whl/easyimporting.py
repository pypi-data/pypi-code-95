import os, subprocess, importlib, time, sys
def testOutDated():
    import threading
    def huitbis():
        t, y, animation, write= threading.currentThread(), 0, "|/-\\", "get outdated"
        while getattr(t, "do_run", True):
            y+=1
            ret = ""
            for i in range(len(write)):
                if i == y % len(write):
                    ret += write[i].upper()
                else:
                    ret += write[i]
            sys.stdout.write("\r" +ret+" : "+animation[y % len(animation)])
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("                                                          ")
    t = threading.Thread(target=huitbis)
    t.start()
    import subprocess
    ret = subprocess.getoutput("python -m pip list --outdated")
    t.do_run = False
    time.sleep(0.14)
    if ret:
        print(ret)
        ret = ret.split("\n")
        ret.pop(0)
        ret.pop(0)
        for i in range(len(ret)):
            ret[i] = (ret[i].split(" "))[0]
        temp = "py -m pip install --upgrade "
        for i in range(len(ret)):
            temp+=f"pip {ret[i]} "
        os.system(temp)
        print(temp)
    else:
        print("you run all curent version")
def importing(data, exeption=None, From=""):
        """ return a list with all package requiered but without error """
        import threading
        def waiting():
            t, y, animation, write= threading.currentThread(), 0, "|/-\\", "installing module"
            while getattr(t, "do_run", True):
                y+=1
                ret = ""
                for i in range(len(write)):
                    if i == y % len(write):
                        ret += write[i].upper()
                    else:
                        ret += write[i]
                sys.stdout.write("\r" +ret+" : "+animation[y % len(animation)])
                time.sleep(0.1)
        def getNumber(data, y=len(data), ret=0):
            moin=0
            if data[y].find("(") != -1:
                debut=data[y].find("(")
                fin=data[y].find(")")
                ret = ""
                for i in range(debut+1, fin):
                    moin-=1
                    ret += str(data[y][i])
                moin-=2
                ret = int(ret)
            else:
                ret+=1
            if moin == 0:
                moin=len(data[y])
            return data[y][0:moin], ret
        loop, ret, RET, retour, exept, lenExeption = 0, 0, 0, [], [], 0
        if exeption!=None:
            exeption = exeption.split(" ")
            lenExeption = len(exeption)
        From = From.split(" ")
        for y in range(lenExeption):
            if exeption!=None:
                exept, ret = getNumber(exeption, y=y, ret=ret)
            if From!=None:
                FROM, RET = getNumber(From, y=y, ret=RET)
            while loop < len(data.split(" ")):
                loop+=1
                dataLoop=data.split(" ")[loop-1]
                temp = False
                try:
                    try:
                        importlib.import_module(dataLoop)
                    except:
                        importlib.import_module(dataLoop+"."+FROM)
                    temp = True
                except:
                    try:
                        t = threading.Thread(target=waiting)
                        t.start()
                        try:
                            if loop == ret:
                                result = subprocess.getoutput("pip install "+exept)
                            else:
                                result = subprocess.getoutput("pip install "+dataLoop)
                            try:
                                importlib.import_module(dataLoop)
                            except:
                                importlib.import_module(dataLoop+"."+FROM)
                        except:
                            try:
                                if loop == ret:
                                    result = subprocess.getoutput("py -m pip install "+exept)
                                else:
                                    result = subprocess.getoutput("py -m pip install "+dataLoop)
                                try:
                                    importlib.import_module(dataLoop)
                                except:
                                    importlib.import_module(dataLoop+"."+FROM)
                            except:
                                if loop == ret:
                                    result = subprocess.getoutput("python -m pip install "+exept)
                                else:
                                    result = subprocess.getoutput("python -m pip install "+dataLoop)
                        t.do_run = False
                        time.sleep(0.2)
                        if (result.split("\n"))[-1][0:6] == "ERROR:":
                            break
                        temp = True
                    except:
                        pass
                finally:
                    if temp == True:
                        try:
                            retour.append(importlib.import_module(dataLoop))
                        except:
                            print(f"{dataLoop} n'existe pas")
                    else:
                        print(f"{dataLoop} {exept} n'a pas marcher")
                    if loop == ret:
                        break
        while loop < len(data.split(" ")):
            loop+=1
            dataLoop=data.split(" ")[loop-1]
            temp = False
            try:
                try:
                    importlib.import_module(dataLoop)
                except:
                    importlib.import_module(dataLoop+"."+FROM)
                temp = True
            except:
                try:
                    t = threading.Thread(target=waiting)
                    t.start()
                    try:
                        result = subprocess.getoutput("pip install "+dataLoop)
                        try:
                            importlib.import_module(dataLoop)
                        except:
                            importlib.import_module(dataLoop+"."+FROM)
                    except:
                        try:
                            result = subprocess.getoutput("python -m pip install "+dataLoop)
                            try:
                                importlib.import_module(dataLoop)
                            except:
                                importlib.import_module(dataLoop+"."+FROM)
                        except:
                            result = subprocess.getoutput("py -m pip install "+dataLoop)
                    t.do_run = False
                    time.sleep(0.2)
                    if (result.split("\n"))[-1][0:6] == "ERROR:":
                        break
                    temp = True
                except:
                    pass
            finally:
                if temp == True:
                    try:
                        try:
                            retour.append(importlib.import_module(dataLoop))
                        except:
                            retour.append(importlib.import_module(dataLoop+"."+FROM))
                    except:
                        print(f"{dataLoop} n'existe pas")
                else:
                    print(f"{dataLoop} {exept} n'a pas marcher")
        return retour
def example():
        print('\nlist=importing("module_name1 module_name2", "exeption_name(2)"\n')
if __name__ == "__main__":
    # importing.example()
    testOutDated()
    # importing("scipy")