#!/bin/python3
import os
import subprocess
import sys


def do_call(args):
    oneline = ['"{}"'.format(x) for x in args]
    oneline = ' '.join(oneline)
    print('[{}]> {}'.format(os.getcwd(), oneline))
    try:
        subprocess.check_call(args, env=os.environ)
    except subprocess.CalledProcessError as error:
        print(error)
        print(error.output)
        sys.exit(1)


def run_mypy():
    print('Run mypy')
    do_call(['mypy', '.'])


def run_flake8():
    print('Run flake8')
    do_call(['flake8', '.'])


if __name__ == "__main__":
    run_flake8()
    run_mypy()
