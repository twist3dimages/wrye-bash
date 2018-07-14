#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""a GUI Fomod Installer that uses fomods.py as a Parser"""
from __future__ import print_function

import wx
import wx.lib.scrolledpanel

from fomods import FomodConfig, FomodInfo

__author__ = "erri120"
__maintainer__ = "erri120"
__credits__ = ["erri120", "GandaG", "warmfrost85", "Utumno", "calthrop",
               "Arthmoor", "Sharlikran", "BeermotorWB"]
__status__ = "Development"

TEST_FOLDER = '../../../fomod-test-folder/'

def get_all_files(config):
    """ function that is called on the last page when you press next """
    group_flag_map = {}
    print('Files from the plugin section:')
    for step_number, group_map in ALL_STEPS.iteritems():
        for group_name, group in group_map.iteritems():
            for group_file in group.file_list:
                if not group_file.file_source == '':
                    # FomodFile is the type of object that is in that list
                    FILES_LIST.append(group_file)
                    print('Source: \"'
                          + group_file.file_source
                          + '\", \n Destination: \"'
                          + group_file.file_destination
                          + '\"')
            # we put those flags into the local var we had at the beginning so
            # that the next step can extract the flags
            for flag_name, flag_value in group.flag_map.iteritems():
                if not flag_name == '':
                    group_flag_map.update({flag_name: flag_value})
    print('Files from the condition files section:')
    extra_files = config.conditional_pattern_list
    for pattern in extra_files:
        flag_map = pattern.flag_map
        for flag_name, flag_value in flag_map.iteritems():
            for group_flag_name, group_value in group_flag_map.iteritems():
                # the name and the value need to be the same
                if group_flag_name == flag_name:
                    if flag_value == group_value:
                        for flag_file in pattern.file_list:
                            FILES_LIST.append(flag_file)
                            print('Source: \"'
                                  + flag_file.file_source
                                  + '\", \n Destination: \"'
                                  + flag_file.file_destination
                                  + '\"')

class InstallerGroup:
    """this class is used to store the data needed for the gui installation"""
    def __init__(self):
        self.group_name = u''
        self.box_map = {}
        self.group_type = u''
        self.element_map = {}
        self.plugin_list = []
        self.flag_map = {}
        self.file_list = []

    def flag_value(self, flag):
        return self.flag_map[flag]

    def add_plugin(self, plugin):
        if not plugin in self.plugin_list:
            self.plugin_list.append(plugin)

    def add_element(self, element, element_name):
        if not element_name in self.element_map.keys():
            self.element_map.update({u'' + element_name: element})

    def get_element(self, element_name):
        if element_name in self.element_map.keys():
            return self.element_map[element_name]

    def get_box_value(self, plugin_name):
        return self.box_map[plugin_name]

    def update_box_value(self, key, value):
        """ this function updates the value of a checkbox """
        self.box_map.update({key: value})

    def update_radio_value(self, key, value, first_in_group):
        """
        this function updates the value of radio button
        when you click a radio button the other are turned False so the map
        changes the value of every other key to False
        if the button is the first in a group (see construct_step) than we
        don't need to change the other buttons because first in group means
        there is no other button in the map
        """
        if value is False or first_in_group:
            self.box_map.update({key: value})
        else:
            for _key, _value in self.box_map.iteritems():
                self.box_map.update({_key: False})
            self.box_map.update({key: value})

    def change_other_elements(self, change_to, exclude):
        """
        the SelectAtMostOne type means we can have 0 or 1 box checked, when one
        box turns True we set every other box False; not only the value in our
        map but the actual element in the frame
        """
        for element_name in self.element_map.keys():
            if not element_name == exclude:
                self.element_map[element_name].SetValue(change_to)
                self.update_box_value(element_name, change_to)

    def update_flags(self, plugin_name, at_most_true):
        """
        when you select a plugin we also need to update the flags that are
        being set
        """
        for plugin in self.plugin_list:
            if plugin.plugin_name == plugin_name:
                plugin_flag_map = plugin.plugin_flag_map
                # this one is a bit complex:
                # SelectExactlyOne, SelectAll, SelectAtMostOne all need to
                # have their flag map deleted
                if self.group_type == 'SelectExactlyOne' or self.group_type \
                        == 'SelectAll' or self.group_type == 'SelectAtMostOne':
                    self.flag_map.clear()
                    # at_most_true is an arg to check if the checkbox is True
                    # if it's True than we need to add the flags form the
                    # plugin if it's turned off, we just delete the list
                    # like above
                    if at_most_true or self.group_type == 'SelectExactlyOne' \
                            or self.group_type == 'SelectAll':
                        for plugin_flag in plugin_flag_map.keys():
                            self.flag_map.update(
                                {plugin_flag: plugin_flag_map[plugin_flag]})
                else:
                    for plugin_flag in plugin_flag_map.keys():
                        if not plugin_flag in self.flag_map.keys():
                            self.flag_map.update(
                                {plugin_flag: plugin_flag_map[plugin_flag]})
                        else:
                            # if it's already there than the user turned it off
                            del self.flag_map[plugin_flag]

    def update_files(self, plugin_name):
        for plugin in self.plugin_list:
            if plugin.plugin_name == plugin_name:
                if self.group_type == 'SelectExactlyOne' or self.group_type \
                        == 'SelectAll' or self.group_type == 'SelectAtMostOne':
                    del self.file_list[:]
                plugin_files = plugin.plugin_file_list
                for plugin_file in plugin_files:
                    if not plugin_file in self.file_list:
                        self.file_list.append(plugin_file)


class FomodInstallerFrame(wx.Frame):
    """ the frame that is used for the installer """

    def add_group(self, group):
        self.group_map.update({group.group_name: group})

    def construct_step(self, parent, step_number):
        """ the function that will literally construct the step we need """
        # getting the current step
        step = self.install_steps[step_number]
        # getting the groups
        group_list = step.group_list
        # create all panels
        main_panel = wx.Panel(parent)
        content_panel = wx.Panel(main_panel)
        button_panel = wx.Panel(main_panel)
        header_panel = wx.Panel(content_panel)
        column_panel = wx.Panel(content_panel)
        # a scrolled panel so we can scroll through all the groups
        left_panel = wx.lib.scrolledpanel.ScrolledPanel(column_panel)
        left_panel.SetupScrolling()
        right_panel = wx.Panel(column_panel)
        # the fonts I used, todo: make globally/change to wrye-bash font
        normal_font = wx.Font(14, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        header_font = wx.Font(20, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        # create all sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        column_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_column_sizer = wx.BoxSizer(wx.VERTICAL)
        right_column_sizer = wx.BoxSizer(wx.VERTICAL)

        # todo: all hardcoded text needs to be changed for different languages
        # create all elements:
        # the buttons:
        next_button = wx.Button(button_panel, label='Next')
        back_button = wx.Button(button_panel, label='Back')

        # elements for the right column:
        desc_text = wx.TextCtrl(right_panel,
                                value='click on any plugin to view the '
                                      'description', id=wx.ID_ANY,
                                style=wx.TE_MULTILINE | wx.TE_READONLY)
        desc_text.SetFont(normal_font)
        # a placeholder
        placeholder_png = wx.Image('../images/fomod_gui_placeholder.png',
                                   wx.BITMAP_TYPE_ANY)
        placeholder_png = placeholder_png.Scale(200, 200)
        image = wx.StaticBitmap(right_panel, wx.ID_ANY,
                                wx.BitmapFromImage(placeholder_png),
                                (200, 200))
        image.Bind(wx.EVT_LEFT_DCLICK, self.bitmap_double_click)

        # we do this to easily access the elements when we need to update them
        self.description = desc_text
        self.image = image

        # elements for the header:
        header_text = wx.TextCtrl(header_panel, value=self.mod_name,
                                  id=wx.ID_ANY,
                                  style=wx.TE_MULTILINE | wx.TE_READONLY)
        header_text.SetFont(header_font)

        # elements for the left column:
        for group in group_list:
            # create a panel and a sizer to store the elements in a proper
            # layout
            group_panel = wx.Panel(left_panel, name=group.group_name)
            group_sizer = wx.BoxSizer(wx.VERTICAL)
            # group name will look like this:
            # MyGroup (SomeType)
            group_name = wx.TextCtrl(group_panel,
                                     value=group.group_name + ' (' + group.group_type + ')',
                                     id=wx.ID_ANY,
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)
            group_name.SetFont(normal_font)
            group_sizer.Add(group_name, 0, wx.EXPAND, 7)
            # if we go back, we get already have all the data stored in the map
            if self.go_back:
                install_group = self.group_map[group.group_name]
            # if we don't go back, we create a new group and start to store the
            # data
            else:
                install_group = InstallerGroup()
                install_group.group_name = group.group_name
                install_group.group_type = group.group_type
            plugin_list = group.plugin_list
            for plugin in plugin_list:
                plugin_name = plugin.plugin_name
                if not self.go_back:
                    install_group.add_plugin(plugin)
                # we need to differentiate between the different types
                if group.group_type == 'SelectExactlyOne':
                    # exactly one means that one radio button is already True
                    # when you load the page, also a first radio button of a
                    # group needs to have a special style which is why I
                    # checked if the plugin is the first one
                    if plugin_list.index(plugin) == 0:
                        group_radiobutton = wx.RadioButton(group_panel,
                                                           wx.ID_ANY,
                                                           label=plugin_name,
                                                           style=wx.RB_GROUP)
                        if not self.go_back:
                            install_group.update_radio_value(plugin_name, True,
                                                             True)
                            install_group.update_flags(plugin_name, False)
                            install_group.update_files(plugin_name)
                        else:
                            group_radiobutton.SetValue(
                                install_group.get_box_value(plugin_name))
                    else:
                        group_radiobutton = wx.RadioButton(group_panel,
                                                           wx.ID_ANY,
                                                           label=plugin_name)
                        if not self.go_back:
                            install_group.update_radio_value(plugin_name,
                                                             False, False)
                        else:
                            group_radiobutton.SetValue(
                                install_group.get_box_value(plugin_name))
                    group_radiobutton.SetFont(normal_font)
                    self.Bind(wx.EVT_RADIOBUTTON, self.radio_button_handler,
                              group_radiobutton)
                    group_sizer.Add(group_radiobutton, 0, wx.EXPAND)
                elif group.group_type == 'SelectAll':
                    # select all is a bit funny because it's often only one
                    # plugin that needs to be installed so I used a single
                    # radio button that needs to be always True
                    group_radiobutton = wx.RadioButton(group_panel, wx.ID_ANY,
                                                       label=plugin_name,
                                                       style=wx.RB_SINGLE)
                    group_radiobutton.SetValue(True)
                    group_radiobutton.SetFont(normal_font)
                    # this is always True so I don't need to change anything if
                    # we go back
                    install_group.update_radio_value(plugin_name, True, True)
                    install_group.update_flags(plugin_name, False)
                    install_group.update_files(plugin_name)
                    self.Bind(wx.EVT_RADIOBUTTON, self.radio_button_handler,
                              group_radiobutton)
                    group_sizer.Add(group_radiobutton, 0, wx.EXPAND)
                elif group.group_type == 'SelectAtMostOne':
                    # at most one means you can select 0 plugins or 1 plugin
                    group_checkbox = wx.CheckBox(group_panel, wx.ID_ANY,
                                                 label=plugin_name)
                    group_checkbox.SetFont(normal_font)
                    if not self.go_back:
                        install_group.update_box_value(plugin_name, False)
                        install_group.add_element(group_checkbox, plugin_name)
                    else:
                        group_checkbox.SetValue(
                            install_group.get_box_value(plugin_name))
                    self.Bind(wx.EVT_CHECKBOX, self.check_box_handler,
                              group_checkbox)
                    group_sizer.Add(group_checkbox, 0, wx.EXPAND)
                else:
                    # todo: change this and add other types if needed
                    group_checkbox = wx.CheckBox(group_panel, wx.ID_ANY,
                                                 label=plugin_name)
                    group_checkbox.SetFont(normal_font)
                    if not self.go_back:
                        install_group.update_box_value(plugin_name, False)
                    else:
                        group_checkbox.SetValue(
                            install_group.get_box_value(plugin_name))
                    self.Bind(wx.EVT_CHECKBOX, self.check_box_handler,
                              group_checkbox)
                    group_sizer.Add(group_checkbox, 0,
                                    wx.EXPAND)  # this loop and  #  #   #  #
                    #  if..elif..else structure can be changed maybe..  #  #
                    #  comment if you know something :)

            group_panel.SetSizer(group_sizer)
            left_column_sizer.Add(group_panel, 1, wx.EXPAND)
            if not self.go_back:
                self.add_group(install_group)

        # adding all elements to their sizer:
        # adding the buttons:
        button_sizer.Add(back_button, 1, wx.EXPAND)
        button_sizer.Add(next_button, 1, wx.EXPAND)
        # adding the right column elements:
        right_column_sizer.Add(desc_text, 1, wx.EXPAND)
        right_column_sizer.Add(image, 1, wx.EXPAND)
        # adding the header elements:
        header_sizer.Add(header_text, 1, wx.EXPAND)

        # give all panels their sizer
        left_panel.SetSizer(left_column_sizer)
        right_panel.SetSizer(right_column_sizer)
        header_panel.SetSizer(header_sizer)
        column_panel.SetSizer(column_sizer)
        button_panel.SetSizer(button_sizer)
        content_panel.SetSizer(content_sizer)
        column_sizer.Add(left_panel, 1, wx.EXPAND)
        column_sizer.Add(right_panel, 1, wx.EXPAND)
        content_sizer.Add(header_panel, 1, wx.EXPAND)
        content_sizer.Add(column_panel, 9, wx.EXPAND)
        main_sizer.Add(content_panel, 9, wx.EXPAND)
        main_sizer.Add(button_panel, 0, wx.EXPAND)
        main_panel.SetSizer(main_sizer, wx.EXPAND)

        # bind the event for the buttons
        self.Bind(wx.EVT_BUTTON, self.next_button_handler, next_button)
        self.Bind(wx.EVT_BUTTON, self.back_button_handler, back_button)

        main_panel.Show()

    def __init__(self, parent, config, mod_name, mod_path, install_steps,
                 testing, step_number, pos, size, title, go_back):
        # this needs a good amount of arguments
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=title, pos=pos,
                          size=size,
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER |
                                wx.TAB_TRAVERSAL)
        # putting the args into variables
        self.testing = testing
        self.config = config
        self.title = title
        self.install_steps = install_steps
        self.mod_name = mod_name
        self.mod_path = mod_path
        self.size_x, self.size_y = size
        self.pos_x, self.pos_y = pos
        self.step_number = step_number
        # this boolean will be used to check if we need to recreate the last
        # state or if we just create every thing new
        self.go_back = go_back

        # key is a group name as a String, value is a InstallerGroup
        # this is needed for the buttons
        self.group_map = {}
        # if we need to recreate the last step, we get our data from the
        # all_steps map
        if self.go_back:
            self.group_map = ALL_STEPS[str(step_number)]

        # this will be needed to get the plugin that is selected (check
        # DClick on bitmap
        self.selected_plugin = None

        # max size for pictures in the DClick frame
        self.picture_max_size = 800

        # this is needed to access the description and the image later on
        self.description, self.image = None, None

        if not testing:
            self.Bind(wx.EVT_CLOSE, self.close_window)

        # method to construct all elements, I didn't want the init to be so
        # lengthy
        self.construct_step(parent=self, step_number=step_number)
        self.Show()
        # the first page should be in the center
        if self.step_number == 0:
            self.Centre()

    def get_group(self, group_name):
        if group_name in self.group_map:
            return self.group_map[group_name]

    def bitmap_double_click(self, event):
        """ creating a new frame when the image is clicked """
        # first check if we actually selected a plugin and if that has an image
        if self.selected_plugin is not None:
            if not self.selected_plugin.plugin_image == '':
                # create the frame
                frame = wx.Frame(parent=None, id=wx.ID_ANY, title='',
                                 size=wx.Size(),
                                 style=wx.DEFAULT_FRAME_STYLE ^
                                       wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)
                image_raw = wx.Image(
                    self.mod_path + '/' + self.selected_plugin.plugin_image,
                    wx.BITMAP_TYPE_ANY)
                # here is the fun part:
                # we check if the width or the height is smaller than 800
                # if it's bigger, we change the width or height so that it will
                # be either 800 in width or 800 in height and it keeps the
                # aspect ratio
                width = image_raw.GetWidth()
                height = image_raw.GetHeight()
                if width < self.picture_max_size or height < self.picture_max_size:
                    new_width = width
                    new_height = height
                else:
                    if width > height:
                        new_width = self.picture_max_size
                        new_height = self.picture_max_size * height / width
                    else:
                        new_height = self.picture_max_size
                        new_width = self.picture_max_size * width / height
                image_raw = image_raw.Scale(new_width, new_height)
                bitmap = wx.StaticBitmap(frame, wx.ID_ANY,
                                         wx.BitmapFromImage(image_raw))
                frame.SetSize(wx.Size(new_width, new_height))
                frame.Show()
                frame.Centre()

    def update_resources(self, group, label):
        """
        we update the description and the image based on what plugin
        was selected
        """
        for plugin in group.plugin_list:
            if plugin.plugin_name == label:
                self.selected_plugin = plugin
                if not plugin.plugin_desc == '':
                    self.description.SetValue(plugin.plugin_desc)
                # todo: when a new picture is loaded the picture 'glitches'
                if not plugin.plugin_image == '':
                    image_raw = wx.Image(
                        self.mod_path + '/' + plugin.plugin_image,
                        wx.BITMAP_TYPE_ANY)
                    image_raw = image_raw.Scale(200, 200)
                    self.image.SetBitmap(wx.BitmapFromImage(image_raw))
                if plugin.plugin_image == '':
                    placeholder_png = wx.Image(TEST_FOLDER + 'placeholder.png',
                                               wx.BITMAP_TYPE_ANY)
                    placeholder_png = placeholder_png.Scale(200, 200)
                    self.image.SetBitmap(wx.BitmapFromImage(placeholder_png))

    def radio_button_handler(self, event):
        """ handler for the wx.EVT_RADIOBUTTON event """
        event_object = event.GetEventObject()
        group = self.get_group(str(event_object.GetParent().GetName()))
        group.update_radio_value(event_object.GetLabel(),
                                 event_object.GetValue(), False)
        group.update_flags(event_object.GetLabel(), False)
        group.update_files(event_object.GetLabel())
        self.add_group(group)
        self.update_resources(group, event_object.GetLabel())

    def check_box_handler(self, event):
        """ handler for the wx.EVT_CHECKBOX event """
        event_object = event.GetEventObject()
        group = self.get_group(str(event_object.GetParent().GetName()))
        if group.group_type == 'SelectAtMostOne' and event_object.GetValue()\
                is True:
            group.change_other_elements(change_to=False,
                                        exclude=event_object.GetLabel())
            group.update_flags(event_object.GetLabel(), True)
        else:
            group.update_flags(event_object.GetLabel(), False)
        group.update_box_value(event_object.GetLabel(),
                               event_object.GetValue())
        group.update_files(event_object.GetLabel())

        self.add_group(group)
        self.update_resources(group, event_object.GetLabel())

    def back_button_handler(self, event):
        """ the handler for the back button """
        if self.step_number > 0:
            self.pos_x, self.pos_y = self.GetPosition()
            # we got manners, we clean up before we go
            self.DestroyChildren()
            self.Destroy()
            # recreating the last frame
            all_step_keys = ALL_STEPS.keys()  # 0 1
            all_step_keys.append(str(self.step_number))
            old_step_number = int(
                all_step_keys[all_step_keys.index(str(self.step_number)) - 1])
            FomodInstallerFrame(parent=None, config=self.config,
                                mod_name=self.mod_name,
                                mod_path=self.mod_path,
                                install_steps=self.install_steps,
                                testing=self.testing,
                                step_number=old_step_number,
                                pos=(self.pos_x, self.pos_y),
                                size=(self.size_x, self.size_y),
                                title=self.title, go_back=True)
        else:
            if not self.testing:
                box = wx.MessageDialog(None, 'This is the first page!',
                                       'Error', wx.CANCEL)
                answer = box.ShowModal()
                if answer == wx.ID_ANY:
                    box.Destroy()

    def next_button_handler(self, event):
        """ the handler for the next button """
        if self.testing:
            print('[=== Now listing all Groups ===]')
            for group_name, group in self.group_map.iteritems():
                print(' - ' + group_name + ' - ')
                print('[Keys]')
                if not group.box_map:
                    for key, value in group.box_map.iteritems():
                        print('Key: ' + str(key) + ', Value: ' + str(value))
                else:
                    print('No keys were set')
                print('[Flags]')
                if not group.flag_map:
                    for flag, flag_value in group.flag_map.iteritems():
                        print('Flag: ' + str(flag) + ', Value: ' + str(
                            flag_value))
                else:
                    print('No Flags were set')
        # onto the real function:
        # before we create the next frame, we need to store the settings we
        # made into the all_steps map
        ALL_STEPS.update({str(self.step_number): self.group_map})
        # first we need to check if we're the last page
        # notice that we check if the current step number is smaller than
        # the length of our list with all steps -1; MINUS ONE because:
        # later/earlier(technically) in the constructStep function:
        # step = self.install_steps[step_number]
        # meaning that if the length is 10 and we try to get the step at the
        # index of 10, we try to get the eleventh step because arrays/lists
        # start at 0 :)
        if self.step_number < len(self.install_steps) - 1:
            # we need to check for the visibility flags on the next step:
            # some vars that will help us later
            found_next = False
            count = 1
            # a while loop because we need to check if we're allowed to see the
            # next page, if the next page needs flags we don't have set, we
            # skip it. This is to continue until we found the next step we are
            # allowed to see
            while found_next is False:
                # getting the data of the next step:
                next_step = self.install_steps[self.install_steps.index(
                    self.install_steps[self.step_number]) + count]
                next_flag_map = next_step.visibility_flag_map
                # we check if one of our set flags is in the map
                # and than check if the value (on or off) is also the same
                # by doing so we get a number of flags (length of
                # next_flag_map) that need to be set and a number of flags we
                # already have (found)
                needed_len = len(next_flag_map)
                found = 0
                for group_name, group in self.group_map.iteritems():
                    for flag, flag_value in group.flag_map.iteritems():
                        if flag in next_flag_map:
                            if next_flag_map[flag] == flag_value:
                                found = found + 1
                # if every value of every flag that we need for the next step
                # is already been set we can create the next frame
                if needed_len == found:
                    # set the position variables = to the current position
                    self.pos_x, self.pos_y = self.GetPosition()
                    # we got manners, we clean up before we go
                    self.DestroyChildren()
                    self.Destroy()
                    FomodInstallerFrame(parent=None, config=self.config,
                                        mod_name=self.mod_name,
                                        mod_path=self.mod_path,
                                        install_steps=self.install_steps,
                                        testing=self.testing,
                                        step_number=self.step_number + count,
                                        pos=(self.pos_x, self.pos_y),
                                        size=(self.size_x, self.size_y),
                                        title=self.title, go_back=False)
                    # exit the while loop
                    found_next = True
                    break
                # if the next step is not the one we need, we'll continue to
                # search
                else:
                    # check if this is the last page
                    if count + 1 + self.step_number == len(self.install_steps):
                        get_all_files(config=self.config)
                        if not self.testing:
                            box = wx.MessageDialog(None,
                                                   'This is the last page!',
                                                   'Error', wx.CANCEL)
                            answer = box.ShowModal()
                            if answer == wx.ID_ANY:
                                box.Destroy()
                                break
                        break
                    else:
                        count = count + 1
        # if we are the last page we are giving a warning
        else:
            get_all_files(config=self.config)
            if not self.testing:
                box = wx.MessageDialog(None, 'This is the last page!', 'Error',
                                       wx.CANCEL)
                answer = box.ShowModal()
                if answer == wx.ID_ANY:
                    box.Destroy()

    def close_window(self, event):
        box = wx.MessageDialog(None, 'Do you want to exit?', 'Confirmation',
                               wx.YES_NO)
        answer = box.ShowModal()
        box.Destroy()
        if answer == wx.ID_YES:
            self.DestroyChildren()
            self.Destroy()

class FomodInstaller:
    # testing arg is used to not show any dialogs like (do you want to exit)
    def __init__(self, mod_name, mod_path, testing, size_x, size_y):
        # before everything else, we need to check if the list of files is null
        if len(FILES_LIST) is not 0:
            del FILES_LIST[:]
        if len(ALL_STEPS) is not 0:
            ALL_STEPS.clear()
        # putting the args into variables
        self.testing = testing
        self.size_x = size_x
        self.size_y = size_y
        self.title = u'Fomod Installer GUI by erri120'
        app = wx.App()
        # getting the data from info.xml
        self.info = FomodInfo(mod_name).get_fomod_info(mod_path)
        # getting the data from ModuleConfig.xml
        self.config = FomodConfig().get_fomod_config(mod_path)
        # adjusting the mod name to the one found in info.xml
        self.mod_name = self.info.mod_name
        self.mod_path = mod_path
        # getting the list of all steps
        self.install_steps = self.config.install_steps

        # creating the start frame (step number = 0)
        start_frame = FomodInstallerFrame(parent=None, config=self.config,
                                          mod_name=self.mod_name,
                                          mod_path=self.mod_path,
                                          install_steps=self.install_steps,
                                          testing=self.testing, step_number=0,
                                          pos=(0, 0),
                                          size=(self.size_x, self.size_y),
                                          title=self.title, go_back=False)

        # the whole program needs to return a list of files to install
        # starting the main loop
        app.MainLoop()

FILES_LIST = []
# key: the step number as String, value: the map of all groups from that step
ALL_STEPS = {}
FomodInstaller(mod_name='test', mod_path=TEST_FOLDER + 'test_subject06/',
               testing=True, size_x=600, size_y=500)