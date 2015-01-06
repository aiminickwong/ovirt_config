"""Dialog plugin."""


from otopi import util


from . import admin_change


@util.export
def createPlugins(context):
    admin_change.Plugin(context=context)


#
