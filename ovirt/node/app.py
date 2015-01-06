#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# app.py - Copyright (C) 2012 Red Hat, Inc.
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
from ovirt.node import base, utils, plugins, ui
from ovirt.node.config import defaults
from ovirt.node.ui import urwid_builder
from ovirt.node.utils import system, Timer
import argparse
import logutils.dictconfig
import sys

"""
Representing the whole application (not just the TUI).
Basically the application consists of two parts: Page-Plugins and the UI
which communicate with each other.
"""


log_filename = "/tmp/ovirt.log"
debug_log_filename = "/tmp/ovirt.debug.log"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s:%(lineno)s ' +
            '%(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)10s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': log_filename,
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': debug_log_filename,
        },
        'stderr': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'stream': sys.stderr
        }
    },
    'loggers': {
        '': {
            'handlers': ['debug', 'stderr'],
            'level': 'DEBUG',
        },
        'ovirt.node': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}

utils.fs.truncate(log_filename)
utils.fs.truncate(debug_log_filename)
logutils.dictconfig.dictConfig(LOGGING)


def configure_logging():
    logdict = dict(LOGGING)
    logutils.dictconfig.dictConfig(logdict)
    #logging.basicConfig(level=logging.DEBUG,
    #                    filename="/tmp/app.log", filemode="w",
    #                    format="%(asctime)s %(levelname)s %(name)s " +
#                               "%(message)s")


class Application(base.Base):
    """The controller part when seeing as an MVC pattern

    Args:
        __plugins: All known plugins
        ui_builder: The builder used to build the UI
        ui: The root window of the UI
    """
    __plugins = {}
    __current_plugin = None

    ui_builder = None
    ui = None

    def __init__(self, plugin_base, ui_builder=urwid_builder.UrwidUIBuilder):
        """Constructs a new application

        Args:
            plugin_base: The package where to find page-plugins
            ui_builder: An implementation of the UIBuilder class to be used
        """
        super(Application, self).__init__()
        self.logger.info(("Starting '%s' application " +
                          "with '%s' UI") % (plugin_base, ui_builder))

        self.__parse_cmdline()

        self.ui_builder = ui_builder(self)
        self.ui = self.ui_builder.build(ui.Window("screen", self))
        self.plugin_base = plugin_base

    def __parse_cmdline(self):
        parser = argparse.ArgumentParser(description='oVirt Node Utility')
        parser.add_argument("--defaults",
                            type=str,
                            help="Central oVirt Node configuration file")
        parser.add_argument("--dry",
                            action='store_true',
                            help="Just write defaults, nothing else")
        self.args = parser.parse_args()
        self.logger.debug("Parsed args: %s" % self.args)
        if self.args.defaults:
            # FIXME Should be read by clients
            defaults.OVIRT_NODE_DEFAULTS_FILENAME = self.args.defaults
            self.logger.debug("Setting config file: %s (%s)" %
                              (self.args.defaults,
                              defaults.OVIRT_NODE_DEFAULTS_FILENAME))

        self.logger.debug("Commandline arguments: %s" % self.args)

    def plugins(self):
        """Retrieve all loaded plugins
        """
        return self.__plugins

    def get_plugin(self, mixed):
        """Find a plugin by instance, name, or type
        """
        mtype = type(mixed)
        self.logger.debug("Looking up plugin: %s (%s)" % (mixed, mtype))
        plugin = None

        if isinstance(mixed, plugins.NodePlugin):
            plugin = mixed
        elif mtype in [str, unicode]:
            plugin = self.__plugins[mixed]
        elif mtype is type:
            #type_to_instance = {type(p): p for p in self.__plugins.values()}
            type_to_instance = dict((type(p), p) for p
                        in self.__plugins.values())
            if mixed not in type_to_instance:
                raise RuntimeError("Requested plugin type '%s' is not in %s" %
                                   (mixed, type_to_instance))
            plugin = type_to_instance[mixed]
        else:
            raise Exception("Can't look up: %s" % mixed)

        self.logger.debug("Found plugin for type: %s" % plugin)
        return plugin

    def current_plugin(self):
        """Returns the current plugin
        """
        return self.__current_plugin

    def assign_actions(self, ui_container):
        """Searches through an element-tree (container is the root) and
        sets callbacks on all common ui.Actions.

        The ui.Module is just specififying the behavior, how the behaior is
        realized happens here. E.g. what a SaveAction actaully triggers.

        Args:
            ui_container: The element-tree root
        """
        self.logger.debug("Assigning UI actions to %s" % ui_container)
        assert ui.ContainerElement in type(ui_container).mro()
        plugin = self.current_plugin()
        window = self.ui
        elements = ui_container.elements()

        def cond_close_dialog(userdata):
            self.logger.debug("Closing dialog: %s" % userdata)
            if ui.Dialog in type(userdata).mro():
                window.close_dialog(userdata.title)
            else:
                window.close_topmost_dialog()

        # All known handlers
        handlers = {ui.SaveAction:
                    lambda d: self.current_plugin()._on_ui_save(),
                    ui.CloseAction: cond_close_dialog,
                    ui.ResetAction:
                    lambda d: self.current_plugin()._on_ui_reset(),
                    ui.ChangeAction:
                    lambda d: self.current_plugin()._on_ui_change(d),
                    ui.ReloadAction:
                    lambda d: self.switch_to_plugin(self.current_plugin(),
                                                    False),
                    ui.QuitAction:
                    lambda d: self.quit()
                    }

        for element in elements:
            for path, signal in element.list_signals():
                callbacks = signal.callbacks
                for cb in callbacks:
                    if type(cb) in handlers and not cb.callback:
                        action = handlers[type(cb)]
                        self.logger.debug("Setting %s.%s to %s" %
                                          (element, cb, action))
                        cb.callback = action
            if type(element) is ui.SaveButton:
                # http://stackoverflow.com/questions/2731111/
                # python-lambdas-and-variable-bindings
                toggle_disabled = lambda t, v, e=element: e.enabled(v)
                plugin.on_valid.connect(toggle_disabled)

    def populate_with_values(self, ui_container):
        """Take values from model and inject them into the appropriate UI
        elements.

        The mapping happens through the "path". Each UI Element has an assigned
        path, which associates them with a place in the model.
        """
        self.logger.debug("Assigning model values to %s" % ui_container)
        assert ui.ContainerElement in type(ui_container).mro()
        model = self.current_plugin().model()
        for element in ui_container.elements():
            if element.path in model:
                value = model[element.path]
                self.logger.debug("Populating %s: %s" % (element, value))
                element.value(value)

    def switch_to_plugin(self, plugin, check_for_changes=True):
        """Set the context to the given plugin.
        This includes displaying the page-plugin UI on a page.
        """
        self.logger.debug("Switching to plugin " +
                          "%s, with checks? %s" % (plugin, check_for_changes))
        if check_for_changes and self._check_outstanding_changes():
            return
        plugin = self.get_plugin(plugin)
        self.__current_plugin = plugin
        with Timer() as t:
            content = plugin.ui_content()
            self.show(content)
        self.logger.debug("Build and displayed plugin_page in %s seconds" % t)

    def show(self, ui_container):
        """Shows the ui.Page as a page.
        This transforms the abstract ui.Page to a urwid specififc version
        and displays it.
        """
        assert ui.Page in type(ui_container).mro()
        plugin = self.current_plugin()
        self.populate_with_values(ui_container)
        self.assign_actions(ui_container)
        plugin.check_semantics()
        if ui.Dialog in type(ui_container).mro():
            self.ui._show_on_dialog(ui_container)
        elif ui.Page in type(ui_container).mro():
            self.ui._show_on_page(ui_container)
        else:
            raise Exception("Unknown container: %s" % ui_container)
        return ui_container

    @property
    def product(self):
        return system.ProductInformation()

    def run(self):
        self.__load_plugins()

        if not self.__plugins:
            raise Exception("No plugins found in '%s'" % self.plugin_base)
        #self.ui.register_hotkey("f2", self.__drop_to_shell)
        self.ui.register_hotkey("window resize", self.__check_terminal_size)

        self.ui.header = "\n %s\n" % str(self.product)
        self.ui.footer = "Press esc to quit."

        try:
            self.ui.run()
        except Exception as e:
            import traceback
            with open('/root/111','a+') as f:
                traceback.print_exc(file=f)
            utils.process.call("reset")
            self.logger.error("An error appeared in the UI: %s" % repr(e))
            utils.console.writeln("Press ENTER to logout ...")
            utils.console.writeln("or enter 's' to drop to shell")
            if utils.console.wait_for_keypress() == 's':
                self.__drop_to_shell()

    def quit(self):
        self.logger.info("Quitting")
        self.ui.quit()

    def notice(self, msg):
        children = [ui.Label("app.notice.text", msg)]
        dialog = ui.Dialog("app.notice", "Notice", children)
        dialog.buttons = [ui.CloseButton("app.notice.close")]
        #self.ui._notice(dialog)

    def _check_outstanding_changes(self):
        has_outstanding_changes = False
        if self.current_plugin():
            pending_changes = self.current_plugin().pending_changes()
            if pending_changes:
                self.logger.warning("Pending changes: %s" % pending_changes)
                msg = ""
                elements = self.current_plugin().ui_content().elements()
                self.logger.debug("Available elements: %s" % elements)
                for path, value in pending_changes.items():
                    if path in elements:
                        # assumption that element is a container
                        element = elements[path]
                        field = element.path
                        self.logger.debug("Changed widget: " +
                                          "%s %s" % (path, element))
                        msg += "- %s\n" % (field.strip(":"))
                if msg:
                    txt = "The following fields have changed:\n%s" % msg
                    txt += "\n\nPlease save or reset the page."
                    self.ui.display_as_dialog(ui.Dialog("pendin",
                                                        "Pending Changes",
                                                        [ui.Label(txt)]))
                    has_outstanding_changes = True
        return has_outstanding_changes

    def __load_plugins(self):
        """Load all plugins which are found in the given plugin_base
        """
        self.__plugins = {}
        for m in plugins.load(self.plugin_base):
            if hasattr(m, "Plugin"):
                self.logger.debug("Found plugin in module: %s" % m)
                plugin = m.Plugin(self)
                self.logger.debug("Registering plugin '%s': %s" %
                                  (plugin.name(), plugin))
                self.__plugins[plugin.name()] = plugin
            else:
                self.logger.debug("Found no plugin in module: %s" % m)

        for plugin in self.__plugins.values():
            self.logger.debug("Loading plugin %s" % plugin)
            self.ui.register_plugin(plugin.ui_name(), plugin)

    def __drop_to_shell(self):
        with self.ui.suspended():
            utils.process.call("reset")
            utils.console.writeln("Dropping to rescue shell ...")
            utils.process.call("bash")

    def __check_terminal_size(self):
        cols, rows = self.ui.size()
        if cols < 80 or rows < 24:
            self.logger.warning("Window size is too small: %dx%d" % (cols,
                                                                     rows))
