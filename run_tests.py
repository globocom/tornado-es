#!/usr/local/bin/python2.7

import unittest2

test_path = "tornadoes/testes/"

def main():
    suite = unittest2.loader.TestLoader().discover(test_path)
    result=unittest2.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(bool(result.failures + result.errors))


if __name__ == '__main__':
    main()
