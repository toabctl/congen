#!/usr/bin/python3
# Copyright (c) 2019 SUSE Linux GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
from copy import deepcopy
import os
import sys

import jinja2
import yaml


def _merge(a, b):
    """merge b into a so b wins"""
    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], dict):
            result[k] = _merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


def _process_generate_check_args(args):
    if not os.path.exists(args.template):
        print('template {} not found'.format(args.template))
        sys.exit(1)

    for i in args.input:
        if not os.path.exists(i):
            print('input {} not found'.format(i))
            sys.exit(1)


def _do_process_generate(args):
    # open the template
    with open(args.template, 'r') as tpl:
        template = jinja2.Template(
            tpl.read(),
            undefined=jinja2.StrictUndefined)

    # open the input file(s)
    input_data = None
    for i in args.input:
        with open(i, 'r') as f:
            y = yaml.safe_load(f.read())
            if not input_data:
                input_data = y
            else:
                input_data = _merge(input_data, y)

    return template.render(**input_data)


def _process_generate(args=None):
    _process_generate_check_args(args)
    res = _do_process_generate(args)
    if args.output == '-':
        print(res)
    else:
        with open(args.output, 'w') as out:
            out.write(res)


def process_args():
    parser = argparse.ArgumentParser(
        description="Render Jinja2 templates with multiple input files")
    subparsers = parser.add_subparsers(help='sub-command help')
    # subparsers - generate
    parser_generate = subparsers.add_parser('generate', help='generate help')
    parser_generate.add_argument('-o', '--output', default='-',
                                 help='Output. "-" means stdout')
    parser_generate.add_argument('template', help='The template to use')
    parser_generate.add_argument('input', help='file to search for with input',
                                 nargs='+')
    parser_generate.set_defaults(func=_process_generate)
    args = parser.parse_args()
    # no subparser? Show the help
    if 'func' not in args:
        sys.exit(parser.print_help())
    return args


def main():
    args = process_args()
    args.func(args)


if __name__ == '__main__':
    sys.exit(main())
