import glob
import os
import pickle
import bz2
import zipfile
import io

def load_token(token_file):
    with open(token_file, 'rb') as f:
        rs = pickle.load(f)

    for k, data in rs['sources'].items():

        out = os.path.dirname(token_file ) +"/" + os.path.basename(token_file)[:-6] + f"_{k}/"

        if not os.path.exists(out):
            zip = zipfile.ZipFile(io.BytesIO(data['zipfile']))
            zip.extractall(out)


    #
    #
    # # in_memory = StringIO.StringIO(original_zip_data)
    # # zf = ZipFile(in_memory, "a")
    #
    #
    #     # read the sources:
    #
    #
    # # with pickle.load(f)
    #
    #
    # # Legacy
    # with bz2.open(token_file, "rt") as f:
    #     s = f.read()
    #
    # import json
    # res = json.loads(s)
    #
    # def pres(res):
    #     for q, qval in res['details'].items():
    #         # print(qval)
    #         for k, v in qval['items'].items():
    #             # for k in qval:
    #             print(q, k, v)
    #
    # if False:
    #     sources = res['sources']
    #     l1 = list(set( [k.split("\\")[-1] for k in sources] ))
    #     for dl in l1:
    #         t = 0
    #         lines = 0
    #         for k, s in res['sources'].items():
    #             kk = k.split('\\')
    #             if kk[-1] != dl:
    #                 continue
    #             t += len(s)
    #             l = len(s.splitlines())
    #             lines += l
    #             # print(k, len(s), l)
    #         print(dl, "total", lines)
    #
    # return res

if __name__ == "__main__":
    import irlc
    import irlc.assignments.assignment_fruit as fa
    fa.__file__


    dn = os.path.dirname(fa.__file__ )

    l = glob.glob(dn+"/*fruit*.token")
    token_file = l[0]
    print(token_file)

    rs = load_token(token_file)

    a = 3455