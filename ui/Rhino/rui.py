from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json
import inspect

import uuid
from xml.etree import ElementTree as ET
from xml.dom import minidom

import compas


HERE = os.path.abspath(os.path.dirname(__file__))


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = [
    'get_methods',
    'get_macros',
    'get_method_docstring',
    'get_method_oneliner',
    'get_public_methods',
    'find_macro',
    'Rui',
]


TPL_RUI = """<?xml version="1.0" encoding="utf-8"?>
<RhinoUI major_ver="2"
         minor_ver="0"
         guid="{0}"
         localize="False"
         default_language_id="1033">
    <extend_rhino_menus>
        <menu guid="{1}">
          <text>
            <locale_1033>Extend Rhino Menus</locale_1033>
          </text>
        </menu>
    </extend_rhino_menus>
    <menus />
    <tool_bar_groups />
    <tool_bars />
    <macros />
    <bitmaps>
        <small_bitmap item_width="16" item_height="16">
          <bitmap>iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6Q
AAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAATSURBVDhPYxgFo2AUjAIwYGAAAA
QQAAGnRHxjAAAAAElFTkSuQmCCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==</bitmap>
        </small_bitmap>
        <normal_bitmap item_width="24" item_height="24">
          <bitmap>iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6Q
AAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAYSURBVEhL7cEBAQAAAIIg/6+uIU
AAAFwNCRgAAdACW14AAAAASUVORK5CYIIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==</bitmap>
        </normal_bitmap>
        <large_bitmap item_width="32" item_height="32">
          <bitmap>iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6Q
AAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAaSURBVFhH7cEBAQAAAIIg/69uSE
AAAADAuRoQIAABnXhJQwAAAABJRU5ErkJgggAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==</bitmap>
        </large_bitmap>
    </bitmaps>
    <scripts />
</RhinoUI>
"""

TPL_MACRO = """
<macro_item guid="{0}">
    <text>
        <locale_1033>{1[name]}</locale_1033>
    </text>
    <script>{1[script]}</script>
    <tooltip>
        <locale_1033>{1[tooltip]}</locale_1033>
    </tooltip>
    <help_text>
        <locale_1033>{1[help_text]}</locale_1033>
    </help_text>
    <button_text>
        <locale_1033>{1[button_text]}</locale_1033>
    </button_text>
    <menu_text>
        <locale_1033>{1[menu_text]}</locale_1033>
    </menu_text>
</macro_item>
"""

TPL_MENUITEM = """
<menu_item guid="{0}" item_type="normal">
    <macro_id>{1}</macro_id>
</menu_item>
"""

TPL_MENUSEPARATOR = """
<menu_item guid="{0}" item_type="separator"></menu_item>
"""

TPL_TOOLBARITEM = """
<tool_bar_item guid="{0}" button_display_mode="control_only" button_style="normal">
    <left_macro_id>{1}</left_macro_id>
    <right_macro_id>{2}</right_macro_id>
</tool_bar_item>
"""

TPL_TOOLBARSEPARATOR = """
<tool_bar_item guid="{0}" button_display_mode="control_only" button_style="spacer">
</tool_bar_item>
"""

TPL_TOOLBAR = """
<tool_bar guid="{0}" item_display_style="{2[item_display_style]}">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
</tool_bar>
"""

TPL_TOOLBARGROUP = """
<tool_bar_group guid="{0}"
                dock_bar_guid32=""
                dock_bar_guid64=""
                active_tool_bar_group=""
                single_file="{2[single_file]}"
                hide_single_tab="{2[hide_single_tab]}"
                point_floating="0,0">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
</tool_bar_group>
"""

TPL_TOOLBARGROUPITEM = """
<tool_bar_group_item guid="{0}" major_version="1" minor_version="1">
    <text>
        <locale_1033>{1}</locale_1033>
    </text>
    <tool_bar_id>{2}</tool_bar_id>
</tool_bar_group_item>
"""


# ==============================================================================
# helpers
# ==============================================================================


def get_method_docstring(obj):
    return inspect.getdoc(obj)


def get_method_oneliner(obj):
    docstring = get_method_docstring(obj)
    if not docstring:
        return
    parts = docstring.trim().split('\n')
    return parts[0]


def get_methods(obj, bysource=False):
    if compas.PY3:
        methods = inspect.getmembers(obj, inspect.isfunction)
    else:
        methods = inspect.getmembers(obj, inspect.ismethod)
    return methods


def get_public_methods(obj):
    methods = get_methods(obj)
    return [method for method in methods if not method[0].startswith('_')]


def get_macros(controller, instance_name):
    methods = get_public_methods(controller)
    macros  = []
    for name, method in methods:
        script      = '-_RunPythonScript ({0}.{1}())'.format(instance_name, name)
        tooltip     = get_method_oneliner(method)
        help_text   = get_method_docstring(method)
        button_text = name
        menu_text   = ' '.join(name.split('_'))
        macros.append({
            'name'        : instance_name + '.' + name,
            'script'      : script,
            'tooltip'     : tooltip,
            'help_text'   : help_text,
            'button_text' : button_text,
            'menu_text'   : menu_text,
        })
    return macros


def find_macro(macros, name):
    for macro in macros:
        if macro['name'] == name:
            return macro


# ==============================================================================
# File support
# ==============================================================================


class Rui(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self.macros = {}
        self.toolbars = {}
        self.xml = None
        self.root = None
        self.root_macros = []
        self.root_menus = []
        self.root_toolbargroups = []
        self.root_toolbars = []
        self.check()

    def check(self):
        if not os.path.exists(os.path.dirname(self.filepath)):
            try:
                os.makedirs(os.path.dirname(self.filepath))
            except OSError as e:
                if e.errno != os.errno.EEXIST:
                    raise e
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w+'):
                pass

    def init(self):
        with open(self.filepath, 'w+') as f:
            f.write(TPL_RUI.format(uuid.uuid4(), uuid.uuid4()))
        self.xml                = ET.parse(self.filepath)
        self.root               = self.xml.getroot()
        self.root_macros        = self.root.find('macros')
        self.root_menus         = self.root.find('menus')
        self.root_toolbargroups = self.root.find('tool_bar_groups')
        self.root_toolbars      = self.root.find('tool_bars')

    def write(self):
        for name in self.macros:
            element = self.macros[name]
            self.root_macros.append(element)

        root = ET.tostring(self.root)
        xml = minidom.parseString(root).toprettyxml(indent="  ")
        xml = '\n'.join([line for line in xml.split('\n') if line.strip()])

        with open(self.filepath, 'wb+') as fh:
            fh.write(xml.encode('utf-8'))

    # --------------------------------------------------------------------------
    # add macros
    # --------------------------------------------------------------------------

    def add_macros(self, macros):
        for macro in macros:
            guid  = str(uuid.uuid4())
            s_macro = TPL_MACRO.format(guid, macro)
            e_macro = ET.fromstring(s_macro)
            self.macros[macro['name']] = e_macro

    # --------------------------------------------------------------------------
    # add menus
    # --------------------------------------------------------------------------

    def add_menus(self, menus):
        for menu in menus:
            self.add_menu(menu)

    def add_menu(self, menu, root=None):
        if root is None:
            root = self.root_menus
        e_menu = ET.SubElement(root, 'menu')
        e_menu.set('guid', str(uuid.uuid4()))
        e_text        = ET.SubElement(e_menu, 'text')
        e_locale      = ET.SubElement(e_text, 'locale_1033')
        e_locale.text = menu['name']
        for item in menu['items']:
            itype = item.get('type')
            if itype == 'separator':
                self.add_menuseparator(e_menu)
                continue
            if itype == 'submenu':
                self.add_menu(item, root=e_menu)
                continue
            e_macro = self.macros[item['macro']]
            macro_guid = e_macro.attrib['guid']
            self.add_menuitem(e_menu, macro_guid)
            continue

    def add_menuitem(self, root, macro_id):
        guid   = uuid.uuid4()
        s_item = TPL_MENUITEM.format(guid, macro_id)
        e_item = ET.fromstring(s_item)
        root.append(e_item)

    def add_menuseparator(self, root):
        guid  = uuid.uuid4()
        s_sep = TPL_MENUSEPARATOR.format(guid)
        e_sep = ET.fromstring(s_sep)
        root.append(e_sep)

    # --------------------------------------------------------------------------
    # add toolbars
    # --------------------------------------------------------------------------

    def add_toolbars(self, toolbars):
        for toolbar in toolbars:
            self.add_toolbar(toolbar)

    def add_toolbar(self, toolbar):
        options = {
            'item_display_style': 'text_only'
        }
        guid = uuid.uuid4()
        s_tb = TPL_TOOLBAR.format(guid, toolbar['name'], options)
        e_tb = ET.fromstring(s_tb)
        self.root_toolbars.append(e_tb)
        self.toolbars[toolbar['name']] = e_tb
        for item in toolbar['items']:
            itype = item.get('type')
            if itype == 'separator':
                self.add_toolbarseparator(e_tb)
                continue
            left_guid = None
            left_macro = item.get('left')
            if left_macro:
                e_left = self.macros[left_macro]
                left_guid = e_left.attrib['guid']
            right_guid = None
            right_macro = item.get('right')
            if right_macro:
                e_right    = self.macros[right_macro]
                right_guid = e_right.attrib['guid']
            self.add_toolbaritem(e_tb, left_guid, right_guid)

    def add_toolbaritem(self, root, left_macro_id, right_macro_id):
        guid   = uuid.uuid4()
        s_item = TPL_TOOLBARITEM.format(guid, left_macro_id, right_macro_id)
        e_item = ET.fromstring(s_item)
        root.append(e_item)

    def add_toolbarseparator(self, root):
        guid  = uuid.uuid4()
        s_sep = TPL_TOOLBARSEPARATOR.format(guid)
        e_sep = ET.fromstring(s_sep)
        root.append(e_sep)

    # --------------------------------------------------------------------------
    # add toolbargroups
    # --------------------------------------------------------------------------

    def add_toolbargroups(self, toolbargroups):
        for tbg in toolbargroups:
            self.add_toolbargroup(tbg)

    def add_toolbargroup(self, tbg):
        options = {
            'single_file'     : 'False',
            'hide_single_tab' : 'False',
        }
        guid  = uuid.uuid4()
        s_tbg = TPL_TOOLBARGROUP.format(guid, tbg['name'], options)
        e_tbg = ET.fromstring(s_tbg)
        self.root_toolbargroups.append(e_tbg)
        for tb_name in tbg['toolbars']:
            e_tb    = self.toolbars[tb_name]
            tb_guid = e_tb.attrib['guid']
            self.add_toolbargroupitem(e_tbg, tb_name, tb_guid)

    def add_toolbargroupitem(self, root, tb_name, tb_guid):
        guid   = uuid.uuid4()
        s_item = TPL_TOOLBARGROUPITEM.format(guid, tb_name, tb_guid)
        e_item = ET.fromstring(s_item)
        root.append(e_item)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    pass
