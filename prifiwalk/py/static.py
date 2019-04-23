# xml validator file
# this validator maintains the intergrity of the xml fiwalk output
# source: https://github.com/dfxml-working-group/dfxml_schema
xsdfile = "prifiwalk/.xsd/dfxml.xsd"

# this dict contains the commands that are executed on the OS
commands = {
    'lsblk_big': "sudo lsblk -Jfb -o NAME,FSTYPE,ROTA,HOTPLUG,FSSIZE,FSAVAIL,FSUSED,PARTFLAGS",
    'devsize': "sudo blockdev --getsize64 /dev/{}",
    'model': r"sudo udevadm info --query=all --name=/dev/{} | grep -zoP '(?<=ID_MODEL=).*(?=\n)'",
    'serial': r"sudo udevadm info --query=all --name=/dev/{} | grep -zoP '(?<=ID_SERIAL=).*(?=\n)'",
    'mount': "sudo mount -o ro /dev/{} {}",
    'mount_check': "sudo grep -s {} /proc/mounts",
    'owndev': "sudo df {} | awk 'NR == 2 {{print $1}}'",
    'lsblk_small': "sudo lsblk -lfbn -o NAME,FSTYPE",
    'blocksize': "sudo blockdev --getbsz /dev/{}",
    'validator': "sudo xmlstarlet val -S -s {} {}",
    'fiwalk': "sudo fiwalk -IOgz -X {} /dev/{}"}

# this dict contains the sql queries needed to communicate with the database
sql = {
    'get_last_id': "SELECT last_insert_rowid();",
    'store_system': "INSERT INTO Systems (start_run,end_run) VALUES({},{});",
    'store_device': """INSERT INTO StorageDevices (model,hwid,rotational,hotplug,size,system_id) VALUES('{}','{}',{},{},{},{});""",
    'store_volume': """INSERT INTO Volumes (size,fs_type,free,flags,used,block_size,storage_device_id) VALUES({},'{}',{},'{}',{},{},{});""",
    'store_file': """INSERT INTO Files (volume_id,extension,extension_len,fs_compressed,size,atime,crtime,ctime,mtime,blocks,num_blocks,num_gaps,sum_gaps_bytes,sum_gaps_blocks,backward,num_backward,fragmented,hardlink_id,resident,num_hardlink,sparse,linearconsecutive,fs_seq,fs_nlink, fs_inode) VALUES {};""",
    'file': """({},'{}',{},{},{},{},{},{},{},'{}',{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}),""",
    'get_instances': "SELECT start_run FROM Systems",
    'get_hardlink_id': "SELECT max(hardlink_id) FROM Files"
}

# list of known file extensions
# extensions with 3 chars or less are not included in this list
# those extensions are always accepted by the cleanData function
extensions = (
    "default", "pckgdep", "provxml", "resource", "uninstall",
    "manifest", "settingcontent-ms", "automaticdestinations-ms",
    "customdestinations-ms", "log1", "log2", "log3", "log4", "log5", "log6",
    "log7", "log8", "log9", "gm81", "tiger", "catproduct", "kdbx", "note",
    "crdownload", "vdoc", "lock", "game", "vbox", "nitf", "zargo", "safe",
    "vbox-extpack", "html", "ylib", "msproducer", "plsc", "qhcp", "maff",
    "szproj", "blend", "xmpz", "trash", "dired", "123dx", "ipsw", "email",
    "graffle", "evtx", "tocg", "bdmv", "xish", "vbox-prev", "azw2", "icfm",
    "ffivw", "pages", "azw1", "dtsi", "kext", "fsproj", "epub", "aspx", "3dmf",
    "jnlp", "trib", "yookoo", "dbfx", "mdmp", "atml", "flac", "saver",
    "4dindy", "vsdm", "policy", "fasta", "accdt", "mol2", "ingr", "contact",
    "dats", "bufr", "smclvl", "plist", "xisb", "vsdx", "hdmp", "wifi", "vmcz",
    "vala", "wireframe", "face", "rmvb", "vstx", "xmod", "vrml", "dylib",
    "sh3d", "workflow", "xlsb", "plantuml", "spin", "xlsx", "ccitt", "plsk",
    "cpmz", "mpkg", "vlogo", "olsr", "fstick", "jbig", "chml", "tpoly",
    "webloc", "ssif", "ecmt", "docx", "yaml", "mediawiki", "lisp", "escsch",
    "mppz", "scpt", "mpeg", "cats", "3dsx", "scptd", "grdnt", "fb2k",
    "gameproj", "swift", "vbproj", "djvu", "xlsm", "blob", "mobi", "mlraw",
    "adicht", "ampl", "sdts", "psppalette", "lasso", "midi", "aifc",
    "steamstart", "elfo", "ipynb", "iv-vrml", "soar", "spiff", "sldasm",
    "weboogl", "class", "xisf", "sldprt", "numbers", "pipe", "php3", "vsto",
    "rbxl", "tmy2", "flame", "accda", "coffee", "icfe", "odif", "dicom",
    "udiwww", "xlbl", "sha1", "pack", "xspf", "tddd", "ftxt", "unif", "part",
    "vicar", "vmdk", "text", "pncl", "runz", "jpeg", "vstm", "vsqx", "acmb",
    "escpcb", "m2ts", "topc", "fweb", "film", "iptc", "msdl", "iges", "slddrw",
    "dvdproj", "package", "olk14contact", "file", "accdu", "psm1", "schematic",
    "opus", "viff", "jasc", "lang", "eossa", "pblib", "t2flow", "jfif",
    "manager", "wiki", "schdoc", "fsim", "pkpass", "amlx", "uoml", "bmpw",
    "cmrl", "kodu", "m3u8", "hcgs", "dfti", "qrmx", "sndb", "genbank", "grads",
    "naplps", "term", "irtr", "ppsx", "pseg", "dotx", "gmod", "scala",
    "fb2k-component", "vinf", "emaker", "proj", "dbpro", "accft", "sqlite",
    "info", "artx", "torrent", "vssx", "grasp", "rbxm", "miniusf", "aiff",
    "php4", "indd", "kbasic", "rdata", "xosm", "isma", "love", "java", "stuff",
    "onepkg", "uzed", "bpoly", "kfdk", "accdb", "miff", "anim", "wsrc", "objf",
    "hpgl", "qtvr", "oeaccount", "json", "msdvd", "netcdf", "balance",
    "desklink", "xrm-ms", "greenfoot", "hppcl", "adef", "poly", "shar", "font",
    "smpl", "sats", "catdrawing", "sdml", "pict", "ptped", "jsonld", "tiff",
    "rtfd", "themepack", "neis", "grft", "pptx", "cweb", "tria", "attf",
    "sctor", "trif", "enff", "properties", "mime", "rhistory", "msqm", "vssm",
    "catpart", "desktop", "accde", "cals", "docm", "asmx", "proto", "ecms",
    "plugin", "irrmesh", "ply2", "quox", "beam", "par2", "clpi", "vcls",
    "theme", "bdef", "fits", "wmdb", "adson", "clprj", "grib", "ibro", "saif")


create_database = '''
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

CREATE TABLE Files (
    id                INTEGER  PRIMARY KEY,
    volume_id         INTEGER,
    extension         TEXT,
    extension_len     INTEGER,
    mtime             DATETIME,
    ctime             DATETIME,
    atime             DATETIME,
    crtime            DATETIME,
    size              INTEGER,
    blocks            NUMERIC,
    num_blocks        INTEGER,
    num_gaps          INTEGER,
    sum_gaps_bytes    INTEGER,
    sum_gaps_blocks   INTEGER,
    fragmented        BOOLEAN,
    backward          BOOLEAN,
    num_backward      INTEGER,
    resident          BOOLEAN,
    fs_compressed     BOOLEAN,
    sparse            BOOLEAN,
    linearconsecutive BOOLEAN,
    hardlink_id       INTEGER,
    num_hardlink      INTEGER,
    fs_seq            INTEGER,
    fs_nlink          INTEGER,
    fs_inode          INTEGER,
    CONSTRAINT lnk_Volumes_Files FOREIGN KEY (
        volume_id
    )
    REFERENCES Volumes (id),
    CONSTRAINT unique_id UNIQUE (
        id
    )
);

CREATE TABLE StorageDevices (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id  INTEGER,
    model      TEXT,
    hwid       TEXT,
    size       INTEGER,
    rotational BOOLEAN,
    hotplug    BOOLEAN,
    CONSTRAINT lnk_Systems_StorageDevices FOREIGN KEY (
        system_id
    )
    REFERENCES Systems (id),
    CONSTRAINT unique_id UNIQUE (
        id
    )
);

CREATE TABLE Systems (
    id        INTEGER  PRIMARY KEY AUTOINCREMENT,
    start_run DATETIME,
    end_run   DATETIME,
    os        TEXT,
    CONSTRAINT unique_id UNIQUE (
        id
    )
);

CREATE TABLE Volumes (
    id                INTEGER PRIMARY KEY,
    storage_device_id INTEGER,
    fs_type           TEXT,
    size              INTEGER,
    used              INTEGER,
    free              INTEGER,
    block_size        INTEGER,
    flags             TEXT,
    CONSTRAINT lnk_StorageDevices_Volumes FOREIGN KEY (
        storage_device_id
    )
    REFERENCES StorageDevices (id),
    CONSTRAINT unique_id UNIQUE (
        id
    )
);

CREATE INDEX index_deviceid ON Volumes (
    "storage_device_id"
);

CREATE INDEX index_instanceid ON StorageDevices (
    "system_id"
);

CREATE INDEX index_volumeid ON Files (
    "volume_id"
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;'''
