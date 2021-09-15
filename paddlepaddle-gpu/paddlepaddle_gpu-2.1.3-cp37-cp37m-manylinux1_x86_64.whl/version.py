# THIS FILE IS GENERATED FROM PADDLEPADDLE SETUP.PY
#
full_version    = '2.1.3'
major           = '2'
minor           = '1'
patch           = '3'
rc              = '0'
istaged         = True
commit          = '06d47ff7e2dff1d2daa96eaff525d81ef7c013eb'
with_mkl        = 'ON'

def show():
    if istaged:
        print('full_version:', full_version)
        print('major:', major)
        print('minor:', minor)
        print('patch:', patch)
        print('rc:', rc)
    else:
        print('commit:', commit)

def mkl():
    return with_mkl
