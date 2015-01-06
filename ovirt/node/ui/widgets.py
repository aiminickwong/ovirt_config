#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# widgets.py - Copyright (C) 2012 Red Hat, Inc.
# Written by Fabian Deutsch <fabiand@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.  A copy of the GNU General Public License is
# also available at http://www.gnu.org/copyleft/gpl.html.

"""
Widgets for oVirt Node's urwid TUI
"""
import urwid
import logging

LOGGER = logging.getLogger(__name__)


class SelectableText(urwid.Text):
    """A Text widget that can be selected to be highlighted
    """
    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class TableEntryWidget(urwid.AttrMap):
    """An entry in a table
    """
    _text = None

    signals = ["activate"]

    def __init__(self, title):
        self._text = SelectableText(title)
#        self._text = Button(title)
#        self._text.button_left = ""
#        self._text.button_right = ""
        super(TableEntryWidget, self).__init__(self._text, 'table.entry',
                                                           'table.entry:focus')

    def keypress(self, size, key):
        if urwid.Button._command_map[key] == 'activate':
            self._emit('activate', None)
        return key

    def mouse_event(self, size, event, button, x, y, focus):
        if button != 1 or not urwid.util.is_mouse_press(event):
            return False

        self._emit('activate', self)
        return True


class TableWidget(urwid.WidgetWrap):
    """A table, with a single column
    """
    __walker = None
    __list = None
    __list_attrmap = None
    __linebox = None
    __linebox_attrmap = None

    signals = ['changed']

    _table_attr = "table"
    _label_attr = "table.label"
    _header_attr = "table.header"

    _position = 0

    def __init__(self, label, header, items, selected_item, height, enabled):
        self.__label = urwid.Text(label)
        self.__label_attrmap = urwid.AttrMap(self.__label, self._label_attr)
        self.__header = urwid.Text(header)
        self.__header_attrmap = urwid.AttrMap(self.__header, self._header_attr)
        self.__items = items
        self.__walker = urwid.SimpleListWalker(self.__items)
        self.__list = urwid.ListBox(self.__walker)
#        self.__list_linebox = urwid.LineBox(self.__list)

        if selected_item:
            self.set_focus(items.index(selected_item))

        def __on_item_change():
            widget, self._position = self.__list.get_focus()
            self._update_scrollbar()
            urwid.emit_signal(self, "changed", widget)
        urwid.connect_signal(self.__walker, 'modified', __on_item_change)

        self.__box = urwid.BoxAdapter(self.__list, height)
        self.__box_attrmap = urwid.AttrMap(self.__box, self._table_attr)

        self.__position_label = urwid.Text("", align="right")
        self.__position_label_attrmap = urwid.AttrMap(self.__position_label,
                                                      self._label_attr)

        self.__pile = urwid.Pile([self.__label_attrmap,
                                  self.__header_attrmap,
                                  self.__box,
                                  self.__position_label_attrmap])

        self._update_scrollbar()

        super(TableWidget, self).__init__(self.__pile)

    def _update_scrollbar(self):
        n = len(self.__list.body)
        self.__position_label.set_text("(%s / %s)" % (self._position + 1, n))

    def set_focus(self, n):
        self.__list.set_focus(n)


class PluginMenuEntry(TableEntryWidget):
    def __init__(self, title, plugin):
        super(PluginMenuEntry, self).__init__(title)
        self._text.plugin = plugin


class PluginMenu(urwid.WidgetWrap):
    """The main menu listing all available plugins (which have a UI)
    FIXME Use TableWidget
    """
    __pages = None
    __walker = None
    __list = None
    __list_attrmap = None
    __linebox = None
    __linebox_attrmap = None

    signals = ['changed']

    def __init__(self, pages):
        self.__pages = pages
        self.__build_walker()
        self.__build_list()
        self.__build_linebox()
        super(PluginMenu, self).__init__(self.__linebox_attrmap)

    def __build_walker(self):
        items = []

        plugins = self.__pages.items()
        plugins = sorted(plugins, key=lambda two: two[1].rank())

        for title, plugin in plugins:
            if plugin.has_ui():
                item = PluginMenuEntry(title, plugin)
                items.append(item)
            else:
                LOGGER.debug("No UI page for plugin %s" % plugin)

        self.__walker = urwid.SimpleListWalker(items)

    def __build_list(self):
        self.__list = urwid.ListBox(self.__walker)

        def __on_item_change():
            widget, position = self.__list.get_focus()
            plugin = widget.original_widget.plugin
            urwid.emit_signal(self, "changed", plugin)

        urwid.connect_signal(self.__walker, 'modified', __on_item_change)

        self.__list_attrmap = urwid.AttrMap(self.__list, "main.menu")

    def __build_linebox(self):
        self.__linebox = urwid.LineBox(self.__list_attrmap)
        self.__linebox_attrmap = urwid.AttrMap(self.__linebox,
                                               "main.menu.frame")

    def set_focus(self, n):
        self.__list.set_focus(n)


class ModalDialog(urwid.WidgetWrap):
    signals = ['close']

    title = None

    def __init__(self, title, body, escape_key, previous_widget):
        self.escape_key = escape_key
        self.previous_widget = previous_widget

        if type(body) in [str, unicode]:
            body = urwid.Text(body)
        self.title = title
        body = urwid.LineBox(body, title)
        overlay = urwid.Overlay(body, previous_widget, 'center',
                                ('relative', 100), 'bottom',
                                ('relative', 100))
        overlay_attrmap = urwid.AttrMap(overlay, "plugin.widget.dialog")
        super(ModalDialog, self).__init__(overlay_attrmap)

    def close(self):
        urwid.emit_signal(self, "close")

    def __repr__(self):
        return "<%s title='%s' at %s>" % (self.__class__.__name__, self.title,
                                          hex(id(self)))


class Label(urwid.WidgetWrap):
    """A read only widget representing a label
    """

    def __init__(self, text):
        self._label = urwid.Text(text)
        self._label_attrmap = urwid.AttrMap(self._label,
                                            "plugin.widget.label")
        super(Label, self).__init__(self._label_attrmap)

    def text(self, value=None):
        if value is not None:
            self._label.set_text(value)
        return self._label.get_text()

    def set_text(self, txt):
        self.text(txt)
        
class ErrorLabel(urwid.WidgetWrap):
    """A read only widget representing a label
    """

    def __init__(self, text):
        self._label = urwid.Text(text)
        self._label_attrmap = urwid.AttrMap(self._label,
                                            "plugin.widget.error")
        super(ErrorLabel, self).__init__(self._label_attrmap)

    def text(self, value=None):
        if value is not None:
            self._label.set_text(value)
        return self._label.get_text()

    def set_text(self, txt):
        self.text(txt)


class Header(Label):
    """A read only widget representing a header
    """
    _header_attr = "plugin.widget.header"

    def __init__(self, text, template="\n  %s\n"):
        super(Header, self).__init__(template % text)
        self._label_attrmap.set_attr_map({None: self._header_attr})


class KeywordLabel(Label):
    """A read only widget consisting of a "<b><keyword>:</b> <value>"
    """
    _keyword_attr = "plugin.widget.label.keyword"
    _text_attr = "plugin.widget.label"

    def __init__(self, keyword, text=""):
        super(KeywordLabel, self).__init__(text)
        self._keyword = keyword
        self.text(text)
#        self._label_attrmap.set_attr_map({None: ""})

    def text(self, text=None):
        if text is not None:
            self._text = text
            keyword_markup = (self._keyword_attr, self._keyword)
            text_markup = (self._text_attr, self._text)
            markup = [keyword_markup, text_markup]
            self._label.set_text(markup)
        return self._text


class Entry(urwid.WidgetWrap):
    signals = ['change', 'click']

    notice = property(lambda self: self.get_notice(),
                      lambda self, v: self.set_notice(v))

    _selectable = True

    def __init__(self, label, mask=None, align_vertical=False):
        with_linebox = False
        with_notice = False

        self._align_vertical = align_vertical

        if with_linebox:
            label = "\n" + label

        self._label = urwid.Text(label)
        self._label_attrmap = urwid.AttrMap(self._label,
                                            "plugin.widget.entry.label")
        self._edit = EditWithChars(mask=mask)
        self._edit_attrmap = urwid.AttrMap(self._edit, "plugin.widget.entry")
        self._linebox = urwid.LineBox(self._edit_attrmap)
        self._linebox_attrmap = urwid.AttrMap(self._linebox,
                                              "plugin.widget.entry.frame")

        input_widget = self._edit_attrmap
        if with_linebox:
            input_widget = self._linebox_attrmap

        alignment_widget = urwid.Columns
        if self._align_vertical:
            alignment_widget = urwid.Pile
        self._columns = alignment_widget([self._label_attrmap,
                                          input_widget])

        self._notice = urwid.Text("")
        self._notice_attrmap = urwid.AttrMap(self._notice,
                                             "plugin.widget.notice")

        children = [self._columns]
        if with_notice:
            children.append(self._notice_attrmap)
        self._pile = urwid.Pile(children)

        def on_widget_change_cb(widget, new_value):
            urwid.emit_signal(self, 'change', self, new_value)
        urwid.connect_signal(self._edit, 'change', on_widget_change_cb)

        super(Entry, self).__init__(self._pile)
    def text(self, value=None):
        if value is not None:
            self._label.set_text(value)
        return self._label.get_text()
    def enable(self, is_enabled):
        self._selectable = is_enabled
        edit_attr_map = {None: "plugin.widget.entry"}
        linebox_attr_map = {None: "plugin.widget.entry.frame"}
        if not is_enabled:
            edit_attr_map = {None: "plugin.widget.entry.disabled"}
            linebox_attr_map = {None: "plugin.widget.entry.frame.disabled"}
        self._edit_attrmap.set_attr_map(edit_attr_map)
        self._linebox_attrmap.set_attr_map(linebox_attr_map)

    def valid(self, is_valid):
        attr_map_label = {None: "plugin.widget.entry.label"}
        attr_map_edit = {None: "plugin.widget.entry"}
        attr_map_linebox = {None: "plugin.widget.entry.frame"}
        if is_valid:
            self.set_notice(None)
        else:
            attr_map_label = {None: "plugin.widget.entry.label.invalid"}
            attr_map_edit = {None: "plugin.widget.entry.invalid"}
            attr_map_linebox = {None: "plugin.widget.entry.frame.invalid"}
        if self._selectable:
            # Only update style if it is selectable/enabled
            self._label_attrmap.set_attr_map(attr_map_label)
            self._edit_attrmap.set_attr_map(attr_map_edit)
            self._linebox_attrmap.set_attr_map(attr_map_linebox)

    def set_text(self, txt):
        self._edit.set_edit_text(txt or "")

    def selectable(self):
        return self._selectable

    def set_notice(self, txt):
        self._notice_txt = txt
        num_children = len(list(self._pile.contents))
        if txt:
            self._notice.set_text(txt)
            if num_children < 2:
                self._pile.contents.append((self._notice_attrmap, ("pack", 0)))
        else:
            if num_children > 1:
                self._pile.contents.pop()

    def get_notice(self):
        return self._notice_txt


class PasswordEntry(Entry):
    def __init__(self, label, align_vertical=False):
        super(PasswordEntry, self).__init__(label, mask="*",
                                            align_vertical=align_vertical)


class Button(urwid.WidgetWrap):
    signals = ["click"]

    selectable = lambda self: True

    _button_attr = "plugin.widget.button"
    _button_disabled_attr = "plugin.widget.button.disabled"

    def __init__(self, label):
        self._button = urwid.Button(label)

        def on_click_cb(widget, data=None):
            if self.selectable():
                urwid.emit_signal(self, 'click', self)
        urwid.connect_signal(self._button, 'click', on_click_cb)

        self._button_attrmap = urwid.AttrMap(self._button, self._button_attr)

        self._padding = urwid.Padding(self._button_attrmap,
                                      width=self.width())

        super(Button, self).__init__(self._padding)

    def enable(self, is_enabled):
        self.selectable = lambda: is_enabled
        if is_enabled:
            amap = {None: self._button_attr}
        else:
            amap = {None: self._button_disabled_attr}
        self._button_attrmap.set_attr_map(amap)

    def width(self):
        return len(self._button.label) + 4


class Divider(urwid.WidgetWrap):
    def __init__(self, char=u" "):
        self._divider = urwid.Divider(char)
        self._divider_attrmap = urwid.AttrMap(self._divider,
                                              "plugin.widget.divider")
        super(Divider, self).__init__(self._divider_attrmap)


class Options(urwid.WidgetWrap):
    signals = ["change"]

    _label_attr = "plugin.widget.options.label"
    _option_attr = "plugin.widget.options"

    def __init__(self, label, options, selected_option_key):
        self._options = options
        self._button_to_key = {}
        self._bgroup = []
        self._label = urwid.Text(label)
        self._label_attrmap = urwid.AttrMap(self._label, self._label_attr)

        self._buttons = []
        for option_key, option_label in self._options:
            widget = urwid.RadioButton(self._bgroup, option_label,
                                       on_state_change=self._on_state_change)
            self._button_to_key[widget] = option_key
            if option_key == selected_option_key:
                widget.set_state(True)
            widget_attr = urwid.AttrMap(widget, self._option_attr)
            self._buttons.append(widget_attr)
        self._columns = urwid.Columns([self._label_attrmap] + self._buttons)
        self._pile = urwid.Pile([urwid.Divider(), self._columns,
                                 urwid.Divider()])
        super(Options, self).__init__(self._pile)

    def _on_state_change(self, widget, new_state):
        if new_state:
            data = self._button_to_key[widget]
            urwid.emit_signal(self, "change", widget, data)

    def select(self, key):
        for button in self._buttons:
            if button in self._button_to_key:
                bkey = self._button_to_key[button]
                if key == bkey:
                    button.set_state(True)
                    LOGGER.debug("Selected option %s (%s)" % (key, button))
        LOGGER.warning("Could not set selection '%s'" % key)

    def set_text(self, txt):
        self.select(txt)


class Checkbox(urwid.WidgetWrap):
    signals = ['change']

    def __init__(self, label, state):
        self._label = urwid.Text(label)
        self._label_attrmap = urwid.AttrMap(self._label,
                                            "plugin.widget.checkbox.label")
        self._checkbox = urwid.CheckBox("", state)
        self._checkbox_attrmap = urwid.AttrMap(self._checkbox,
                                               "plugin.widget.checkbox")
        self._divider = urwid.Divider()
        self._container = urwid.Columns([self._label_attrmap,
                                         self._checkbox_attrmap])

        def on_change_cb(widget, new_value):
            urwid.emit_signal(self, 'change', self, new_value)
        urwid.connect_signal(self._checkbox, 'change', on_change_cb)

        super(Checkbox, self).__init__(urwid.Pile([self._container,
                                                   self._divider]))

    def set_text(self, s):
        if s in [True, False]:
            self._checkbox.set_state(s)
        else:
            raise Exception("Invalid value: %s" % s)


class PageWidget(urwid.WidgetWrap):
    save_button = None

    def __init__(self, widgets, title=None):
#        self._listwalker = urwid.SimpleListWalker(widgets)
#        self._container = urwid.ListBox(self._listwalker)
        self._container = urwid.Pile(widgets)
        self._container_attrmap = urwid.AttrMap(self._container,
                                                "plugin.widget.page")
        self._header = None
        if title:
            self._header = urwid.AttrMap(urwid.Text(title),
                                         "plugin.widget.page.header")
        self._frame = urwid.Frame(self._container_attrmap, self._header)
        self._box = urwid.Padding(self._frame, width=("relative", 97))
        super(PageWidget, self).__init__(self._box)


class RowWidget(urwid.Columns):
    pass


class ProgressBarWidget(urwid.WidgetWrap):
    def __init__(self, current, done):
        self._progressbar = urwid.ProgressBar(
            "plugin.widget.progressbar.uncomplete",
            "plugin.widget.progressbar.complete",
            current, done)
        self._linebox = urwid.LineBox(self._progressbar)
        self._linebox_attrmap = urwid.AttrMap(self._linebox,
                                              "plugin.widget.progressbar.box")
        super(ProgressBarWidget, self).__init__(self._linebox_attrmap)

    def set_completion(self, v):
        self._progressbar.set_completion(v)


class EditWithChars(urwid.Edit):
    """Is an Edit, but displaying self.char where not char is.
    """
    char = u"_"

    def render(self, size, focus=False):
        (maxcol,) = size
        self._shift_view_to_cursor = bool(focus)

        txt = self.get_edit_text()
        txt = u"".join([self._mask] * len(txt)) if self._mask else txt
        txt = txt.ljust(maxcol, self.char)[:maxcol]
        canv = urwid.Text(txt).render((maxcol,))
        if focus:
            canv = urwid.CompositeCanvas(canv)
            canv.cursor = self.get_cursor_coords((maxcol,))

        return canv


class TabablePile(urwid.Pile):
    def keypress(self, size, key):
        #if "tab" in key:
        #    self.focus_position += 1
        #elif "shift tab" in key:
        #    self.focus_position -= 1
        return (size, key)
