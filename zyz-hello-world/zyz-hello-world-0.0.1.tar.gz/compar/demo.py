import argparse
import sentence_parser
import udp

if __name__ == '__main__':
    parser_ = argparse.ArgumentParser()
    parser_.add_argument('--udp_server_ip', type=str, required=False, default='127.0.0.1', help='udp服务端的ip地址')
    parser_.add_argument('--udp_server_port', type=int, required=False, default='60002', help='udp服务端的端口号')
    args = parser_.parse_args()
    print(args)


    x = udp.udp_hex(args.udp_server_ip, args.udp_server_port)
    par = sentence_parser.up_parser()

    while True:
        sentence = x.listenonce()
        par.parse(par)


