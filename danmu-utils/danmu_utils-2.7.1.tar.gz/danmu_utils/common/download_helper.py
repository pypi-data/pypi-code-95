import os
import time


__all__ = ['download_line', 'download_file', 'download_dir']


def download_line(line, tool, add_file_timestamp=False, output_dir='.'):
    print('Start download line: "%s".' % line.strip('\n'))
    line_res = tool.download(line)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for item in line_res:
        filename = item['filename']
        if add_file_timestamp:
            tmp_1 = os.path.splitext(filename)
            timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime())
            filename = tmp_1[0] + '_' + timestamp + tmp_1[1]
        filename = os.path.join(output_dir, filename)
        with open(filename, 'wb') as f:
            f.write(item['data'])


def download_file(filename, tool, add_dir_timestamp=False, add_file_timestamp=False, output_dir=None):
    print('Start process list file: "%s".' % filename)
    tmp_1 = os.path.splitext(filename)
    if tmp_1[1] == '.' + tool.DANMU_LIST_EXTNAME:
        out_dir = tmp_1[0]
    else:
        out_dir = filename
    if output_dir != None:
        out_dir = output_dir
    if add_dir_timestamp:
        timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime())
        out_dir = out_dir + '_' + timestamp
    with open(filename, encoding='utf8') as f:
        for line in f:
            try:
                download_line(line, tool, add_file_timestamp=add_file_timestamp, output_dir=out_dir)
            except Exception as e:
                print(e)
                continue
    print('Success generate dir: "%s" for list file.' % out_dir)


def download_dir(dirname, tool, add_dir_timestamp=False, add_file_timestamp=False, output_dir=None):
    print('Start process dir: "%s".' % dirname)
    for filename in os.listdir(dirname):
        filename = os.path.join(dirname, filename)
        if not os.path.isfile(filename):
            continue
        if os.path.splitext(filename)[1] != '.' + tool.DANMU_LIST_EXTNAME:
            continue
        download_file(filename, tool, add_dir_timestamp=add_dir_timestamp, add_file_timestamp=add_file_timestamp, output_dir=output_dir)
    print('Success process dir: "%s".' % dirname)