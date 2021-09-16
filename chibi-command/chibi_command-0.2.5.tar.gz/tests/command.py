import copy
from unittest import TestCase

from chibi_command import Command


class Test_echo( TestCase ):

    def test_can_build_a_new_command( self ):
        result = Command()
        self.assertEqual( "", result.preview(), )
        result = Command( "echo", "hello my world!" )
        self.assertEqual( "echo hello my world!", result.preview(), )
        result = Command()
        self.assertEqual( "", result.preview(), )

    def test_eq( self ):
        command_1 = Command( "echo" )
        command_2 = Command( "cowsay" )
        command_3 = Command( "echo" )
        self.assertNotEqual( command_1, command_2 )
        self.assertEqual( command_1, command_3 )

    def test_can_copy_the_command( self ):
        command = Command()
        new_command = copy.copy( command )
        self.assertEqual( command, new_command )

        command = Command( "echo" )
        new_command = copy.copy( command )
        self.assertEqual( command, new_command )

    def test_add_new_args( self ):
        command = Command( 'echo' )
        command.add_args( 'hello' )
        self.assertEqual( 'echo hello', command.preview() )

        command = Command( 'echo' )
        command.add_args( hello='hello' )
        self.assertEqual( 'echo hello hello', command.preview() )
