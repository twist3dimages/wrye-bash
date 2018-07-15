#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""a parser than reads the info.xml and ModuleConfig.xml of a fomod"""

import os

from lxml import etree

__author__ = "erri120"
__maintainer__ = "erri120"
__credits__ = ["erri120", "GandaG", "warmfrost85", "Utumno"]
__status__ = "Development"

class FomodInfo:
    """class that holds the infos of info.xml (easy)"""

    def __init__(self, mod_name):
        self.mod_name = mod_name
        self.mod_author = u''
        self.mod_version = u''
        self.mod_description = u''
        self.mod_website = u''

    @staticmethod
    def get_fomod_info(mod_name):
        """ this method will parse the whole info.xml file """
        info = FomodInfo(mod_name=mod_name)
        info_path = os.path.join(mod_name,'fomod/info.xml')
        if os.path.exists(info_path):
            with open(info_path) as info_file:
                # recover is True so that even 'broken' XML files get parsed
                parser = etree.XMLParser(recover=True)
                tree = etree.parse(info_file, parser)
                # <fomod> is the root element
                for node in tree.xpath('/fomod'):
                    info.mod_name = node.find('Name').text.rstrip()
                    if not node.find('Version') is None:
                        info.mod_version = node.find('Version').text.rstrip()
                    if not node.find('Author') is None:
                        info.mod_author = node.find('Author').text.rstrip()
                    if not node.find('Description') is None and not node.find(
                            'Description').text is None:
                        info.mod_description = node.find(
                            'Description').text.rstrip()
                    if not node.find('Website') is None:
                        info.mod_website = node.find('Website').text.rstrip()
        return info

"""
This is the structure of the installSteps in ModuleConfig.xml:
something in () means its an attribute and attributes/elements with =op are 
optional
attribute with something in [] means that the attribute is one of the things 
in []
# means it's a comment in a comment (ikr) 
... means it continues with the same pattern 

installSteps (order=op)
    installStep (name)
        visible=op
            flagDependency (flag, value)
        optionalFileGroups(order)
            group (name, type[SelectAtLeastOne,SelectAtMostOne,
            SelectExactlyOne,
                                SelectAll, SelectAny])
                plugins (order)
                    plugin (name)
                    #literaly everything after plugin is optional :(
                        description
                        image (path)
                        files
                            fileA (source, destination, priority, 
                            alwaysInstall,
                                    installIfUsable)
                            fileB
                            fileC
                        conditionFlag 
                            flag (name, value)
                        typeDescriptor
                            type (name)
                            dependencyType
                                defaultType (name)
                                patterns
                                    pattern
                                        dependencies (operator)
                                            fileDependencyA (file, state)
                                            flagDependency (flag, value)
                                            gameDependency (version)
                                            fommDependency (version)
                                            dependencies (operator)
                                                ...
                                        type (name)
    installStep(name)
        ...
conditionalFileInstalls
    patterns
        pattern
            dependencies
                flagDependency (flag, value)
            files
                fileA (source, destination, priority, alwaysInstall, 
                installIfUsable)
"""

def order_list(list_to_order, order):
    """ code by https://github.com/GandaG
    modified for usage within the parser """
    if order == 'Explicit':
        return list_to_order
    elif order == 'Ascending':
        reverse = False
    else:
        reverse = True
    if len(list_to_order) is not 0:
        if isinstance(list_to_order[0],FomodGroup):
            return sorted(list_to_order, key=lambda x: x.group_name,
                          reverse=reverse)
        elif isinstance(list_to_order[0],FomodPlugin):
            return sorted(list_to_order, key=lambda x: x.plugin_name,
                          reverse=reverse)
        else:
            return list_to_order


class FomodFile:
    """ the class that will hold info for every file/folder """

    def __init__(self):
        self.file_source = u''
        self.file_destination = u''
        self.file_always_install = u''
        self.file_install_if_usable = u''
        self.file_priority = 0


class FomodPlugin:
    """ class that hold every info about a plugin """

    def __init__(self):
        self.plugin_name = u''
        self.plugin_desc = u''
        self.plugin_image = u''
        self.plugin_file_list = []
        self.plugin_flag_map = {}
        self.plugin_type = u''

    def add_file(self, plugin_file):
        self.plugin_file_list.append(plugin_file)

    def add_flag(self, flag_name, flag_value):
        self.plugin_flag_map.update({flag_name: flag_value})

    def get_flag_value(self, flag_name):
        return self.plugin_flag_map.get(flag_name)

class FomodGroup:
    """ class that holds info on a group """

    def __init__(self):
        self.group_name = u''
        self.group_type = u''
        self.plugin_list = []
        self.plugin_order = u''

    def add_plugin(self, plugin):
        self.plugin_list.append(plugin)

class FomodStep:
    """ class that holds info on a step """

    def __init__(self):
        self.step_name = u''
        self.visibility_flag_map = {}
        self.group_list = []
        self.group_order = u''

    def add_group(self, group):
        self.group_list.append(group)

    def add_flag(self, flag_name, flag_value):
        self.visibility_flag_map.update({flag_name: flag_value})

    def flag_value(self, flag_name):
        return self.visibility_flag_map[flag_name]

class FomodPattern:
    """ class holds info on a pattern used for the conditionalFileInstalls"""

    def __init__(self):
        self.flag_map = {}
        self.file_list = []

    def add_file(self, value):
        if not value in self.file_list:
            self.file_list.append(value)

    def add_flag(self, flag_name, flag_value):
        self.flag_map.update({flag_name: flag_value})

    def get_flag_value(self, flag_name):
        return self.flag_map[flag_name]

class FomodConfig:
    """
    class that holds the infos of ModuleConfig.xml
    """

    def __init__(self):
        self.module_name = u''
        # this is a path to a header image
        # todo: actually show this somewhere (wish of warmfrost85)
        self.module_image = u''
        # a dependency that is made up of one or more dependencies. nice
        # todo: change this
        self.module_dependencies = u''
        # list of files/folders that are required
        # todo: fill this
        self.required_files = []
        # list of all steps
        self.install_steps = []
        # todo: comment
        self.conditional_pattern_list = []

    @staticmethod
    def get_fomod_config(mod_path):
        """ returns the config of a fomod """
        # we create a new config that we fill and return it at the end
        config = FomodConfig()
        # todo: detect fomod folder
        config_path = os.path.join(mod_path,'fomod/ModuleConfig.xml')
        if os.path.exists(config_path):
            with open(config_path) as config_file:
                # todo: custom parser
                tree = etree.parse(config_file)
                # <config> is the root element
                for node in tree.xpath('/config'):
                    config.module_name = node.find('moduleName').text
                    if node.find('moduleImage') is not None:
                        config.module_image = node.find('moduleImage').get('path')
                    # todo: required files
                    # conditional_pattern_list:
                    if node.find('conditionalFileInstalls') is not None:
                        for pattern in node.findall(
                                'conditionalFileInstalls/patterns/pattern'):
                            current_pattern = FomodPattern()
                            for pattern_flag in pattern.findall('dependencies/'
                                                                'flagDependency'):
                                if pattern_flag.get('flag') is not None \
                                        and pattern_flag.get('value') is not None:
                                    current_pattern.add_flag(
                                        pattern_flag.get('flag'),
                                        pattern_flag.get('value'))
                            # todo: check if izip can be used
                            for pattern_file in pattern.findall('files/file'):
                                current_file = FomodFile()
                                if pattern_file.get('source') is not None:
                                    current_file.file_source = \
                                        pattern_file.get(
                                        'source')
                                if pattern_file.get('destination') is not None:
                                    current_file.file_destination = \
                                        pattern_file.get(
                                        'destination')
                                if pattern_file.get('alwaysInstall') is not None:
                                    current_file.file_always_install = \
                                        pattern_file.get(
                                        'alwaysInstall')
                                if pattern_file.get('installIfUsable') is not None:
                                    current_file.file_install_if_usable = \
                                        pattern_file.get('installIfUsable')
                                if pattern_file.get('priority') is not None:
                                    current_file.file_priority = \
                                        pattern_file.get('priority')
                                current_pattern.add_file(current_file)
                            for pattern_folder in pattern.findall(
                                    'files/folder'):
                                current_file = FomodFile()
                                if pattern_folder.get('source') is not None:
                                    current_file.file_source = \
                                        pattern_folder.get('source')
                                if pattern_folder.get('destination') is not None:
                                    current_file.file_destination = \
                                        pattern_folder.get('destination')
                                if pattern_folder.get('alwaysInstall') is not None:
                                    current_file.file_always_install = \
                                        pattern_folder.get('alwaysInstall')
                                if pattern_folder.get('installIfUsable') is not None:
                                    current_file.file_install_if_usable = \
                                        pattern_folder.get('installIfUsable')
                                if pattern_folder.get('priority') is not None:
                                    current_file.file_priority = \
                                        pattern_folder.get('priority')
                                current_pattern.add_file(current_file)
                            config.conditional_pattern_list.append(
                                current_pattern)
                    # install steps:
                    for step in node.findall('installSteps/installStep'):
                        current_step = FomodStep()
                        current_step.step_name = step.get('name')
                        current_step.group_order = step.find('optionalFileGroups').get('order')
                        if step.find('visible') is not None:
                            for vis_flag in step.findall('visible/flagDependency'):
                                current_step.add_flag(vis_flag.get('flag'),
                                                      vis_flag.get('value'))
                        for group in step.findall('optionalFileGroups/group'):
                            current_group = FomodGroup()
                            current_group.group_name = group.get('name')
                            current_group.group_type = group.get('type')
                            current_group.group_order = group.find('plugins').get('order')
                            for plugin in group.findall('plugins/plugin'):
                                current_plugin = FomodPlugin()
                                current_plugin.plugin_name = plugin.get('name')
                                current_plugin.plugin_desc = plugin.find(
                                    'description').text
                                if plugin.find('image') is not None:
                                    current_plugin.plugin_image =\
                                        plugin.find('image').get('path')
                                if plugin.find('typeDescriptor/type') is not None:
                                    current_plugin.plugin_type = \
                                        plugin.find('typeDescriptor/type').get('name')
                                for plugin_file in plugin.findall('files/file'):
                                    current_file = FomodFile()
                                    if plugin_file.get('source') is not None:
                                        current_file.file_source =\
                                            plugin_file.get('source')
                                    if plugin_file.get('destination') is not None:
                                        current_file.file_destination =\
                                            plugin_file.get('destination')
                                    if plugin_file.get('alwaysInstall') is not None:
                                        current_file.file_always_install = \
                                            plugin_file.get('alwaysInstall')
                                    if plugin_file.get('installIfUsable') is not None:
                                        current_file.file_install_if_usable = \
                                            plugin_file.get('installIfUsable')
                                    if plugin_file.get('priority') is not None:
                                        current_file.file_priority = \
                                            plugin_file.get('priority')
                                    current_plugin.add_file(current_file)
                                for plugin_folder in plugin.findall('files/folder'):
                                    current_file = FomodFile()
                                    if plugin_folder.get('source') is not None:
                                        current_file.file_source = \
                                            plugin_folder.get('source')
                                    if plugin_folder.get('destination') is not None:
                                        current_file.file_destination =\
                                            plugin_folder.get('destination')
                                    if plugin_folder.get('alwaysInstall') is not None:
                                        current_file.file_always_install =\
                                            plugin_folder.get('alwaysInstall')
                                    if plugin_folder.get('installIfUsable') is not None:
                                        current_file.file_install_if_usable = \
                                            plugin_folder.get('installIfUsable')
                                    if plugin_folder.get('priority') is not None:
                                        current_file.file_priority =\
                                            plugin_folder.get('priority')
                                    current_plugin.add_file(current_file)
                                # todo: check for none
                                for plugin_flags in plugin.findall('conditionFlags/flag'):
                                    flag_name = plugin_flags.get('name')
                                    flag_value = plugin_flags.text
                                    current_plugin.add_flag(flag_name,
                                                            flag_value)
                                current_group.add_plugin(current_plugin)
                            if current_group.group_order is not None:
                                current_group.plugin_list = \
                                    order_list(current_group.plugin_list,
                                               current_group.group_order)
                            current_step.add_group(current_group)
                        if current_step.group_order is not None:
                            current_step.group_list = \
                                order_list(current_step.group_list,
                                           current_step.group_order)
                        config.install_steps.append(current_step)

        return config