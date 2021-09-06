import re

class c:
    def __setattr__( self, k, v ):
        self.__dict__[ k ] = v if isinstance( v, re.Pattern ) else re.compile( v )

c = c()

comment = r'(?:#( \<.*\>)?(.*))'
c.comment = re.compile( comment + '$', re.MULTILINE )

c.space = space = r'\s+'

c.filepos = re.compile( r'(?P<start>^\*?---\s*)?(?P<rel>\+?)(?P<pos>[a-f0-9]*)(?P<end>:)', re.MULTILINE )

c.hex = r'(=?[a-f0-9.]+)'

name = r'[\w.\-{}!?]+'

var = r'\{\s*' + name + r'\s*\}'
_vars = r'\{\s*' + name + r'\s*(?:,\s*' + name + r')*\s*\}'
values = r'(?:[0-9\.]+|' + var + r')'

c.endian = r'@[<>@]'

c.dtypes = dtypes = r'(?:\-?[OBIHLEFD])'
c.types = r'(' + dtypes + r'+)(' + _vars + r')?(?:\[([^\]]+)\])?'

string_inner = r'(?:\\"|[^"])*'
string = r'(?P<start>")(' + string_inner + r')(?P<end>")?'
c.string = r'(?P<type>[SU](?:|0))(?P<name>' + var + r')?(?:\*(?P<size>' + values + r'))?(?:' + string + r')?'

c.macrodef = re.compile( r'(?P<start><=(?P<name>' + name + r')>)((?:[^<]|<(?!\/(?P=name)>))*)(?P<end><\/(?P=name)>)?', re.DOTALL )
c.macrouse = re.compile( r'<(?P<name>' + name + r')\s*(?P<ns>' + name + r')?(?:(?P<start>>)((?:[^<]|<(?!\/(?P=name)>))*)(?P<end><\/(?P=name)>)?|\s*?(?P<short_end>\/>))', re.DOTALL )
c.macroimport = re.compile( r'<\+(?P<filename>' + name + r'|"' + string_inner + r'")\s*(?P<ns>' + name + r')?(?:(?P<start>>)((?:[^<]|<(?!\/\+>))*)(?P<end><\/\+>)?|\s*?(?P<short_end>\/>))', re.DOTALL )

repeat = r'(?:(\s*)\*\s*(?P<repeat>' + values + r'))'
c.repeat = repeat + r'+'

if __name__ == '__main__': # pragma: no cover
    for k, v in dict( vars() ).items():
        print( k, ':', sep = '' )
        if k == 'c':
            for ck, cv in vars( c ).items():
                print( '\t', ck, ':', sep = '' )
                print( '\t', cv.pattern )
            continue
        print( v )
