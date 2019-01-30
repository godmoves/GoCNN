#!/usr/bin/env python2
import os


URL_BASE = "http://www.yss-aya.com/cgos/9x9/archives/9x9_%d_%02d.tar.bz2"


def download_extract_file(year, month):
    print("downloading cgos data: year=%d, month=%02d" % (year, month))
    url = URL_BASE % (year, month)
    file_name = url.split('/')[-1]
    res = os.system("wget %s" % url)
    # if we download successfully
    if res == 0:
        # make a new folder and extract data into it
        dir_name = str(year) + "_" + str(month)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        res = os.system("tar -jxf %s -C %s" % (file_name, dir_name))
        os.remove(file_name)
        assert(res == 0)
    return res


def download_cgos_data(save_path):
    # move to the save_path first
    os.chdir(save_path)
    print('save cgos 9x9 data in %s\n' % os.getcwd())
    for y in range(2015, 2019):
        for m in range(1, 13):
            download_extract_file(y, m)
