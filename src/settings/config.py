#!/usr/bin/python

from ConfigParser import ConfigParser
import os, string

import src.block.manifest_block
import src.util.locations as locations
import src.util.ugo as ugo

SALVE_ENV_PREFIX = 'SALVE_'


class SALVEConfigParser(ConfigParser):
    """
    The SALVE configuration parser.
    Loads default values, then attempts to look up
    the current user's rc file for overwrites to those
    values.
    """
    def __init__(self, userhome, filename):
        """
        SALVEConfigParser constructor.
        Creates a ConfigParser specialized for SALVE.

        Args:
            @userhome
            The home directory of the running user ($SUDO_USER if
            running under 'sudo').
            @filename
            The name of a specific config file to load.
        """
        # create a config parser
        ConfigParser.__init__(self)

        # first read the defaults
        # either read the user's rc file, if not given a filename
        # or read the given file
        filenames = [locations.get_default_config(),
                     os.path.join(userhome,'.salverc'),
                     filename]
        # filter out filename if it is None
        self.read(f for f in filenames if f is not None)

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
        """
        SALVEConfig constructor.

        KWArgs:
            @filename
            The specific config file to create Config from. Defaults to
            None, which indicates that the defaults and ~/.salverc
            should be used without any supplement.
        """
        # get the user that we're running as, even if invoked with sudo
        user = os.environ['USER']
        if 'SUDO_USER' in os.environ:
            user = os.environ['SUDO_USER']
        userhome = os.path.expanduser('~' + user)

        # copy the environ to a dictionary, because we don't want to
        # modify the environment just to track things like USER and
        # HOME when working around invocation with sudo
        self.env = {}
        for k in os.environ:
            self.env[k] = os.environ[k]
        # in self.env, reset USER and HOME to the desired values
        # along with SALVE_USER_PRIMARY_GROUP
        self.env['USER'] = user
        self.env['HOME'] = userhome
        self.env['SALVE_ROOT'] = locations.get_salve_root()
        self.env['SALVE_USER_PRIMARY_GROUP'] = ugo.get_group_from_username(user)

        # track the filename that's being used, for error out
        self.filename = filename

        # read the configuration, taking ~userhome/.salverc if there is
        # no file
        conf = SALVEConfigParser(userhome,filename)
        sections = conf.sections()
        # the loaded configuration is stored in the config object as a
        # dict mapping section names to a dict of (key,value) items
        # all keys are converted the lowercase for uniformity
        self.attributes = dict((s.lower(),
                                dict((k.lower(),v)
                                     for (k,v)
                                     in conf.items(s)))
                               for s in sections)

        # Grab all of the mappings from the environment that
        # start with the SALVE prefix and are uppercase
        # prevents XYz=a and XYZ=b from being ambiguous
        salve_env = dict((k,os.environ[k]) for k in os.environ
                          if k.startswith(SALVE_ENV_PREFIX)
                             and k.isupper())

        # Walk through these environment variables and overwrite
        # the existing configuration with them if present
        prefixes = {(SALVE_ENV_PREFIX + s.upper()):s
                    for s in sections}
        for key in salve_env:
            for p in prefixes:
                if key.startswith(p):
                    # pull out the dictionary of values in the matching
                    # section
                    subdict = self.attributes[prefixes[p]]
                    # environment vars are uppercase
                    subkey = key[len(p)+1:].lower()
                    subdict[subkey] = salve_env[key]

        # expand any common settings by templating
        common_attrs = self.attributes['common']
        for key in common_attrs:
            common_attrs[key] = self.template(common_attrs[key])

    def template(self, template_string):
        """
        Given a @template_string, takes the environment stored in the
        SALVE configuration object and uses it to replace placeholders

        Returns a new string in which placeholders have been replaced,
        or raises a KeyError if they are not found.

        Args:
            @template_string
            A string containing variables meant to be replaced with
            environment variables, as represented or overridden in the
            Config.
        """
        temp = string.Template(template_string)
        return temp.substitute(self.env)

    def apply_to_block(self, block):
        """
        Given a @block produced by the parser, takes any settings which
        describe defaults and uses them to populate any missing attrs
        of the block.

        Args:
            @block
            The block to which Config attributes should be applied. The
            general policy is to only apply attributes that are not
            already specified.
        """
        ty = block.block_type.lower()
        relevant_attrs = self.attributes[ty]
        for key in relevant_attrs:
            if key not in block.attrs:
                block.set(key,relevant_attrs[key])
        for key in block.attrs:
            block.set(key,self.template(block.get(key)))
        for key in self.attributes['common']:
            if not block.has(key):
                block.set(key,self.attributes['common'][key])
