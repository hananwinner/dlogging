import os
import re

_file_name = 'the_log_file.log'
_home_dir = os.path.expanduser('~')
_dlogging_home = os.path.join(_home_dir, "dlogging")
if not os.path.exists(_dlogging_home):
    os.makedirs(_dlogging_home)
_file_path = os.path.join(_dlogging_home, _file_name)
_updater_pid_file = 'dlogging/updater.pid'


def iterate_fds(pid):
    dir = '/proc/'+str(pid)+'/fd'
    if not os.access(dir,os.R_OK|os.X_OK): return

    for fds in os.listdir(dir):
        for fd in fds:
            full_name = os.path.join(dir, fd)
            try:
                file = os.readlink(full_name)
                if file == '/dev/null' or \
                  re.match(r'pipe:\[\d+\]',file) or \
                  re.match(r'socket:\[\d+\]',file):
                    file = None
            except OSError as err:
                if err.errno == 2:
                    file = None
                else:
                    raise(err)

            yield (fd,file)


def _get_updater_pid():
    pid = None
    if os.path.exists(_updater_pid_file):
        with open(_updater_pid_file, "r") as fdr:
            pid = fdr.readline()
    return pid


def _logger_check_file_free():
    pid = _get_updater_pid()
    if pid is not None:
        for fd, file in iterate_fds(pid):
            if file == _file_path:
                return False
    return True
