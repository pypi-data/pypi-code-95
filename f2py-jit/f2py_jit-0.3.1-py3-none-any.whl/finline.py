"""
Inline fortran 90 code
"""

import re

# TODO: fix implicit none in functions and routines


def _inline_locals_declaration_block(name, db):
    """
    This dumps a safe variable declaration block with local variables
    of inlineable subroutine `name` from the subroutine database `db`
    """
    variables, local_variables, body = db[name]
    #print('! inline local vars for:', name)
    #print('! inline local vars:', local_variables)
    out = []
    for var in local_variables:
        decl = var.split('::')[0]
        old_words = var.split('::')[1]
        underscored_words = []
        for word in old_words.split(','):
            underscored_words.append('{}__{}'.format(name, word.strip()))
        #print(decl, '::', ','.join(underscored_words))
        out.append('{} :: {} '.format(decl, ','.join(underscored_words)))
    return '\n'.join(out)

def _inline_body(name, db, dummy_variables):
    # This copy is necessary to avoid modifying the body in the database
    import copy
    
    variables, local_variables, old_body = db[name]
    body = copy.deepcopy(old_body)
    comment = """
! inline: {}
! local: {} 
! dummy: {}
! vars: {}
""".format(name, local_variables, dummy_variables, variables)

    # Safely replace dummies with subroutine variables
    for dummy_var, var in zip(dummy_variables, variables):
        for i, line in enumerate(body):
            safe_line = line.split()
            for j, word in enumerate(safe_line):
                # We skip everything once an inline comment starts
                if '!' in word:
                    break
                # Also check if variable is an argument of a call
                # in which case the we have to dig further
                pattern = r'(\b){}(\b)'.format(var)
                repl = r'\1{}\2'.format(dummy_var)
                try:
                    new_word = re.sub(pattern, repl, word)
                except:
                    raise
                safe_line[j] = new_word

            body[i] = ' '.join(safe_line) + '\n'

    # Replace local variables with safe names (prefixed)
    # TODO: refactor normalization of variables from line
    for local_var in local_variables:        
        old_words = local_var.split('::')[1]
        for word in old_words.split(','):
            var = word.strip()
            safe_var = '{}__{}'.format(name, word.strip())

            # TODO: refactor
            for i, line in enumerate(body):
                # Add spaces around math symbols
                new_line = copy.deepcopy(line)
                for symbol in '+-*/':
                    new_line = new_line.replace(symbol, ' ' + symbol + ' ')
                new_line = new_line.replace(',', ', ')
                new_line = new_line.replace('(', '( ')
                new_line = new_line.replace(')', ' )')
                # But fix exponentiation
                new_line = new_line.replace('* *', '**')
                new_line = new_line.replace('*  *', '**')                
                safe_line = new_line.split()

                for j, word in enumerate(safe_line):
                    # Also check if variable is an argument of a call
                    # in which case the we have to dig further
                    pattern = r'([(,\s]){}([),\s])'.format(var)
                    repl = r'\1{}\2'.format(safe_var)
                    safe_line[j] = re.sub(pattern, repl, word)
                    if word == var:
                        safe_line[j] = safe_var

                body[i] = ' '.join(safe_line) + '\n'

    return comment + ''.join(body).strip('\n')


# def report(subroutines):
#     for name in subroutines:
#         variables, local_variables, body = subroutines[name]
#         txt = '# name:', name
#         txt += '# vars:', variables
#         txt += '# local:', local_variables
#         txt += ''.join(body)
#     return txt

def inline(f, db):
    from collections import defaultdict
    in_subroutine = False
    variable_declaration = False
    candidates = {}
    locals_inline = defaultdict(list)
    out = []
    with open(f) as fh:
        # Jump at the end of the file, get the line index and come back
        fh.seek(0, 2)
        end = fh.tell()
        fh.seek(0)

        while True:
            # Break if we are the EOF
            idx = fh.tell()
            if idx == end:
                break

            line = fh.readline()

            # Check if we are in a block of variable declarations
            if '::' in line:
                variable_declaration = True
                continue

            # Find line where variable declarations ends and keep its idx
            # This is where we can add local variables of inlined subroutines
            if variable_declaration and not '::' in line:
                idx_variable_decl = idx
                variable_declaration = False

            # Look for subroutine calls and store corresponding line idx
            if 'call ' in line and not line.lstrip().startswith('!'):
                line = line.split('!')[0]
                keys = line.split()
                i = keys.index('call')
                name = keys[i + 1].split('(')[0]
                signature = keys[i + 1].split('(')[1]
                # Extract the signature paying attention to array sections in signature
                signature = '('.join(line.split('(')[1:])
                signature = signature.strip()
                signature = signature.strip(')')

                variables = [_.strip() for _ in signature.split(',')]
                
                # Merge array sections that have been split by command above
                merged_variables = []
                section = False
                for var in variables:
                    if '(' in var:
                        section = True
                        var_merge = ''
                    if not section:
                        merged_variables.append(var)
                    else:
                        var_merge += var + ','
                    if ')' in var:
                        section = False
                        merged_variables.append(var_merge.strip(','))

                candidates[idx] = [name, merged_variables]
                locals_inline[idx_variable_decl].append(name)

        # Inline subroutines
        fh.seek(0)
        while True:
            idx = fh.tell()
            if idx == end:
                break

            if idx in locals_inline:
                for name in locals_inline[idx]:
                    # Make sure subroutine is in the db of inlineable subroutines
                    # Add a variable declaration block with safe local variables
                    if name in db:
                        out.append(_inline_locals_declaration_block(name, db))

            line = fh.readline()

            if idx in candidates:
                name = candidates[idx][0]
                # Extract and normalize variables passed to subroutine
                variables = candidates[idx][1]
                # Make sure subroutine is in the db of inlineable subroutines
                if name in db:
                    out.append(_inline_body(name, db, variables))
                else:
                    out.append(line.strip('\n'))
            else:
                out.append(line.strip('\n'))
    return '\n'.join(out)


def extract(f, ignore=None):
    """
    Extract all inlineable subroutines variables and bodies from file

    It currently ignores subroutines with interface blocks.

    Return a dictionary.
    """
    in_subroutine = False
    in_interface = False
    db = {}
    with open(f) as fh:
        for line in fh:
            # Skip comments
            if line.lstrip().startswith('!'):
                continue

            # Downcase everything
            line = line.lower()
            
            # We are done
            if 'end subroutine' in line and not in_interface:
                in_subroutine = False
                if ignore is None or name not in ignore:
                    # print( '! add' , name)
                    if name in db:
                        # print('! ALREADY FOUND', name)
                        pass
                    db[name] = [variables, local_variables, body]
                continue

            # Parse subroutine
            if 'subroutine' in line and not in_interface:
                in_subroutine = True
                keys = line.split()
                idx = keys.index('subroutine')
                signature_keys = keys[idx + 1:]
                signature = ''.join(signature_keys)

                # Extract subroutine name and variables from signature
                name, keys = signature.split('(')
                body = []
                variables = keys.replace(')', '').split(',')
                local_variables = []
                continue

            # Ignore whatever is inside an interface block
            # because this may be confused with an actual subroutine body
            if 'interface' in line and not 'end' in line:
                in_interface = True

            if 'end interface' in line:
                in_interface = False

            # Look for subroutine body
            if in_subroutine:
                if '::' not in line:
                    body.append(line)
                else:
                    # Look for local variables
                    if 'intent' not in line:
                        local_variables.append(line)
    return db

# TODO: restore this as a separate driver
# def main(f, fout=None, ignore=None):
#     _ = extract(f, ignore=ignore.split(',') if ignore is not None else None)
#     if fout is None:
#         print(inline(f, _))
#     else:
#         with open(fout, 'w') as fh:
#             fh.write(inline(f, _))


def inline_source(source, ignore=None):
    # TODO: avoid passing via files and just use str sources
    import tempfile
    import os
    tmp_dir = tempfile.mkdtemp()
    tmp_file = os.path.join(tmp_dir, 'source.f90')
    with open(tmp_file, 'w') as tmp_fh:
        tmp_fh.write(source)
    db = extract(tmp_file, ignore=ignore.split(
        ',') if ignore is not None else None)
    return inline(tmp_file, db)
