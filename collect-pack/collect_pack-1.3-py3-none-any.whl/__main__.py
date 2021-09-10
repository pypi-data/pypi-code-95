from .pack.collect_framework import format_return, work_with_args, cli

if __name__ == '__main__':
    print(format_return(work_with_args(cli().file, cli().string)))
