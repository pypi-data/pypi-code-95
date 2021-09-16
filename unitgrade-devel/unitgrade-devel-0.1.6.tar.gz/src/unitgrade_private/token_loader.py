import glob
import os
import pickle
import bz2
import zipfile
import io

def unpack_sources_from_token(token_file, destination=None):
    # with open(token_file, 'rb') as f:
    #     rs = pickle.load(f)
    from unitgrade_private import load_token

    data, _ = load_token(token_file)
    if destination is None:
        destination = os.path.dirname(token_file )
    destination = os.path.normpath(destination)

    for k, data in rs['sources'].items():

        out = destination +"/" + os.path.basename(token_file)[:-6] + f"_{k}/"

        if not os.path.exists(out):
            zip = zipfile.ZipFile(io.BytesIO(data['zipfile']))
            zip.extractall(out)


if __name__ == "__main__":
    import irlc
    import irlc.assignments.assignment_fruit as fa
    fa.__file__


    dn = os.path.dirname(fa.__file__ )

    l = glob.glob(dn+"/*fruit*.token")
    token_file = l[0]
    print(token_file)

    rs = unpack_sources_from_token(token_file)

    a = 3455