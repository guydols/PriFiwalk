from py.function import date_to_unixtime as d2u
from math import ceil


class File():
    """docstring for File"""

    def __init__(self, data):

        # define parent
        self.volume = data['volume']

        # preloaded vars
        self.extension = data['filename']
        self.extension_len = data['extlen']
        self.filesize = data.get('filesize', None)
        self.fs_inode = data.get('inode', None)
        self.fs_nlink = data.get('nlink', None)

        # the sequence field is only used by NTFS
        if self.volume.filesystem.lower() == 'ntfs':
            self.fs_sequence = data['seq']
        else:
            self.fs_sequence = None

        # converted vars
        self.atime = d2u(data.get('atime', None))
        self.crtime = d2u(data.get('crtime', None))
        self.ctime = d2u(data.get('ctime', None))
        self.mtime = d2u(data.get('mtime', None))

        # calculated vars
        self.on_disk = self.is_on_disk(data)
        self.resident = self.is_resident(data)
        self.fs_compressed = self.is_fs_compressed(data)
        self.sparse = self.is_sparse(data)
        self.blocks = self.define_blocks(data)

        self.num_blocks = None
        self.num_gaps = None
        self.sum_gaps_bytes = None
        self.sum_gaps_blocks = None
        self.fragmented = None
        self.backward = None
        self.num_backward = None
        self.linear_consecutive = None

        self.derive_statistics(data)

        self.hardlink_id = None
        self.hardlink_num = None

    # defining file types

    def is_on_disk(self, data):
        if data.get('filesize', 0) == 0 or len(data.get('byte_runs', [])) == 0:
            return False
        return True

    def is_resident(self, data):
        if (data.get('type', None) == 'resident' or
        data.get('byte_runs', [{}])[0].get('type', None) == 'resident'):
            return True
        else:
            return False

    def is_fs_compressed(self, data):
        for byterun in data.get('byte_runs', []):
            if (data.get('compressed', 0) == 1 and
                    'uncompressed_len' in byterun):
                return True
        return False

    def is_sparse(self, data):
        for byterun in data.get('byte_runs', []):
            if 'fill' in byterun:
                return True
        return False

    # defining the blocks a file occupies

    def define_blocks(self, data):
        if 'byte_runs' not in data.keys():
            return None
        if len(data['byte_runs']) == 0:
            return None
        if self.resident:
            return None
        if self.fs_compressed:
            return self.compressed_blocks(data['byte_runs'])
        if self.sparse:
            return self.sparse_blocks(data['byte_runs'])
        return self.normal_blocks(data['byte_runs'])

    def normal_blocks(self, byteruns):
        blocks = []
        for byterun in byteruns:
            blocks.append(byterun['fs_offset'])
            blocks.append("-")
            blocks.append(byterun['len'] + byterun['fs_offset'] - 1)
        return blocks

    def sparse_blocks(self, byteruns):
        blocks = []
        for byterun in byteruns:
            if 'fs_offset' in byterun and 'len' in byterun:
                blocks.append(byterun['fs_offset'])
                blocks.append("-")
                blocks.append(byterun['len'] + byterun['fs_offset'] - 1)
            elif 'fill' in byterun:
                continue
        return blocks

    def compressed_blocks(self, byteruns):
        blocks = []
        for byterun in byteruns:
            if (len(byterun) == 2 and
                'file_offset' in byterun and
                    'uncompressed_len' in byterun):
                continue
            else:
                blocks.append(byterun['fs_offset'])
                blocks.append("-")
                blocks.append(
                    byterun['uncompressed_len'] + byterun['fs_offset'] - 1)
        if len(blocks) == 0:
            return None
        return blocks

    # deriving statistics from blockdata

    def derive_statistics(self, data):
        '''
        This function calculates derivative value's from the block infomration
        '''

        if self.is_on_disk is False or self.blocks is None:
            return

        num_gaps = 0
        filesize = 0
        sum_gaps = 0
        num_backward = 0
        backward = False
        linear_consecutive = 0

        for i, block in enumerate(self.blocks):
            if block == '-':
                # stat to count the number of blocks
                filesize += (self.blocks[(i + 1)] + 1) - self.blocks[(i - 1)]

                # check if the blocks of a file are linear consecutive
                if self.blocks[(i + 1)] + 1 in self.blocks:
                    pass
                else:
                    linear_consecutive += 1

                if len(self.blocks) > (i + 2):
                    # stat to calculate the sum of the gaps between blocks
                    sum_gaps += (abs(self.blocks[(i + 1)] -
                                     self.blocks[(i + 2)]) - 1)

                    # count the cumber of gaps between blocks
                    if self.blocks[(i + 1)] + 1 != self.blocks[(i + 2)]:
                        num_gaps += 1

                    # check if file is backwards fragmented and how often
                    if self.blocks[(i + 1)] > self.blocks[(i + 2)]:
                        num_backward += 1
                        backward = True

        self.num_blocks = ceil(filesize / self.volume.blocksize)
        self.num_gaps = num_gaps
        self.sum_gaps_bytes = sum_gaps
        self.backward = backward
        self.num_backward = num_backward

        self.sum_gaps_blocks = ceil(
            self.sum_gaps_bytes / self.volume.blocksize)

        if self.num_gaps == 0:
            self.fragmented = False
        else:
            self.fragmented = True

        if linear_consecutive <= 1:
            self.linear_consecutive = True
        else:
            self.linear_consecutive = False
