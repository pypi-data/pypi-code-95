import hexer
import io
import pathlib
import re
import tempfile
import unittest

from hexer import regs, main

class test_handlers( unittest.TestCase ):
    def setUp( self ):
        # test file content
        tf = b'\0\0\0\1\0\x0a\0\x0bABCD"FGH\0\2\0\3\0\0\0\0'
        self.data_file = io.BytesIO()
        self.data_file.write( tf )
        self.data_file.seek( 0 )

        self.hx_file = io.StringIO()
        self.out_file = io.StringIO()

        self.hx = hexer.hexer( self.data_file, self.hx_file, self.out_file )

    def assertInOut( self, handler, reg, input, output, *a, **kw ):
        self.assertEqual( list( handler( reg.match( input ), self.hx, *a, **kw ) ), output )

    def test_filepos_token( self ):
        self.assertInOut( hexer.filepos_token, regs.c.filepos, ':', [ '00:' ] )

    def test_filepos_token_bad_pos( self ):
        with self.assertRaises( hexer.FilePosMissmatch ) as cx:
            self.assertInOut( hexer.filepos_token, regs.c.filepos, '100:', [] )
        self.assertEqual( str( cx.exception ), 'file position missmatch 0x0 vs 0x100' )

    def test_filepos_token_skip( self ):
        self.assertInOut( hexer.filepos_token, regs.c.filepos, '--- 4:', [ '--- 04:' ] )
        self.assertEqual( self.hx.data_file.tell(), 4 )

    def test_filepos_token_skip_output( self ):
        with self.assertRaises( NotImplementedError ):
            self.assertInOut( hexer.filepos_token, regs.c.filepos, '*--- 4:', [] )

    def test_filepos_token_rel( self ):
        self.data_file.seek( 4 )
        self.assertInOut( hexer.filepos_token, regs.c.filepos, '+4:', [ '08:' ] )
        self.assertEqual( self.hx.data_file.tell(), 8 )

    def test_comment_token( self ):
        self.assertInOut( hexer.comment_token, regs.c.comment, '# abc', [ '# abc' ] )

    def test_hex_token( self ):
        self.assertInOut( hexer.hex_token, regs.c.hex, '.', [ '00' ] )

    def test_hex_token_assert( self ):
        self.assertInOut( hexer.hex_token, regs.c.hex, '=00000001', [ '=', '00000001' ] )

    def test_hex_token_assert_bad( self ):
        with self.assertRaises( hexer.HexDataAssertError ) as cx:
            self.assertInOut( hexer.hex_token, regs.c.hex, '=00000002', [] )

        self.assertEqual( str( cx.exception ), '00000002 != 00000001' )

    def test_endian_token( self ):
        self.assertInOut( hexer.endian_token, regs.c.endian, '@>', [ '@>' ] )
        self.assertEqual( self.hx.endianess, '>' )

    def test_types_token( self ):
        self.test_endian_token()
        self.assertInOut( hexer.types_token, regs.c.types, 'L', [ 'L[1]' ] )
        self.data_file.seek(0)
        self.assertInOut( hexer.types_token, regs.c.types, 'L{a}', [ 'L{a}[1]' ] )
        self.assertEqual( self.hx._vars['a'], 1 )

    def test_types_token_mult( self ):
        self.test_endian_token()
        self.assertInOut( hexer.types_token, regs.c.types, 'LHH', [ 'LHH[1,10,11]' ] )

    def test_string_token( self ):
        self.data_file.seek( 8 )
        self.assertInOut( hexer.string_token, regs.c.string, 'S*8', [ r'S*8"ABCD\"FGH"' ] )
        self.data_file.seek( 8 )
        self.assertInOut( hexer.string_token, regs.c.string, 'S{name}*8', [ r'S{name}*8"ABCD\"FGH"' ] )
        self.assertEqual( self.hx._vars['name'], b'ABCD"FGH' )

    def test_macro_def_token( self ):
        self.assertInOut( hexer.macro_def_token, regs.c.macrodef, '<=abc>.</abc>', [ '<=abc>.</abc>' ] )
        self.assertEqual( self.hx.macros['abc'], '.' )

    def test_macro_use_token( self ):
        self.test_macro_def_token()
        self.assertInOut( hexer.macro_use_token, regs.c.macrouse, '<abc />', [ '<abc>','00','</abc>' ] )
        self.assertInOut( hexer.macro_use_token, regs.c.macrouse, '<abc ns/>', [ '<abc ns>','00','</abc>' ] )

    def test_macro_not_found( self ):
        with self.assertRaises( hexer.MacroNotFound ) as cx:
            self.assertInOut( hexer.macro_use_token, regs.c.macrouse, '<abc />', [] )

        self.assertEqual( str( cx.exception ), 'abc' )

    def test_macro_import_token( self ):
        with tempfile.NamedTemporaryFile( 'w' ) as tmp:
            tmp.write( '.' )
            tmp.flush()

            self.assertInOut( hexer.macro_import_token, regs.c.macroimport, '<+"' + tmp.name + '"/>', [ '<+"' + tmp.name + '"/>' ] )
            self.assertInOut( hexer.macro_import_token, regs.c.macroimport, '<+"' + tmp.name + '"></+>', [ '<+"' + tmp.name + '">', '00' ,'</+>' ] )

    def test_repeat_token( self ):
        self.test_endian_token()

        token = ( hexer.types_token, regs.c.types.match( 'B' ) )

        self.data_file.seek( 0 )
        self.assertInOut( hexer.repeat_token, regs.c.repeat, '*1', [ 'B[0]' ], token = token )

        self.data_file.seek( 0 )
        self.assertInOut( hexer.repeat_token, regs.c.repeat, '*2', [ 'B[0]', 'B[0]' ], token = token )

        self.data_file.seek( 0 )
        self.assertInOut( hexer.repeat_token, regs.c.repeat, '*3', [ 'B[0]', 'B[0]', 'B[0]' ], token = token )

        self.data_file.seek( 0 )
        self.assertInOut( hexer.repeat_token, regs.c.repeat, ' * 2', [ 'B[0]', ' ', 'B[0]', ' ' ], token = token )

        self.data_file.seek( 0 )
        self.assertInOut( hexer.repeat_token, regs.c.repeat, '*2*3', [ 'B[0]', 'B[0]', 'B[0]', 'B[1]', 'B[0]', 'B[10]' ], token = token )

        self.data_file.seek( 0 )
        self.assertInOut( hexer.repeat_token, regs.c.repeat, ' *2 *3 *4', [
            'B[0]', ' ', 'B[0]', ' ', ' ',
            'B[0]', ' ', 'B[1]', ' ', ' ',
            'B[0]', ' ', 'B[10]', ' ', ' ', ' ',
            'B[0]', ' ', 'B[11]', ' ', ' ',
            'B[65]', ' ', 'B[66]', ' ', ' ',
            'B[67]', ' ', 'B[68]', ' ', ' ', ' ',
            'B[34]', ' ', 'B[70]', ' ', ' ',
            'B[71]', ' ', 'B[72]', ' ', ' ',
            'B[0]', ' ', 'B[2]', ' ', ' ', ' ',
            'B[0]', ' ', 'B[3]', ' ', ' ',
            'B[0]', ' ', 'B[0]', ' ', ' ',
            'B[0]', ' ', 'B[0]', ' ', ' ', ' ' ], token = token )

class test_regs( unittest.TestCase ):
    def test_comment( self ):
        m = regs.c.comment.match( '# abc' )
        self.assertIsInstance( m, re.Match )

    def test_space( self ):
        m = regs.c.space.match( '  ' )
        self.assertIsInstance( m, re.Match )

    def test_filepos( self ):
        m = regs.c.filepos.match( '1234:' )
        self.assertIsInstance( m, re.Match )

    def test_hex( self ):
        m = regs.c.hex.match( 'abc123' )
        self.assertIsInstance( m, re.Match )

    def test_endian( self ):
        m = regs.c.endian.match( '@>' )
        self.assertIsInstance( m, re.Match )

    def test_dtypes( self ):
        m = regs.c.dtypes.match( 'LLHB' )
        self.assertIsInstance( m, re.Match )

    def test_types( self ):
        m = regs.c.types.match( 'LLHB[1,2,3,4]' )
        self.assertIsInstance( m, re.Match )

    def test_string( self ):
        m = regs.c.string.match( 'S*4"...."' )
        self.assertIsInstance( m, re.Match )

    def test_macrodef( self ):
        m = regs.c.macrodef.match( '<=abc>LLHB</abc>' )
        self.assertIsInstance( m, re.Match )

    def test_macrouse( self ):
        m = regs.c.macrouse.match( '<abc />' )
        self.assertIsInstance( m, re.Match )

    def test_macroimport( self ):
        matches = [
            '<+filename/>',
            '<+filename></+>',
            '<+filename ns></+>',
            '<+"filename with space" ns/>',
        ]

        for match in matches:
            m = regs.c.macroimport.match( match )
            self.assertIsInstance( m, re.Match, msg = 'did not match "%s"' % match )

    def test_repeat( self ):
        m = regs.c.repeat.match( '*3' )
        self.assertIsInstance( m, re.Match )

class test_hexer( unittest.TestCase ):
    def setUp( self ):
        # test file content
        tf = b'\0\0\0\1\0\x0a\0\x0bABCD"FGH\0\2\0\3'
        self.data_file = io.BytesIO()
        self.data_file.write( tf )
        self.data_file.seek( 0 )

        self.hx_file = io.StringIO()
        self.out_file = io.StringIO()

        self.hx = hexer.hexer( self.data_file, self.hx_file, self.out_file )

    def hx_write( self, hx ):
        self.hx_file.write( hx )
        self.hx_file.seek( 0 )

    def assertOut( self, out ):
        self.out_file.seek( 0 )
        self.assertEqual( self.out_file.read(), out )

    # __init__
    # run

    def test_run_to_end( self ):
        self.hx_file.write( '@>LHHS*8HH' )
        self.hx_file.seek( 0 )
        self.hx.run()
        self.out_file.seek( 0 )
        self.assertEqual( self.out_file.read(), '@>LHH[1,10,11]S*8"ABCD\\"FGH"HH[2,3]' )

    # get_tokens

    def test_multiline_str( self ):
        self.hx_write( ': S*4"A\nB\n"\n' )
        self.hx.run()
        self.assertOut( '00: S*4"\\x00\\x00\\x00\\x01"\n04: 000a 000b 4142 4344 # <....ABCD>\n0c: 2246 4748 0002 0003 # <"FGH....>\n' )

    def test_repeat( self ):
        self.hx_write( '@> H*10' )
        self.hx.debug = True
        self.hx.run()
        self.assertOut( '@> H[0]H[1]H[10]H[11]H[16706]H[17220]H[8774]H[18248]H[2]H[3]' )

    def test_bad_token( self ):
        self.hx_write( '~~~' )
        with self.assertRaises( Exception ) as cx:
            self.hx.run()
        self.assertEqual( str( cx.exception ), 'could not match: ~~~' )

    def test_str_no_end( self ):
        self.hx_write( 'S*8"\n' )
        with self.assertRaises( hexer.NoEndPastEOF ) as cx:
            self.hx.run()
        self.assertEqual( str( cx.exception ), "no end past eof: 'S*8\"\\n'" )

    @unittest.skip( "to be fixed in v0.1.0" )
    def test_repeat_next_line( self ):
        self.hx_write( ': ....\n*2\n' )
        self.hx.run()
        self.assertOut( '00: 0000\n0001\n04: 000a 000b 4142 4344 # <....ABCD>\n0c: 2246 4748 0002 0003 # <"FGH....>\n' )

    def test_interpolate_str( self ):
        self.hx._vars['test'] = '123'
        self.assertEqual( self.hx.interpolate_str( r'something{test}' ), 'something123' )

    def test_interpolate_name( self ):
        self.hx._vars['test'] = '123'
        self.hx._vars['ns.test'] = '321'
        self.assertEqual( self.hx.interpolate_name( r'name_{test}' ), 'name_123' )
        self.hx.namespace = [ 'ns' ]
        self.assertEqual( self.hx.interpolate_name( r'name_{test}', True ), 'ns.name_321' )

    def test_parse_str( self ):
        self.assertEqual( self.hx.parse_str( r'"something"' ), 'something' )
        self.assertEqual( self.hx.parse_str( r'"escaped\""' ), 'escaped\\"' )

    def test_get_vars( self ):
        self.assertEqual( self.hx.get_vars( r'{a}' ), [ 'a' ] )
        self.assertEqual( self.hx.get_vars( r'{a,b,c}' ), [ 'a', 'b', 'c' ] )
        self.hx.namespace = [ 'ns' ]
        self.hx._vars['ns.i'] = 0
        self.assertEqual( self.hx.get_vars( r'{a_{i}}' ), [ 'ns.a_0' ] )

    def test_get_var( self ):
        self.hx._vars['a'] = 'something'
        self.hx._vars['a_something'] = 'else'
        self.assertEqual( self.hx.get_var( r'a' ), 'something' )
        self.assertEqual( self.hx.get_var( r'a_{a}' ), 'else' )

    def test_set_var( self ):
        self.hx.set_var( r'a', 'something' )
        self.assertEqual( self.hx._vars['a'], 'something' )

    def test_get_val( self ):
        self.hx._vars['a'] = 'something'
        self.assertEqual( self.hx.get_val( r'{a}' ), 'something' )
        self.hx._vars['a'] = 10
        self.assertEqual( self.hx.get_val( r'{a}' ), 10 )

class test_main( unittest.TestCase ):
    def setUp( self ):
        # test file content
        tf = b'\0\0\0\1\0\x0a\0\x0bABCD"FGH\0\2\0\3'

        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = pathlib.Path( self.temp_dir.name, 'data_file' )
        self.hx_file = pathlib.Path( self.temp_dir.name, 'data_file.hx' )

        self.data_file.write_bytes( tf )

    def tearDown( self ):
        self.temp_dir.cleanup()

    def test_no_args( self ):
        with self.assertRaises( SystemExit ) as cm:
            main( [] )

        self.assertEqual( cm.exception.code, 2 )

    def test_no_hx( self ):
        main( [ str( self.data_file ) ] )

        self.assertTrue( self.hx_file.exists() )
        self.assertEqual( self.hx_file.read_text(), '00: 0000 0001 000a 000b # <........>\n08: 4142 4344 2246 4748 # <ABCD"FGH>\n10: 0002 0003 ' )

    def test_hx( self ):
        self.hx_file.write_text( '00: @>LHH\n' )

        main( [ str( self.data_file ) ] )

        self.assertTrue( self.hx_file.exists() )
        self.assertEqual( self.hx_file.read_text(), '00: @>LHH[1,10,11]\n08: 4142 4344 2246 4748 # <ABCD"FGH>\n10: 0002 0003 ' )

    def test_json( self ):
        self.hx_file.write_text( '00: @>S{a}*8\n' )

        main( [ str( self.data_file ), '-j' ] )

        self.assertTrue( self.hx_file.exists() )
        self.assertEqual( self.hx_file.read_text(), '00: @>S{a}*8"\\x00\\x00\\x00\\x01\\x00\\n\\x00\\x0b"\n08: 4142 4344 2246 4748 # <ABCD"FGH>\n10: 0002 0003 ' )

    def test_debug( self ):
        self.hx_file.write_text( '00: @> H*10\n' )

        main( [ str( self.data_file ), '-d' ] )

        self.assertTrue( self.hx_file.exists() )
        self.assertEqual( self.hx_file.read_text(), '00: @> H[0]H[1]H[10]H[11]H[16706]H[17220]H[8774]H[18248]H[2]H[3]\n' )

    def test_default( self ):
        main( [ str( self.data_file ), '-m', ': . . . .' ] )

        self.assertTrue( self.hx_file.exists() )
        self.assertEqual( self.hx_file.read_text(), '00: 00 00 00 01\n04: 00 0a 00 0b\n08: 41 42 43 44\n0c: 22 46 47 48\n10: 00 02 00 03\n' )
        
if __name__ == '__main__': # pragma: no cover
    unittest.main()
