try:
    args = parser.parse_args()

    if args.version:
        print("ediclean", ediclean.__version__)

    elif not args.filename[0]:
        parser.print_usage()
    else:
        print (paxlst.cleanfile(args.filename[0]))


except SystemExit as err: 
    if err.code == 2: parser.print_help()
