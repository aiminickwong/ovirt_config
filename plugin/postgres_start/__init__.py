"""Dialog plugin."""


from otopi import util


from . import postgres_startup


@util.export
def createPlugins(context):
    postgres_startup.Plugin(context=context)


#
