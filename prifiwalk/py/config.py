# This option makes the script ignore the device that this script is run from
# This helps with executing the script from an bootable usb for data collection
ignore_own_dev = True

# Filesystem types that will be researched by this script
# Theoretical support for NTFS, FAT, ExFAT, UFS 1, UFS 2, EXT2FS, EXT3FS, Ext4,
# HFS, ISO 9660, and YAFFS2
allowed_filesystems = ['ntfs']

# only save files (don't save directories)
# fiwalk creates an xml as output, that's converted to a python datastructure
# if this setting is true the directories will be omitted
# if this setting is false the direcctories when be added to the datastructure
# but these directories wont have their names (to preserve privacy)
files_only = True

# config file path
logfile = 'prifiwalk/logs/main.log'
logname = 'main_logger'

# this is the maximum number of files added to the database in one query
# reason: to maintain performance and memory footprint
max_sql_insert = 10000
