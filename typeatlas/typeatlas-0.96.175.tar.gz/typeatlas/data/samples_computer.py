
add_sample = lambda *a, **kw: None

PC_LOAD_SOURCE = 'PC LOAD LETTER - Wikipedia, 00:22, 31 March 2018 <https://en.wikipedia.org/w/index.php?title=PC_LOAD_LETTER&oldid=833343787>'

add_sample('PC LOAD LETTER',
           language='en', device='LCD', region='US',
           vendor='HP', product='LaserJet 4',
           sources=[PC_LOAD_SOURCE])

add_sample('PC LOAD LEGAL',
           language='en', device='LCD', region='US',
           vendor='HP', product='LaserJet 4',
           sources=[PC_LOAD_SOURCE])

add_sample('PC LOAD A4',
           language='en', device='LCD', region='Europe',
           vendor='HP', product='LaserJet 4',
           sources=[PC_LOAD_SOURCE])


add_sample('Abort, Retry, Fail?',
           alternatives=['Abort, Retry, Ignore, Fail?'],
           context='''
C:\>dir b:

Not ready reading drive A
{text}{cursor}
''',
           language='en', device='textmode',
           vendor='Microsoft', product='MS-DOS',
           sources=['Abort, Retry, Fail? - Wikipedia, 02:28, 20 April 2018 <https://en.wikipedia.org/w/index.php?title=Abort,_Retry,_Fail%3F&oldid=837319661>'])


add_sample('Not a typewriter',
           context="550 {username}: User unknown: {text}",
           product="*nix",
           device="terminal",
           sources=['Not a typewriter - Wikipedia, 08:56, 29 May 2016 <https://en.wikipedia.org/w/index.php?title=Not_a_typewriter&oldid=722633543>'])

add_sample('lp0 on fire',
           context="{logdate} {hostname}: {text}",
           vendor="*nix", 
           device="terminal",
           sources=['lp0 on fire - Wikipedia, 02:41, 7 May 2018 <https://en.wikipedia.org/w/index.php?title=Lp0_on_fire&oldid=840000387>'])


add_sample("Bad command or file name",
           context='''
C:\TYPEATLS>TYPEATLS /TTF C:\FONTS\TIMR.TTF
{text}
''',
           language='en', device='textmode',
           vendor='Microsoft', product='MS-DOS',
           sources=['Bad command or file name - Wikipedia, 18:58, 3 December 2017 <https://en.wikipedia.org/w/index.php?title=Bad_command_or_file_name&oldid=813440129>'])


add_sample('values of β will give rise to dom!',
           vendor="Bell Labs", product='Unix', subject="mv",
           device="terminal", 
           sources=['Odd Comments and Strange Doings in Unix <https://www.bell-labs.com/usr/dmr/www/odd.html>'])

