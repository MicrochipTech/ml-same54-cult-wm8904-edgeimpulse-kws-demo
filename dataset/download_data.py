#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:46:13 2021

@author: toemo
"""
import os, sys

__usage__ = '''\
download_data.py <output-directory>'''

def main(argv):
    try:
        wdir = argv[1]
    except IndexError:
        print("usage: %s" % __usage__, file=sys.stderr)
        return -1    

    # Create a work directory        
    if not os.path.exists(wdir):
        os.mkdir(wdir)
    
    # Download datasets
    import urllib.request
    url = 'http://download.tensorflow.org/data/speech_commands_v0.02.tar.gz'
    
    gsc_fn = os.path.join(wdir, url.rsplit('/', 1)[1])
    urllib.request.urlretrieve(url, gsc_fn)
    
    url = 'https://cdn.edgeimpulse.com/datasets/keywords2.zip'
    
    eik_fn = os.path.join(wdir, url.rsplit('/', 1)[1])
    urllib.request.urlretrieve(url, eik_fn)
    
    # Extract and combine datasets
    import tarfile
    
    with tarfile.open(gsc_fn, "r:gz") as tf:
        tf.extractall(path=wdir)
        
    import zipfile
    
    with zipfile.ZipFile(eik_fn, "r") as zf:
        for fn in zf.namelist():
            if fn.startswith('noise/'):
                zf.extract(fn, wdir)
            
if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
