import sys
import credentials
from Profiler import Profiler


def file_to_dict(filename):
    ret = {}
    with open(filename, "r") as file:
        line = file.readline()
        while line:
            line = line.strip()
            if line != "":
                ret[line] = line
            line = file.readline()
    print(f"Read {len(ret)} lines from {filename}")
    return ret


# Main entrypoint of script
if __name__ == "__main__":

    with Profiler("Elapsed time {}"):
        i = file_to_dict("i_728k.csv")
        o = file_to_dict("o_440k.csv")
        ret = {}
        for il in i:
            if not bool(o.get(il)):
                ret[il] = il

        out_filename = "out_io.csv"
        with open(out_filename, "w") as outfile:
            for ol in ret:
                bob = f"https://gapi.beeketing.com/v1/recsys/recommendation/result/v2/{ol}/best-seller\n"
                # 				outfile.write(f"{ol}\n");
                outfile.write(bob)
            bob = f"https://gapi.beeketing.com/v1/recsys/recommendation/result/v2/{ol}/best-seller\n"
            print(f"Wrote {len(ret)} lines to {out_filename}")
