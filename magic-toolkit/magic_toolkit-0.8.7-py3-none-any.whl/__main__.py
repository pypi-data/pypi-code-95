import argparse
import magic
from magic.tensorrt import Onnx2trtConverter

def main():
    p = argparse.ArgumentParser(usage="magic command ..., magic -h for more details",)
    p.add_argument("-V", "--version",
                   action='version',
                   version='magic %s' % magic.__version__,
                   help="show version and exit")
    sub_parsers = p.add_subparsers(
        metavar='command',
        dest='cmd',
    )
    sub_parsers.required = True
    """ add converters"""
    onnx2trt_converter = Onnx2trtConverter(sub_parsers)
    args = p.parse_args()

    if args.cmd == "onnx2trt":
        onnx2trt_converter.execute(args)

if __name__ == '__main__':
    main()
