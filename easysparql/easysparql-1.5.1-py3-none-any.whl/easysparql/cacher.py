import hashlib
import os


class Cacher:

    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)

    def get_cache_if_any(self, query):
        if not self.cache_dir:
            return None

        fname = hashlib.blake2b(str.encode(query)).hexdigest()+".txt"
        cache_f_path = os.path.join(self.cache_dir, fname)
        rows = []
        if os.path.exists(cache_f_path):
            f = open(cache_f_path)
            for line in f:
                if line.strip() != "":
                    row = line.strip().split('\t')
                    rows.append(row)
            f.close()
            return rows
        return None

    def write_to_cache(self, query, data, keys):
        fname = hashlib.blake2b(str.encode(query)).hexdigest()+".txt"
        cache_f_path = os.path.join(self.cache_dir, fname)
        if type(data) == str:
            f = open(cache_f_path, 'w')
            f.write("\t".join(keys))
            f.write("\n")
            f.write(data)
            f.close()
        elif type(data) == list:
            f = open(cache_f_path, 'w')
            for attrs in data:
                line = "\t".join(attrs)
                f.write(line)
                f.write("\n")
            f.close()
        else:
            print("type: %s" % (str(type(data))))
            print(data)
            raise Exception("Invalid data type for data to cache. Expecting a string or a list of lists")

    def write_results_to_cache(self, query, data):
        fname = hashlib.blake2b(str.encode(query)).hexdigest()+".txt"
        cache_f_path = os.path.join(self.cache_dir, fname)
        f = open(cache_f_path, 'w')
        for idx, row in enumerate(data):
            ks = [k for k in row.keys()]
            if idx == 0:
                line = "\t".join(ks)
                f.write(line)
                f.write('\n')
            attrs = [row[k]['value'] for k in ks]
            line = "\t".join(attrs)
            f.write(line)
            f.write("\n")
        f.close()

    def data_to_dict(self, rows):
        results = []
        if rows and len(rows)> 0:
            keys = rows[0]
            for i in range(1, len(rows)):
                d = dict()
                for idx, k in enumerate(keys):
                    d[k] = {
                        'value': rows[i][idx]
                    }
                results.append(d)
        return results