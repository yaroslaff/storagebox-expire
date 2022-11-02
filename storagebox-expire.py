#!/usr/bin/env python3

import argparse
import os
import sys
import re
import datetime
from loguru import logger as log

import warnings
from cryptography.utils import CryptographyDeprecationWarning
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=CryptographyDeprecationWarning)
    import paramiko

args = None


now = datetime.datetime.now()

class BackupFile():
    def __init__(self, filename, name, date):
        self.filename = filename
        self.name = name
        self.date = date

    def __repr__(self):
        return "{}: {} {}".format(self.filename, self.name, self.date)

    def age_days(self):
        return (now - self.date).days


class BackupDirectory():
    def __init__(self):
        self._files = dict()
        self._latest = dict()

    def append(self, bfile):
        if bfile.name not in self._files:
            self._files[bfile.name] = list()
            self._latest[bfile.name] = bfile

        self._files[bfile.name].append(bfile)
        if bfile.date > self._latest[bfile.name].date:
            self._latest[bfile.name] = bfile

    def all_names(self):
        " Return all backup names "
        return self._files.keys()

    def all_files(self, name):
        for bf in self._files[name]:
            yield bf

    def latest(self, name):
        " Get latest bfile "
        return self._latest[name]
    
    def older(self, name, days):
        " True if no backup NAME or it's older then DAYS "
        if name not in self._latest:
            return True

        if self._latest[name].age_days() > days:
            return True
        
        return False

def get_args():

    def_daily = '/home/daily'
    def_monthly = '/home/monthly'
    def_key = os.path.join(os.path.expanduser('~'), ".ssh", "id_ed25519")
    def_re = '(?P<name>.+)-(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+).tar.gz'


    parser = argparse.ArgumentParser(description='Create monthy backups, delete expired backups from remote ssh machine (e.g. hetzner storagebox)')

    g = parser.add_argument_group('Commands')
    g.add_argument('--list', default=False, action='store_true', help='Just list daily backups')
    g.add_argument('--mkmonthly', default=False, action='store_true', help='Make monthly backups from daily')
    g.add_argument('--expire', type=int, metavar='DAYS', help='Delete expired daily backups, older then DAYS')


    g = parser.add_argument_group('Remote server location and authenticaton')
    g.add_argument('host')
    g.add_argument('-p', '--port', default=22)
    g.add_argument('-u', '--user')
    g.add_argument('-i', metavar='KEY', dest='key', default=def_key, help='Path to authentication key, def: {}'.format(def_key))
    
    g = parser.add_argument_group('Other storagebox options')
    g.add_argument('--daily', default=def_daily, help='path to daily backups. def: {}'.format(def_daily))
    g.add_argument('--monthly', default=def_monthly, help='path to daily backups. def: {}'.format(def_monthly))
    g.add_argument('--re', default=def_re, help='Filename parsing regex, def: {}'.format(def_re))

    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    return parser.parse_args()



def read_directories(client):
    daily=BackupDirectory()
    monthly=BackupDirectory()

    stdin, stdout, stderr = client.exec_command('ls {}'.format(args.daily))
    files = stdout.read().decode().split('\n')
    for f in files:
        if not f:
            continue
        bfile = parse_filename(f)
        daily.append(bfile)

    stdin, stdout, stderr = client.exec_command('ls {}'.format(args.monthly))
    files = stdout.read().decode().split('\n')
    for f in files:
        if not f:
            continue
        bfile = parse_filename(f)
        monthly.append(bfile)

    return daily, monthly

def parse_filename(filename):
    m = re.match(args.re, filename)
    if m is None:
        print(f"Cannot parse filename {filename!r} against regex {args.re!r}")
    assert(m)
    dt = datetime.datetime(int(m.group('year')), int(m.group('month')), int(m.group('day')))

    return BackupFile(filename, m.group('name'), dt)

def cmd_list(client):

    daily, monthly = read_directories(client)

    print("Daily:")
    for name in daily.all_names():
        print(daily.latest(name))
    print()

    print("Monthly:")
    for name in monthly.all_names():
        print(monthly.latest(name))
    print()


def expire(client, days):
    daily, monthly = read_directories(client)

    for name in daily.all_names():
        print("===", name)
        for bf in daily.all_files(name):
            if bf.age_days() > days:
                fullpath = os.path.join(args.daily, bf.filename)
                print("DELETE", fullpath)
                stdin, stdout, stderr = client.exec_command('rm {}'.format(fullpath))
                out = stdout.read().decode()
                err = stderr.read().decode()
                if out:
                    print(out)
                if err:
                    print(err)



def mkmonthly(client):
    
    daily, monthly = read_directories(client)

    print("Daily:")
    for name in daily.all_names():
        print(daily.latest(name))
    print()

    print("Monthly:")
    for name in monthly.all_names():
        print(monthly.latest(name))
    print()

    copied = 0

    for name in daily.all_names():
        if monthly.older(name, 30):
            src = os.path.join(args.daily, daily.latest(name).filename)
            dst = args.monthly
            print("UPDATE", src, dst)
            stdin, stdout, stderr = client.exec_command('cp {} {}'.format(src, dst))
            out = stdout.read().decode()
            err = stderr.read().decode()
            
            if out:
                print("out:", out.read())
            if err:
                print("err:", err.read())

            copied += 1

    print("Copied", copied, "backups")


    # print("err:", stderr.read())
    client.close()



def main():
    global args

    args = get_args()

    if not args.verbose:
        log.remove()
        log.add(sys.stderr, level="INFO")        

    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    client.connect(args.host, port=args.port, username=args.user, key_filename=args.key)
    
    print("{} started".format(now.strftime('%Y-%m-%d %H:%M')))

    if args.list:
        cmd_list(client)

    if args.mkmonthly:
        mkmonthly(client)

    if args.expire:
        expire(client, args.expire)

    
if __name__ == '__main__':
    main()