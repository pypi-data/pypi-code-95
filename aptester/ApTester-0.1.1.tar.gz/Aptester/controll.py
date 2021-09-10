import subprocess
import pathlib
import os
import re
import sys

class Tester():
    def __init__(self, python_path, input_path, executable):
        self.python_path = python_path
        self.input_path = input_path
        self.executable = executable
    
    @staticmethod
    def check_file(file) -> bool:
        file = pathlib.Path(file).resolve()

        return os.path.isfile(file)

    def gets_stdout(self, input_text) -> str:
        """
        Pythonファイルを実行して、標準入力をして、
        その標準出力を返しくれる
        """
        try:
            stdout = subprocess.check_output(
                [self.executable, self.python_path],
                input=input_text.encode('utf-8'),
                stderr = subprocess.PIPE
            )

            return stdout.splitlines()
        except subprocess.CalledProcessError as error:
            print("実行ファイルにエラーがあります")
            for i in error.stderr.splitlines():
                print(i.decode('utf-8'))
            sys.exit()
    
class ReadFiles():
    @staticmethod
    def read(file_path) -> str:
        file = open(file_path, 'r')

        data = file.read()

        file.close()
        return data

    def analysis(data):
        testcases = None
        test_inputs = []
        answers = []

        inputs = False

        data = data.splitlines()
        count = 0
        for i in data:
            if i == "END":
                yield [
                    testcases,
                    test_inputs,
                    answers
                ]

                testcases = None
                test_inputs = []
                answers = []

                inputs = None
                continue
            
            if re.match('-(.*)-', i):
                inputs = True
                testcases = "".join(re.findall('-(.*)-', i))

            if inputs:
                if re.match('_(.*)_', i) and testcases == "".join(re.findall('_(.*)_', i)):
                    inputs = False
                elif inputs and not i == "-" + testcases + "-":
                    test_inputs.append(i)
            elif not inputs and not inputs is None:
                answers.append(i)
