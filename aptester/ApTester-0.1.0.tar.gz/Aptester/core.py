from fabric.colors import red, green
import sys
import argparse
from time import sleep
from rich.console import Console


from . import controll as Ctl

def main():
    last_answer = []
    last_test = []

    answer_app = last_answer.append
    test_app = last_test.append


    description = """
Hello. I'm Aptester.
Auto Tester for Competitive programming.

©Copyright 2021 Hirose Heitor
""".strip()

    parser = argparse.ArgumentParser(
        description = description,
        formatter_class = argparse.RawTextHelpFormatter
    )
    # re.findall('a(.*)b', 'axyzb')

    parser.add_argument("path_input", help="Path to the Test case File.")
    parser.add_argument("path_python", help="Path to the python file.")
    args = parser.parse_args()

    PythonFile = Ctl.Tester(
        python_path = args.path_python,
        input_path = args.path_input,
        executable = sys.executable
    )
    console = Console()

    if not PythonFile.check_file(args.path_python):
        raise FileNotFoundError(red("Can't find python file."))
    if not PythonFile.check_file(args.path_input):
        raise FileNotFoundError(red("Can't find input file."))

    input_file = Ctl.ReadFiles.read(args.path_input)
    cases = Ctl.ReadFiles.analysis(input_file)
    for i in cases:
        answers = []
        spell = "\n".join(i[1])
        input_text = spell
        test = None


        with console.status(f"[bold green]Testing {i[0]}...") as status:
            while test is None:
                sleep(1)
                test = PythonFile.gets_stdout(input_text)
        app = answers.append
        for l in test:
            app(l.decode('utf-8'))
        
        test = "\n".join(answers)
        answer = "\n".join(i[2])
        if test == answer:
            print(green(f"The {i[0]} was pased."))
        else:
            print(red("The answer is incorrect."))
            print(red("Test answer :"))
            print(red(test))
            print(red("Your answer :"))
            print(red(answer))


if __name__ == "__main__":
    main()
