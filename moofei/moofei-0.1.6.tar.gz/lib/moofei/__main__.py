import os, sys, argparse, json
print('usage:')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#for method in ('find', 'valid'):
#    print(' '*4+' '.join([sys.executable, '-m', 'moofei.'+method, '-h']))

def set_config(cmd=None):
    parser = argparse.ArgumentParser(description="""Set Moofei-Config""")
    if cmd:
       parser.add_argument('cmd',  help="Command line mode; generally can be ignored") 
    parser.add_argument('-set-user','--set-user', help='set auth user')
    parser.add_argument('-set-pwd','--set-pwd', help='set auth password')
    parser.add_argument('--pprint', action='store_true', help='print  moofei-config')
    parser.add_argument('--clear-all', action='store_true', help='delete moofei-config')
    
    args = parser.parse_args()
    if '-h' in sys.argv :
        print(args)
    else:
        cfgpath = os.path.join(BASE_DIR, '.conf')
        if os.path.isfile(cfgpath):
            config = json.load(open(cfgpath))
        else:
            config = {}
        if args.pprint:
            print(json.dumps(config, sort_keys=True, indent=4, separators=(', ', ': ')))
            exit(0)
        elif args.clear_all:
            os.remove(cfgpath)
            print('Remove succeed:', cfgpath)
            exit(0)
        if args.set_user and args.set_pwd:
            config.setdefault('users', {})[args.set_user] = args.set_pwd
            print('Save User:', args.set_user)
        with open(cfgpath, 'w') as fp:
            fp.write(json.dumps(config))
            
if len(sys.argv)==1:
        print('1. Full-Text-Search Webbrowser')
        N = str(input('Please Input Number: ')).strip()
        if N=='1':
            cmd = sys.executable+' -m moofei.find 0.0.0.0:5000 --webbrowser'
            os.system(cmd)
            
elif len(sys.argv)==2:
    if sys.argv[1] in (":help", '-h', '--help', 'help'):
        print('python -m :(find|config|cat|V)')
    elif sys.argv[1] in (":V",':v','-V'):
        from .__version__ import __version__
        print(__version__)
           
elif len(sys.argv)>2:
    if sys.argv[1] in (":find",'find'):
        from ._find import main
    elif sys.argv[1] in (":config", ':conf', ':cfg', 'config'):
        main = set_config
    elif sys.argv[1] in (":cat", 'cat'):
        from ._cat import main
    
    main(sys.argv[1])
    
exit(0)
