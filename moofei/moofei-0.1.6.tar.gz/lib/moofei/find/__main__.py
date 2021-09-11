import os, sys, json
if '--webbrowser' in sys.argv:
    #£ºpython -m moofei.find 127.0.0.1:5000 --webbrowser
    #£ºpython find 127.0.0.1:5000 --webbrowser
    sys.argv.remove('--webbrowser')
    try:
        from ..view import app
    except ImportError:
        from moofei.view import app
    
    import argparse
    parser = argparse.ArgumentParser() 
    parser.add_argument('p', default=":", nargs='?', )
    args = parser.parse_args()
    d = {} 
    if args.p:
        if ':' in args.p:
            h, p = args.p.split(':')
            if h: d['host'] = h
            if p and p.isdigit(): d['port'] = int(p)
        else:
            p = args.p
            if p and p.isdigit(): d['port'] = int(p)
            else: d['host'] = p
    try:            
        import webbrowser
        if d.get('host','')=='0.0.0.0':
            webbrowser.open("http://%s:%s"%('127.0.0.1', d.get('port', 5000)))
        else:    
            webbrowser.open("http://%s:%s"%(d.get('host','127.0.0.1'), d.get('port', 5000)))
    except:
        pass
    app.run(**d)
    
else:
    #£ºpython -m moofei.find
    #£ºpython find
    try:
        from .._find import main
    except ImportError:
        from moofei._find import main
    main()
    
exit(0)
