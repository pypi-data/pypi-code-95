import dotignore

di = dotignore.dotignore( ".testignore" )
files = di.get_files( ".", recurse=True )
for f in files:
    print(f'Found file: {f}')
