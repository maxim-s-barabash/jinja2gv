#!/usr/bin/env python

'''
    jinja2gv
    ~~~~~~~~~~~~~~
    :copyright: Copyright 2017 by Maxim.S.Barabash <maxim.s.barabash@gmail.com>.
    :license: BSD, see LICENSE for details.
'''

from __future__ import unicode_literals
import sys
import io
from collections import defaultdict
from importlib import import_module
from jinja2 import Environment
from jinja2 import meta


TMPL = """digraph "templates" {{
charset="utf-8"
rankdir=LR
{nodes}
{edges}
}}\n"""


def get_env(path):

    if ':' not in path:
        path += ':env'

    null = io.BytesIO()

    module_name, obj_name = path.split(':', 1)
    save_stdout, save_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = null

    try:
        env = import_module(module_name)
        for name in obj_name.split('.'):
            env = getattr(env, name)
    finally:
        sys.stdout, sys.stderr = save_stdout, save_stderr

    return env


def indexing(env):

    def _get_blocks(template_name):
        template = env.get_template(template_name)
        return ['\{{% {} %\}}'.format(block) for block in template.blocks]

    list_templates = env.loader.list_templates()

    template_index = defaultdict(list)
    for name in list_templates:
        template_source = env.loader.get_source(env, name)
        ast = env.parse(template_source[0])
        deps = list(meta.find_referenced_templates(ast))
        for d in deps:
            template_index[d] += []
        template_index[name].extend(deps)

    node_index = {}
    nodes = []
    for idx, name in enumerate(template_index):
        node_index[name] = idx
        if name in list_templates:
            body = _get_blocks(name)
            label = '{{{name}|{body}}}'.format(name=name, body='\l'.join(body))
            style = 'shape="record"'
        else:
            label = name
            style = 'shape="box", style="dashed", fontcolor="red", color="red"'
        nodes.append('"{}" [label="{}", {}];'.format(idx, label, style))

    edges = []
    for node, idx1 in node_index.items():
        for dep in set(template_index.get(node, [])):
            idx2 = node_index.get(dep)
            if idx2 is not None:
                style = 'arrowhead="open", arrowtail="none"'
                edges.append('"{}" -> "{}" [{}];'.format(idx1, idx2, style))

    return nodes, edges


def main(path):
    env = get_env(path)
    if isinstance(env, Environment):
        nodes, edges = indexing(env)
        print(TMPL.format(nodes='\n'.join(nodes), edges='\n'.join(edges)))
    else:
        print('Object is not jinja2 Environment')
        return 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1]))
    else:
        print('Usage jinja2gv module:environment')
