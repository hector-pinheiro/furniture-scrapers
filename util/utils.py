import os
import uuid


def mkdir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def print_update_progress(prefix, done, total):
    print('\r{}{}/{} done, {:.1f}%'.format(prefix, done, total, int(100 * float(done) / total)), end='', flush=True)


def generate_id():
    return uuid.uuid4().hex[:12]
