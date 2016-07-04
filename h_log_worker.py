#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
import logging
import re
import gzip

sensors = []

def argParse():
    parser = argparse.ArgumentParser(usage="./logWorker.py -s <sourceDir> -d <destDir>")
    parser.add_argument('-s', dest='source_dir', help='specify the archive source directory')
    parser.add_argument('-d', dest='dest_dir', help='specify the destination directory')
    args = parser.parse_args()
    source_dir = args.source_dir
    dest_dir = args.dest_dir
    if source_dir is None or dest_dir is None:
        print(parser.usage)
        exit(0)

    return source_dir, dest_dir


def createFileStructure(archive_files, source_dir, dest_dir):
    # sensor_list = [x for x in source_dir if x.endswith('gz')]
    global sensors
    pattern = '(\w+-\w+-\w+)\.\d{4}-\d{2}-\d{2}-(\d{4})'
    try:
        for archive in archive_files:
            found = re.search(pattern, str(archive))
            if found:
                sen_full_path = os.path.join(dest_dir, found.group(1))  # checks to see if sensor file path exists
                if os.path.exists(sen_full_path):
                    # print('already exists')
                    # unpack(source_dir, archive, sen_full_path)
                    continue
                # print(found.group(1))
                else:
                    sensors.append(found.group(1))
                    os.mkdir(os.path.join(dest_dir, found.group(1)))
                if os.path.exists(os.path.join(dest_dir, found.group(1), 'since_db')):
                    continue
                else:
                    os.mkdir(os.path.join(dest_dir, found.group(1), 'since_db'))
                    # unpack(source_dir, archive, sen_full_path)

    except Exception as e:
        print(e)


def getSensorName(archive):
    pattern = '(\w+-\w+-\w+)\.\d{4}-\d{2}-\d{2}-(\d{4})'
    found = re.search(pattern, str(archive))
    if found:
        return found.group(1)


def unpack(source_dir, archive_files, dest_dir):
    for archive in archive_files:
        sensor_name = getSensorName(archive)
        dest_full_path = os.path.join(dest_dir, sensor_name, archive[:-4])
        # print(dest_full_path)
        try:
            with gzip.open((os.path.join(source_dir, archive)), 'rt') as infile:
                s = infile.read()
                # print(s)

            with open(dest_full_path, 'w+') as outfile:
                # print(s)
                # print(dest_full_path)
                outfile.write(str(s))
        except Exception as e:
            print(str(e))


def normalize(dest_dir):
    global sensors
    for sensor in sensors:
        dest_dir = os.path.join(os.path.abspath(dest_dir), sensor) # /Users/asoa/PycharmProjects/152/test/<sensor>
        for log in os.listdir(dest_dir):
            # print(log)
            with open(os.path.join(dest_dir, log), 'r') as infile:
                # print(infile.read())
                lines = infile.readlines()[8:]
                with open(os.path.join(dest_dir, log + '_done'), 'w') as outfile:
                    for line in lines:
                        outfile.write(str(line))

def cleanUp(dest_dir):
    ## run this command to only run this function
    # python3 -c 'import os; from logWorker import *; cleanUp("/Users/asoa/PycharmProjects/152/test/")
    sensors = []
    cmd = ['rm', '-r', dest_dir]

    for root, dirs, files in os.walk(dest_dir):
        for dir in dirs:
            pattern = '\w+-\w+-\w+'
            found = re.search(pattern, dir)
            if found:
                sensors.append(found.group())

    for sensor in sensors:

        for root, dirs, files in os.walk(os.path.join(dest_dir, sensor)):
            for file in files:
                os.remove(os.path.join(dest_dir, sensor, file))
        for root, dirs, files in os.walk(os.path.join(dest_dir, sensor, 'since_db')):
            for file in files:
                os.remove(os.path.join(dest_dir, sensor, file))

    # prompt = '>>> '
    # print('All is done and you should have logfiles at {} for ingestion into logastash'.format(dest_dir))
    # print('Hit enter when logstash has ingested all files; all files will be deleted')
    # input(prompt)
    # cmd = ['rm', '-r', dest_dir]
    # subprocess.call(cmd)
    # os.mkdir('test')  # directory is recreated to prepare for next run of script


def main():
    ## test code
    # source_dir = '/Users/asoa/junk/'
    # dest_dir = '/Users/asoa/PycharmProjects/152/test/'
    source_dir, dest_dir = argParse()
    archive_files = [x for x in os.listdir(source_dir) if x.endswith('gz')]
    createFileStructure(archive_files, source_dir, dest_dir)
    unpack(source_dir, archive_files, dest_dir)
    #normalize(dest_dir)
    #cleanUp(dest_dir)

if __name__ == "__main__":
    main()