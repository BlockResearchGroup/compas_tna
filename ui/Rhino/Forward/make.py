from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


from frontcontroller import HiLoShellFrontController

with open(os.path.join(HERE, 'rui_config.json'), 'r') as fp:
    config = json.load(fp)

Front = HiLoShellFrontController
front = Front.instancename

macros  = get_macros(Front, front)

init_script = [
    '-_RunPythonScript ResetEngine (',
    'import rhinoscriptsyntax as rs;',
    'import sys;',
    'import os;',
    'path = rs.ToolbarCollectionPath(\'{}\');'.format(front),
    'path = os.path.dirname(path);',
    'sys.path.insert(0, path);',
    'from {} import {};'.format('frontcontroller', Front.__name__),
    '{} = {}();'.format(front, Front.__name__),
    '{}.init();'.format(front),
    ')'
]

for macro in macros:
    if macro['name'] == '{}.init'.format(front):
        macro['script'] = ' '.join(init_script)

rui = Rui('./{}.rui'.format(front))

rui.init()
rui.add_macros(macros)

# for name in rui.macros:
#     print(name)

for toolbar in config['toolbars']:
    for item in toolbar['items']:
        itype = item.get('type')
        if itype == 'separator':
            continue
        if 'text' in item:
            name = item['left']
            element = rui.macros[name]
            element.find('button_text/locale_1033').text = item['text']

rui.add_menus(config['menus'])
rui.add_toolbars(config['toolbars'])
rui.add_toolbargroups(config['toolbargroups'])

rui.write()
