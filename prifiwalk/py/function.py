from datetime import datetime
import py.config as config
import py.static as static
from sys import exit
import subprocess
import logging
import calendar
import xml.sax
import pickle
import os


logger = logging.getLogger(config.logname)
formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')


def execute(cmd, multiline=None, nullable=False):
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        output = process.communicate()
        retval = process.wait()

        interpretation = interpret(output, retval, nullable)
        if interpretation == 'error':
            message(["Error occurred during the execution command: " +
                     str(cmd), "Output: " + str(output) + " Return value: " +
                     str(retval)], log='error', display=False)
            message("\nRuntime error occurred, check log: " +
                    config.logfile, log=None, display=True)
            exit()
        else:
            return interpretation

    except Exception as e:
        message("Error occurred during the execution command: " +
                str(cmd), log='error', display=False)
        logger.error(e, exc_info=True)
        message("\nRuntime error occurred, check log: " +
                config.logfile, log=None, display=True)
        exit()


def interpret(output, retval, nullable):
    if ('command not found' not in str(output[0]) and
            retval == 0 and output[1] is None):
        decoded = output[0][:-1].decode("utf-8")
        if decoded.isnumeric():
            return int(decoded)
        return decoded
    else:
        if nullable:
            return ''
        return 'error'


def date_to_unixtime(date):
    if date is None:
        return date

    date = str(date)
    try:
        if len(date) > 0 and len(date) <= 3:
            return 0
        if len(date) >= 4 and len(date) <= 5:
            if date[-1].isdigit():
                newdate = datetime.strptime(date, "%Y")
            else:
                newdate = datetime.strptime(date[:-1], "%Y")
        if len(date) > 5 and len(date) <= 8:
            if date[-1].isdigit():
                newdate = datetime.strptime(date, "%Y-%m")
            else:
                newdate = datetime.strptime(date[:-1], "%Y-%m")
        if len(date) > 8 and len(date) <= 11:
            if date[-1].isdigit():
                newdate = datetime.strptime(date, "%Y-%m-%d")
            else:
                newdate = datetime.strptime(date[:-1], "%Y-%m-%d")
        if len(date) > 11 and len(date) <= 14:
            if date[-1].isdigit():
                newdate = datetime.strptime(date, "%Y-%m-%dT%H")
            else:
                newdate = datetime.strptime(date[:-1], "%Y-%m-%dT%H")
        if len(date) > 14 and len(date) <= 17:
            if date[-1].isdigit():
                newdate = datetime.strptime(date, "%Y-%m-%dT%H:%M")
            else:
                newdate = datetime.strptime(date[:-1], "%Y-%m-%dT%H:%M")
        if len(date) > 17 and len(date) <= 19:
            if date[-1].isdigit():
                newdate = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            else:
                newdate = datetime.strptime(date[:-1], "%Y-%m-%dT%H:%M:%S")
        if len(date) == 20:
            newdate = datetime.strptime(date[:-1], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return 0
    return calendar.timegm(newdate.timetuple())


class Fiwalkxml(xml.sax.ContentHandler):
    """
    This class converts fiwalk xml to a list.
    """

    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.key = None
        self.start = False

    def startElement(self, name, attrs):
        if name == "fileobject":
            self.start = True
            files.append({})
        if name == "byte_runs":
            files[-1]["byte_runs"] = []
        if name == "byte_run":
            files[-1]["byte_runs"].append({})
            names = attrs.getNames()
            for name in names:
                if attrs.getValue(name).isnumeric():
                    files[-1]["byte_runs"][-1][name] = int(
                        attrs.getValue(name))
                else:
                    files[-1]["byte_runs"][-1][name] = attrs.getValue(name)
        else:
            if self.start:
                self.key = name

    def characters(self, content):
        if self.key is not None:
            if not content.isspace() and content.isnumeric():
                files[-1][self.key] = int(content)
                self.key = None
            elif not content.isspace() and not content.isnumeric():
                if self.key == 'filename':
                    files[-1][self.key] = content
                    self.key = None
                else:
                    files[-1][self.key] = content
                    self.key = None


def fiwalk_xml(xmlfile):
    '''
    Convert the xml to a python list of dictionaries
    '''
    global files
    command = static.commands['validator']
    try:
        files = []
        output = execute(command.format(static.xsdfile, xmlfile))
        if ' valid' in output:
            source = open(xmlfile)
            xml.sax.parse(source, Fiwalkxml())
            del files[0]
        else:
            pass  # logging
        return files
    except Exception as e:
        message("Runtime error during handeling of fiwalk xml.",
                log='error', display=False)
        logger.error(e, exc_info=True)
        message("\nRuntime error occurred, check log: " +
                config.logfile, log=None, display=True)
        exit()


def clean_file_names(files):
    '''
    Filter out fields that are not necessary
    '''
    try:
        for file in files:

            current = str(file['filename']).split('/')[-1].lower()
            if '.' not in current:
                file['extlen'] = 0
                file['filename'] = ''
                continue

            current = current.split('.')[-1]
            extlen = len(current)
            if extlen <= 3:
                file['extlen'] = extlen
                file['filename'] = current
                continue

            name = ''
            for ext in static.extensions:
                if current == ext:
                    name = ext
                    break
            file['filename'] = name
            file['extlen'] = extlen

        return files
    except Exception as e:
        message("Runtime error during cleaning of file names.",
                log='error', display=False)
        logger.error(e, exc_info=True)
        message("\nRuntime error occurred, check log: " +
                config.logfile, log=None, display=True)
        exit()


def save_object(name, object):
    '''
    Serialize an python object to a file
        name: filename to save to
        object: python object to save
    '''
    try:
        cwd = os.getcwd()
        fullpath = cwd + "/prifiwalk/data/states/" + name
        with open(fullpath, 'wb') as f:
            logger.info('Saved state : ' + fullpath)
            pickle.dump(object, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        message("Runtime error during save of python object.",
                log='error', display=False)
        logger.error(e, exc_info=True)
        message("\nRuntime error occurred, check log: " +
                config.logfile, log=None, display=True)
        exit()


def restore_object(name):
    '''
    Restore a serialized python object
        fullpath: path and file name to restore
        return: a python object
    '''
    try:
        cwd = os.getcwd()
        fullpath = cwd + "/prifiwalk/data/states/" + name
        with open(fullpath, 'rb') as f:
            logger.info('Restored state : ' + fullpath)
            return pickle.load(f)
    except Exception as e:
        message("Runtime error during restoring of python object.",
                log='error', display=False)
        logger.error(e, exc_info=True)
        message("\nRuntime error occurred, check log: " +
                config.logfile, log=None, display=True)
        exit()


def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def message(msg, log='info', display=False):
    if isinstance(msg, str):
        msg = [msg]
    for m in msg:
        if log == 'info':
            logger.info(m)
        elif log == 'error':
            logger.error(m)
        if display:
            print(m)
