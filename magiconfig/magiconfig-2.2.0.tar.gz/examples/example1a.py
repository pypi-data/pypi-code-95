from magiconfig import ArgumentParser, MagiConfigOptions
import six

if __name__=="__main__":
    parser = ArgumentParser(config_options=MagiConfigOptions())
    parser.set_config_options(args = ["poscon"])
#    parser = ArgumentParser(config_options=MagiConfigOptions(args=["poscon"]))
#    parser = ArgumentParser()
#    parser.add_argument("poscon", type=str, default="poscon", help="con arg")
    parser.add_argument("-f","--foo", dest="foo", type=str, default="lorem", help="foo arg")
    parser.add_argument("-b","--bar", dest="bar", type=float, required=True, help="bar arg")
    parser.add_argument("-i","--ipsum", dest="ipsum", action="store_true", help="ipsum arg")
    args = parser.parse_args()
    six.print_(args)
    parser.write_config(args,"examples/config1_out.py")
