from py.function import execute as cmdexec
from py.function import message
from py.storage import Storage
from py.static import commands
import py.config as config
import json
import os
import time


class System:
    """docstring for System"""

    def __init__(self, mode):
        self.mode = mode
        self.operating_system = None
        self.start_measurement = int(time.time())
        self.storages = []
        self.database_id = None
        self.hardlink_id = None

        self.find_devices()

        self.end_measurement = int(time.time())

    def find_devices(self):
        self.allowed_devs = self.get_allowed_devs()

        message(
            "Researching devices: " +
            ", ".join(str(x) for x in self.allowed_devs),
            log='info', display=True)

        self.mount_storage_devs()
        lsblk_data = self.get_dev_meta()

        for device in lsblk_data['blockdevices']:
            if 'children' in device.keys():
                for child in device['children']:
                    if (child['name'] in self.allowed_devs and
                            not self.device_created(device)):
                        self.add_storage_dev(device)
            else:
                if device['name'] in self.allowed_devs:
                    pass  # todo
                    # lsblk sometime returns volumes not on the
                    # level of childeren but on blockdevice level

    def device_created(self, device):
        for created_device in self.storages:
            if created_device.name == device['name']:
                return True
        return False

    def add_storage_dev(self, device):
        new_storage = Storage(
            {'system': self,
             'hotplug': device['hotplug'],
             'hardware_id': self.get_dev_hardware_id(device['name']),
             'model': self.get_dev_model(device['name']),
             'name': device['name'],
             'rotational': device['rota'],
             'size': self.get_dev_size(device['name']),
             'children': device['children'],
             'allowed_devs': self.allowed_devs
             })
        self.storages.append(new_storage)

    def get_allowed_devs(self):
        all_devs = []
        command = commands['lsblk_small']

        output = cmdexec(command)
        output = output.split('\n')
        for dev in output:
            all_devs.append(dev.split(' '))

        if config.ignore_own_dev:
            own_dev = self.get_own_device()
            return self.filter_devs(all_devs, own_dev)
        else:
            return self.filter_devs(all_devs)

    def get_own_device(self):
        command = commands['owndev']
        path = os.getcwd()
        output = cmdexec(command.format(path + '/' + __file__))
        dev = output.split('/')[-1]
        return dev

    def filter_devs(self, all_devs, ignore_dev=None):
        allowed_devs = []
        for dev in all_devs:
            if ignore_dev is not None and ignore_dev in dev:
                continue
            if dev[-1] not in config.allowed_filesystems:
                continue
            allowed_devs.append(dev[0])
        return allowed_devs

    def mount_storage_devs(self):
        mountpath = os.path.dirname(
            os.path.realpath(__file__))[:-2] + ".mount/{}"
        mountcmd = commands['mount']
        checkcmd = commands['mount_check']
        for dev in self.allowed_devs:
            output = cmdexec(checkcmd.format(dev), nullable=True)
            if dev in output:
                continue
            if not os.path.exists(mountpath.format(dev)):
                os.makedirs(mountpath.format(dev))
            cmdexec(mountcmd.format(dev, mountpath.format(dev)))

    def get_dev_meta(self):
        command = commands['lsblk_big']
        output = cmdexec(command)
        devices = json.loads(output)
        return devices

    def get_dev_size(self, dev):
        command = commands['devsize']
        output = cmdexec(command.format(dev))
        return output

    def get_dev_model(self, dev):
        command = commands['model']
        output = cmdexec(command.format(dev))
        return output

    def get_dev_hardware_id(self, dev):
        command = commands['serial']
        output = cmdexec(command.format(dev))
        return output
