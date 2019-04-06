#!/usr/bin/env python3

# Written by Stephen Fromm <stephenf nero net>
# (C) 2014 University of Oregon
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import argparse
import datetime
import glob
import imp
import logging
import os
import sys
import time
from peewee import CharField, DateTimeField, Model

import netspryte.constants as C
from netspryte.utils import setup_logging
from netspryte.manager import Manager

DEFAULT_MIGRATIONS_PATH = os.path.join(os.path.dirname(__file__), "migrations")


class Migration(Model):
    ''' Migration model to track migration status '''
    migration = CharField()
    timestamp = DateTimeField(default=datetime.datetime.now)


def get_filenames(dir_name):
    files = []
    for path in glob.glob(os.path.join(dir_name, '*.py')):
        files.append(os.path.basename(path))
    return sorted(files, key=lambda fname: int(fname.split("_")[0]))


def log_migration(model, name, direction):
    if direction == 'up':
        model.insert(migration=name).execute()
    else:
        model.delete().where(model.migration == name).execute()


def do_migration(model, path, direction, mgr):
    ''' Handle specific migration '''
    if not os.path.exists(path):
        logging.error("Path %s does not exist; cannot perform migration", path)
        return False
    dir_name = os.path.dirname(path)
    name, ext = os.path.splitext(os.path.basename(path))

    migration_exists = model.select().where(model.migration == name).limit(1).exists()

    if migration_exists and direction == 'up':
        logging.warning("Migration %s already exists; skipping.", name)
        return False
    if not migration_exists and direction == 'down':
        logging.warning("Migration %s does not exist; skipping.", name)
        return False

    logging.info("Loading migration %s", name)
    try:
        (fp, pathname, descr) = imp.find_module(name, [dir_name])
        try:
            module = imp.load_module(name, fp, pathname, descr)
        finally:
            fp.close()
    except Exception as e:
        logging.error("failed to load migration '%s': %s", name, str(e))
        return False

    if not hasattr(module, direction):
        logging.error("Migration %s does not implement %s migration", name, direction)
        return False
    logging.info("Running %s migration %s", direction, name)
    r = getattr(module, direction)(mgr)
    if r:
        log_migration(model, name, direction)
    return r


def migrate_db(migration_path, direction, migration=None):
    migrations = []
    mgr = Manager(create=False)
    if not mgr.database:
        logging.error("Did not find database model object")
    model = Migration
    model._meta.database = mgr.database
    model.create_table(fail_silently=True)

    if os.path.isdir(migration_path):
        migrations = get_filenames(migration_path)
    if not migrations:
        logging.warning("No migrations found")
    if direction == 'down':
        migrations.reverse()

    if migration is not None:
        if migration not in migrations and '%s.py' % migration not in migrations:
            logging.error("Could not find migration %s", migration)
            return False
        fname = os.path.join(migration_path, migration)
        if not os.path.exists(fname):
            migration += ".py"
        result = do_migration(model, os.path.join(migration_path, migration), direction, mgr)
        return True

    for f in migrations:
        result = do_migration(model, os.path.join(migration_path, f), direction, mgr)
    return True


def main():
    ''' main '''
    parser = argparse.ArgumentParser(description="Facilitate database migrations",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m', '--migrations',
                        default=DEFAULT_MIGRATIONS_PATH,
                        help='Path to MIGRATIONS directory')
    parser.add_argument('-d', '--direction', choices=['up', 'down'],
                        default='up', help='Migration direction: up or down')
    parser.add_argument('-M', '--migration',
                        help='Only migrate up/down to this version')
    parser.add_argument('-v', '--verbose',
                        action="count", default=C.DEFAULT_VERBOSE,
                        help='Be verbose.  Use more than once to increase verbosity')
    args = parser.parse_args()
    setup_logging(args.verbose)
    if not args.direction:
        logging.warning("Missing required argument 'up' or 'down'")
        return 1
    logging.warning("You are strongly encouraged to backup your database before proceeding")
    time.sleep(1.0)
    migrate_db(args.migrations, args.direction, args.migration)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        sys.exit(1)
