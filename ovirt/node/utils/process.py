#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# process.py - Copyright (C) 2012 Red Hat, Inc.
# Written by Fabian Deutsch <fabiand@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.  A copy of the GNU General Public License is
# also available at http://www.gnu.org/copyleft/gpl.html.

"""
Some convenience functions related to processes
"""

import subprocess
import logging

LOGGER = logging.getLogger(__name__)

COMMON_POPEN_ARGS = {
    "close_fds": True,
    "shell": True
}

CalledProcessError = subprocess.CalledProcessError


def popen(*args, **kwargs):
    """subprocess.Popen wrapper to not leak file descriptors
    """
    kwargs.update(COMMON_POPEN_ARGS)
    LOGGER.debug("Popen with: %s %s" % (args, kwargs))
    return subprocess.Popen(*args, **kwargs)


def call(*args, **kwargs):
    """subprocess.call wrapper to not leak file descriptors
    """
    kwargs.update(COMMON_POPEN_ARGS)
    LOGGER.debug("Calling with: %s %s" % (args, kwargs))
    return int(subprocess.call(*args, **kwargs))


def check_call(*args, **kwargs):
    """subprocess.check_call wrapper to not leak file descriptors
    """
    kwargs.update(COMMON_POPEN_ARGS)
    LOGGER.debug("Checking call with: %s %s" % (args, kwargs))
    return int(subprocess.check_call(*args, **kwargs))


def check_output(*args, **kwargs):
    """subprocess.check_output wrapper to not leak file descriptors
    """
    kwargs.update(COMMON_POPEN_ARGS)
    LOGGER.debug("Checking output with: %s %s" % (args, kwargs))
    return subprocess.check_output(*args, **kwargs)


    #return unicode(subprocess.check_output(*args, **kwargs))


def pipe(cmd, stdin=None):
    """Run a non-interactive command and return it's output

    Args:
        cmd: Cmdline to be run
        stdin: (optional) Data passed to stdin

    Returns:
        stdout, stderr of the process (as one blob)
    """
    return popen(cmd,shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT).communicate(stdin)[0]


def pipe_async(cmd, stdin=None):
    # https://github.com/wardi/urwid/blob/master/examples/subproc.py
    process = popen(cmd, shell=True, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    if stdin:
        process.stdin.write(stdin)
    while process.poll() != 0:
        yield process.stdout.readline()
if __name__ == '__main__':
    #cmd = "engine-file-setup --answer-file=/etc/ovirt-engine/engine-setup.conf.temp"
    cmd = "service postgresql stop"
    print pipe(cmd)
    #for i in pipe_async(cmd,stdin='-sh'):
    #    print i
    #    if not i:
    #        break
        
