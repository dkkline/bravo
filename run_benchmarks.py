#!/usr/bin/env python

from __future__ import division

import time
import glob
import imp
import math
import os.path
import urllib
import urllib2


def average(l):
    return sum(l) / len(l)


def stddev(l):
    return math.sqrt(sum((i - average(l))**2 for i in l))


def main():
    start_time = time.time()
    for bench in glob.glob("benchmarks/*.py"):
        name = os.path.splitext(os.path.basename(bench))[0]
        module = imp.load_source("bench", bench)
        benchmarks = module.benchmarks
        print "Running benchmarks in %s..." % name
        for benchmark in benchmarks:
            name, l = benchmark()
            print "%s: Average %f, min %f, max %f, stddev %f" % (
                name, average(l), min(l), max(l), stddev(l))

    print "\nTotal time: %s" % (time.time() - start_time)


if __name__ == "__main__":
    main()
