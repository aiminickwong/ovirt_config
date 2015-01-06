#from ovirt.node.utils import vdcoption


import gettext
_ = lambda m: gettext.dgettext(message=m, domain='ovirt-engine-setup')


from otopi import constants as otopicons
from otopi import util
from otopi import plugin


from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common \
    import constants as oengcommcons
from ovirt_engine_setup import dialog
from ovirt_engine_setup.engine import vdcoption

class Plugin(plugin.PluginBase):
    
    def __init__(self, context):
        super(Plugin, self).__init__(context=context)
        self._enabled = True


        
        
        
    @plugin.event(
        stage=plugin.Stages.STAGE_BOOT,
        
        priority=plugin.Stages.PRIORITY_LAST+20,
        condition=lambda self: self._enabled,
    )
    def postgres_startup(self):
        
        cmd = "postgresql-setup initdb"
        from ovirt.node.utils import process
        res=process.pipe(cmd)
        
        cmd = "systemctl start postgresql"
        
        res=process.pipe(cmd)        
        

    def __miscEncrypted(self):
        import ovirt.node.utils.vdcoption as vdcoption
        vdcoption.VdcOption().updateVdcOptions(
            options=(
                {
                    'name': 'LocalAdminPassword',
                    'value': self.environment[
                        'OVESETUP_CONFIG/adminPassword'
                        ],
                    'encrypt': True,
                    },
                {
                    'name': 'AdminPassword',
                    'value': self.environment[
                        'OVESETUP_CONFIG/adminPassword'
                        ],
                    'encrypt': True,
                    },
                ),
        )    
