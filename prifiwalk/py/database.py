from py.static import create_database
from py.config import logname
from py.config import max_sql_insert
from logging import getLogger
from py.static import sql
from sys import exit
import sqlite3
import os


file = "prifiwalk/data/database/prifiwalk.db"
dbfile = os.path.join(os.getcwd(), file)


class Database:
    """docstring for Database"""

    def __init__(self):
        self.logger = getLogger(logname)
        self.connection = None
        self.cursor = None

        if not self.exists():
            self.create()

        if not self.integrity():
            self.logger.error("The integrity of the database is compromised.")
            self.logger.error("Either delete or move the database so that" +
                              " the program can recreate it next execution.")
            exit()

    def exists(self):
        return os.path.isfile(dbfile)

    def create(self):
        connection = sqlite3.connect(dbfile)
        cursor = connection.cursor()
        cursor.executescript(create_database)
        connection.commit()
        connection.close()

    def integrity(self):
        connection = sqlite3.connect(dbfile)
        cursor = connection.cursor()
        cursor.execute("pragma integrity_check;")
        result = cursor.fetchone()[0]
        if result == 'ok':
            self.connection = connection
            self.cursor = cursor
            return True
        else:
            connection.commit()
            connection.close()
            return False

    def get_hardlink_id(self):
        self.cursor.execute(sql['get_hardlink_id'])
        self.connection.commit()
        result = self.cursor.fetchone()[0]
        if result is None:
            result = 0
        return result

    def store(self, system):
        self.store_system(system)

        for device in system.storages:
            self.store_device(device)
            for volume in device.volumes:
                self.store_volume(volume)

        self.store_files(system)

    def store_system(self, system):
        # insert new data
        statement = sql['store_system']
        statement = statement.format(
            system.start_measurement,
            system.end_measurement)
        self.cursor.execute(statement)
        self.connection.commit()

        # get generated id from inserted data
        statement = sql['get_last_id']
        self.cursor.execute(statement)
        self.connection.commit()
        result = self.cursor.fetchone()[0]
        system.database_id = int(result)

    def store_device(self, device):
        # insert new data
        statement = sql['store_device']
        statement = statement.format(
            device.model,
            device.hardware_id,
            device.rotational,
            device.hotplug,
            device.size,
            device.system.database_id)
        self.cursor.execute(statement)
        self.connection.commit()

        # get generated id from inserted data
        statement = sql['get_last_id']
        self.cursor.execute(statement)
        self.connection.commit()
        result = self.cursor.fetchone()[0]
        device.database_id = int(result)

    def store_volume(self, volume):
        # insert new data
        statement = sql['store_volume']
        statement = statement.format(
            volume.size,
            volume.filesystem,
            volume.free,
            volume.flags,
            volume.used,
            volume.blocksize,
            volume.storage.database_id)
        self.cursor.execute(statement)
        self.connection.commit()

        # get generated id from inserted data
        statement = sql['get_last_id']
        self.cursor.execute(statement)
        self.connection.commit()
        result = self.cursor.fetchone()[0]
        volume.database_id = int(result)

    def store_files(self, system):
        count = 0
        collection = ''

        for device in system.storages:
            for volume in device.volumes:
                for file in volume.files:
                    collection += self.build_file_insert(file)
                    count += 1
                    if count == max_sql_insert:
                        self.insert_files(collection)
                        collection = ''
                        count = 0
        if collection != '':
            self.insert_files(collection)

    def build_file_insert(self, file):
        file_insert = sql['file']
        if file.blocks is None:
            blocks = []
        else:
            blocks = file.blocks
        blocks = " ".join(str(x) for x in blocks)
        file_insert = file_insert.format(
            file.volume.database_id,
            file.extension,
            file.extension_len,
            file.fs_compressed,
            file.filesize,
            file.atime,
            file.crtime,
            file.ctime,
            file.mtime,
            blocks,
            file.num_blocks,
            file.num_gaps,
            file.sum_gaps_bytes,
            file.sum_gaps_blocks,
            file.backward,
            file.num_backward,
            file.fragmented,
            file.hardlink_id,
            file.resident,
            file.hardlink_num,
            file.sparse,
            file.linear_consecutive,
            file.fs_sequence,
            file.fs_nlink,
            file.fs_inode)
        file_insert = file_insert.replace(",None", ",null")
        return file_insert

    def insert_files(self, collection):
        statement = sql['store_file']
        statement = statement.format(collection[:-1])
        self.cursor.execute(statement)
        self.connection.commit()
