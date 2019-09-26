j2gen
=====
Tool to render `Jinja2`_ templates with mutliple input `YAML`_ data sources.

Features
--------
- Render files as `Jinja2`_ templates (usually ending with .j2)
- Use `YAML`_ as data source for templating
- Multiple YAML data sources are allowed to overlay sources

Usage
-----
Let's show some examples what `j2gen`_ is good for.

Simple rendering
++++++++++++++++
A `test.j2` template::

  Hello {{ variable }} !

A `test.yaml` file containing the data::

  ---
  variable: world

Will render to::

  $ j2gen generate test.j2 test.yaml
  Hello world !

By default, `j2gen`_ will write its output to stdout. Use the `--output`
(or `-o`) flag to write to a file::

  $ j2gen generate -o output test.j2 test.yaml
  $ cat output
  Hello world !

Rendering with multiple sources
+++++++++++++++++++++++++++++++
There are cases where you want a common data source (eg. `common.yaml`)
but need to overwrite parts of the common source (eg. with `special.yaml`):

`common.yaml` looks like::

  container:
    base: openSUSE-Leap-15.1
    name: memcached container for openSUSE
    description:
      short: memcached container
      long: memcached container for openSUSE

`special.yaml` looks like::

  container:
    base: SLES15SP1
    name: memcached container for SLES15SP1
    description:
      long: memcached container for SUSE Linux Enterprise Server 15 SP1

`template.j2` looks like::

  Base      : {{ container.base }}
  Name      : {{ container.name }}
  Desc short: {{ container.description.short }}
  Desc long : {{ container.description.long }}

This results in::

  $ j2gen generate template.j2 common.yaml special.yaml
  Base      : SLES15SP1
  Name      : memcached container for SLES15SP1
  Desc short: memcached container
  Desc long : memcached container for SUSE Linux Enterprise Server 15 SP1

Note here that `container.description.short` is taken from the `common.yaml`
input while all the other variables are overwritten with the values from
`special.yaml`. So dict/hash like structures in the YAML data sources are deep
merged.
Another important part is the order of the `input` files when calling
`j2gen generate`. The last source wins (in this case `special.yaml`).

Contributing
------------
I'm happy about every contribution like bugfixes, filling issues, improving
documentation or whatever.

- For bugs: https://github.com/toabctl/j2gen/issues
- For changes: https://github.com/toabctl/j2gen/pulls

Running tests
+++++++++++++

The testsuite can be executed locally with::

  $ tox

.. _Jinja2: https://jinja.palletsprojects.com/
.. _YAML: https://yaml.org/
.. _j2gen: https://github.com/toabctl/j2gen
