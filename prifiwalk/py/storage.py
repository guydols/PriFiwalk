from py.function import execute as cmdexec
from py.volume import Volume
from py.static import commands


class Storage():
    """docstring for Storage"""

    def __init__(self, data):
        self.system = data['system']
        self.hotplug = data['hotplug']
        self.hardware_id = data['hardware_id']
        self.model = data['model']
        self.name = data['name']
        self.rotational = data['rotational']
        self.size = data['size']
        self.volumes = []
        self.database_id = None

        self.find_volumes(data['children'], data['allowed_devs'])

    def find_volumes(self, volumes, allowed):
        for volume in volumes:
            if volume['name'] in allowed:
                self.add_volume(volume)

    def add_volume(self, volume):
        new_volume = Volume(
            {'storage': self,
             'blocksize': self.get_blocksize(volume['name']),
             'size': volume['fssize'],
             'free': volume['fsavail'],
             'used': volume['fsused'],
             'filesystem': volume['fstype'],
             'flags': volume['partflags'],
             'name': volume['name']
             })
        self.volumes.append(new_volume)

    def get_blocksize(self, dev):
        command = commands['blocksize']
        output = cmdexec(command.format(dev))
        return output
