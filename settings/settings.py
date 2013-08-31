#!/usr/bin/python

from ConfigParser import ConfigParser
from os.path import expanduser

DEFAULT_CONFIG_FILE = '/etc/salve-config/salve_basic.ini'
RC_CONFIG_FILE = expanduser('~/.salverc')

SALVE_ENV_PREFIX = 'SALVE_'


class SALVEConfigParser(ConfigParser):
    """
    The SALVE configuration parser.
    Loads default values, then attempts to look up
    the current user's rc file for overwrites to those
    values.
    """
    def __init__(self):
        ConfigParser.__init__(self, filename=None)
        if not filename:
            self.read(DEFAULT_CONFIG_FILE)
            self.read(RC_CONFIG_FILE)
        else:
            self.read(filename)

class SALVEConfig(object):
    """
    SALVE's configuration is stored statefully as
    an object. In this way, configuration can be modified
    if we support an interactive mode in the future.
    SALVE will also load special values from the environment
    so that users can make ephemeral changes to configuration
    without modifying the config files. They also offer a way
    of guaranteeing that the configuration values are as desired
    without inspecting the files.
    """
    def __init__(self, filename=None):
        from os import environ
        self.filename = filename
        conf = SALVEConfigParser(filename)
        sections = conf.sections()
        self.conf = {s:dict(conf.items(s)) for s in sections}

        # Grab all of the mappings from the environment that
        # start with the SALVE prefix and are uppercase
        # prevents XYz=a and XYZ=b from being ambiguous
        env = {k:environ[k] for k in environ
               if k.startswith(SALVE_ENV_PREFIX)
                  and k.isupper()}

        # Walk through these environment variables and overwrite
        # the existing configuration with them if present
        prefixes = {(SALVE_ENV_PREFIX + '_' + s.upper()):s
                    for s in sections}
        for key in env:
            for p in prefixes:
                if key.startswith(p):
                    # pull out the dictionary of values in the matching
                    # section
                    subdict = self.conf[prefixes[p]]
                    # environment vars are uppercase
                    subkey = key[len(p):].lower()
                    subdict[subkey] = env[key]

        # preserve the order of the manifests in the file,
        # as it may be important to semantics
        self.manifests = []
        man_file = self.conf['metadata']['known_manifests']
        with open(man_file,'r') as f:
            for line in f:
                self.manifests.append(line.strip())
