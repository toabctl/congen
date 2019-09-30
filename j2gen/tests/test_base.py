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
import tempfile
import unittest
from unittest import mock

from ddt import ddt, data, unpack

import jinja2
import j2gen


@ddt
class TestBasics(unittest.TestCase):
    """Test basic stuff"""
    @data(
        [{}, {}, {}],
        [None, None, None],
        [(), (), ()],
        [1, {}, 1],
        [{}, 1, 1],
        [None, 1, 1],
        [[1, 2, 3], 1, 1],
        [{'f': 1}, {'f': 2}, {'f': 2}],
        [{'f': 1, 'x': 2}, {'f': 2}, {'f': 2, 'x': 2}],
    )
    @unpack
    def test__merge(self, data1, data2, expected):
        """test different cases to merge 2 dicts (or other data types"""
        self.assertEqual(j2gen._merge(data1, data2), expected)

    @mock.patch('j2gen._process_generate_check_args')
    @data(
        [
            '{{ v1 }}',  # the template
            ['v1: x'],  # list of inputs (yaml format)
            'x'  # expected result
        ],
        [
            '{{ v1 }}',
            ['v1: x', 'v1: y'],
            'y'
        ],
        [
            '{{ v1.x }}',
            ["""---
            v1:
              x: foo
            """],
            'foo'
        ],
    )
    @unpack
    def test__do_process_generate(self, tpl_str, inputs_str, expected_result,
                                  mock_check_args):
        with tempfile.NamedTemporaryFile(mode='w') as tpl:
            # write template example
            tpl.write(tpl_str)
            tpl.seek(0)
            # handle inputs
            inputs = []
            for i_str in inputs_str:
                i_tmp = tempfile.NamedTemporaryFile(mode='w')
                # write input1 data example
                i_tmp.write(i_str)
                i_tmp.seek(0)
                # remember the list of inputs
                inputs.append(i_tmp)

            try:
                # do the work
                rendered = j2gen._do_process_generate(
                    argparse.Namespace(output='-',
                                       input=[i.name for i in inputs],
                                       template=tpl.name))
                # check result
                self.assertEqual(rendered, expected_result)
            finally:
                # close to delete tempfiles
                for i in inputs:
                    i.close()

    def test__do_process_generate_undefined_variable(self):
        with tempfile.NamedTemporaryFile(mode='w') as tpl, \
             tempfile.NamedTemporaryFile(mode='w') as input1:
            # write template example
            tpl.write('{{ unkown }}')
            tpl.seek(0)
            # write input
            input1.write("""---
            well_known: 1""")
            input1.seek(0)
            # do the work
            ns = argparse.Namespace(output='-',
                                    input=[input1.name],
                                    template=tpl.name)
            with self.assertRaises(jinja2.exceptions.UndefinedError):
                j2gen._do_process_generate(ns)


if __name__ == '__main__':
    unittest.main()
