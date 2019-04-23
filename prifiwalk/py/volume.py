from py.function import execute as cmdexec
from py.function import clean_file_names
from py.function import fiwalk_xml
from py.config import files_only
from py.database import Database
from py.static import commands
from py.file import File
import os


class Volume():
    """docstring for Volume"""

    def __init__(self, data):
        self.storage = data['storage']
        self.blocksize = data['blocksize']
        self.size = data['size']
        self.free = data['free']
        self.used = data['used']
        self.filesystem = data['filesystem']
        self.flags = data['flags']
        self.name = data['name']
        self.files = []
        self.temp_files = []
        self.database_id = None

        self.find_files(data['name'])

    def find_files(self, device):
        xmlfile = "prifiwalk/.temp/{}.xml".format(device)
        command = commands['fiwalk']
        cmdexec(command.format(xmlfile, device))
        self.temp_files = fiwalk_xml(xmlfile)
        self.temp_files = clean_file_names(self.temp_files)
        self.clear_temp_folder()

        if self.storage.system.mode == 'full':
            self.create_files()
            self.find_hardlinks()
        elif self.storage.system.mode == 'half':
            pass

    def create_files(self):
        while self.temp_files != []:
            data = self.temp_files.pop()
            if files_only:
                if data['name_type'] == 'd':
                    continue
            self.add_file(data)

    def add_file(self, data):
        data['volume'] = self
        new_file = File(data)
        self.files.append(new_file)

    def clear_temp_folder(self):
        cwd = os.path.join(os.getcwd(), 'prifiwalk/.temp')
        folder = os.listdir(cwd)
        for item in folder:
            if item.endswith(".xml"):
                os.remove(os.path.join(cwd, item))

    def find_hardlinks(self):
        self.files = sorted(self.files, key=self.file_block_sorter)
        print(len(self.files))

        if self.storage.system.hardlink_id is None:
            db = Database()
            self.storage.system.hardlink_id = db.get_hardlink_id()
            self.storage.system.hardlink_id += 1

        for i, file in enumerate(self.files):
            if file.blocks is not None and file.hardlink_id is None:
                numref = 1
                while((len(self.files) - 1) >= (i + numref) and
                      self.files[i].blocks == self.files[i + numref].blocks):
                    numref += 1
                if numref != 1:
                    for x in range(0, numref):
                        self.files[i + x].hardlink_id =\
                            self.storage.system.hardlink_id
                        self.files[i + x].hardlink_num = numref
                    self.storage.system.hardlink_id += 1

    def file_block_sorter(self, f):
        if f.blocks is None:
            return 0
        else:
            return f.blocks[0]
