#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
# import shutil
import json
import random
from glob import glob, iglob
from itertools import chain, groupby
ichain = chain.from_iterable

__usage__ = "split_data.py <data-directory> <keyword-class-1> [<keyword-class-2>...]"

MAX_SAMPLES_PER_CLASS = 1500
delimiter = '\0'

random.seed(0)

def sample_over_classes(datadict, N, shuffle=True):
    i = 0
    classes = sorted(datadict, key=lambda cls: len(datadict[cls]))
    while N > 0:
        m = max(1, N//len(classes))
        cls = classes.pop(i)
        m = min(m, len(datadict[cls]))
        x = datadict[cls]
        if shuffle:
            random.shuffle(x)
        yield (cls, x[:m])
        N -= m

def num_samples_over_classes(datadict, N):
    i = 0
    classes = sorted(datadict, key=lambda cls: len(datadict[cls]))
    while N > 0:
        m = max(1, N//len(classes))
        cls = classes.pop(i)
        m = min(m, len(datadict[cls]))
        yield (cls, m)
        N -= m
        
def group_by_pid(files):
    pid_files = groupby(files, key=lambda fn: os.path.basename(fn).split('_nohash_')[0])
    return dict((x,list(y)) for x,y in pid_files)

def main(argv):
    if len(argv) < 3:
        print("usage: %s" % __usage__, file=sys.stderr)
        return -1
    
    wdir = argv[1]
    if not os.path.exists(wdir):
        raise Exception("Data directory does not exist: %s" % wdir)
        
    target_classes = [x.lower() for x in argv[2:]]
    
    stats = {'totals': {}}

    #%% Get class names
    classes = [os.path.basename(fn) for fn in iglob(os.path.join(wdir, '*')) if os.path.isdir(fn) and not fn.startswith('_')]
    
    # Check input classes are valid
    invalidclasses = set(target_classes).difference(classes)
    if len(invalidclasses):
        raise Exception("Target classes not found: %s" % invalidclasses)
    
    #%% Write lists for target classes
    for cls in target_classes:
        pid_files = group_by_pid(iglob(os.path.join(wdir, cls, '*.wav')))
        samples = dict(sample_over_classes(pid_files, MAX_SAMPLES_PER_CLASS))
        clsfiles = list(ichain(samples.values()))
        
        with open(cls + '_list.txt', 'w') as fh:
            fh.write(delimiter.join(fn.replace(os.sep, '/') for fn in clsfiles))
        
        stats['totals'][cls] = len(clsfiles)
        stats[cls] = [os.path.relpath(fn, wdir).replace(os.sep, '/') for fn in clsfiles]
        # if not os.path.exists(cls):
        #     os.mkdir(cls)
        # for fn in files:
        #     shutil.copyfile(fn, os.path.join(cls, os.path.basename(fn)))
        
    #%% Write list for 'unknown' class
    unknown_classes = set(classes).difference(target_classes)
    unknown_files = { cls: glob(os.path.join(wdir, cls, '*.wav')) for cls in unknown_classes }
    
    files = []
    stats['unknown'] = []
    for cls, m in num_samples_over_classes(unknown_files, MAX_SAMPLES_PER_CLASS):
        pid_files = group_by_pid(unknown_files[cls])
        samples = dict(sample_over_classes(pid_files, m))
        clsfiles = list(ichain(samples.values()))
        
        files.extend(clsfiles)
        
        stats['unknown'] += [os.path.relpath(fn, wdir).replace(os.sep, '/') for fn in clsfiles]
    stats['totals']['unknown'] = len(stats['unknown'])
        
    with open('unknown_list.txt', 'w') as fh:
        fh.write(delimiter.join(fn.replace(os.sep, '/') for fn in files))
        # if not os.path.exists('unknown'):
        #     os.mkdir('unknown')
        # for fn in files:
        #     shutil.copyfile(fn, os.path.join('unknown', os.path.basename(fn)))
    
    #%% Write list for 'noise' class
    noise_classes = set(os.path.basename(fn).rsplit('.')[-4].rsplit('_', 1)[0] for fn in glob(os.path.join(wdir, 'noise', '*.wav')))
    noise_files = { cls: glob(os.path.join(wdir, 'noise', '*.' + cls + '*.wav')) for cls in noise_classes }
    
    samples = dict(sample_over_classes(noise_files, MAX_SAMPLES_PER_CLASS))
    clsfiles = list(ichain(samples.values()))
    
    with open('noise_list.txt', 'w') as fh:
        fh.write(delimiter.join(fn.replace(os.sep, '/') for fn in clsfiles))
    
    stats['totals']['noise'] = { cls: len(samples[cls]) for cls in samples }
    stats['noise'] = [os.path.relpath(fn, wdir).replace(os.sep, '/') for fn in clsfiles]
    
    #%% Write stats
    print(json.dumps(stats.pop('totals'), indent=4))
    with open('sample_list.json', 'w') as fh:
        json.dump(stats, fh, indent=4)

if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)