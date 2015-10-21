# python 2/3 compatible use of configparser
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import logging
import os
import string

import salve
import salve.log

from salve import ugo
from salve.context import FileContext, ExecutionContext
from salve.exceptions import SALVEException

from .parser import SALVEConfigParser

SALVE_ENV_PREFIX = 'SALVE_'


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
        self.env['SALVE_USER_PRIMARY_GROUP'] = \
            ugo.get_group_from_username(user)

        # track the filename that's being used, for error out
        self.filename = filename

        # read the configuration, taking ~userhome/.salverc if there is
        # no file
        try:
            conf = SALVEConfigParser(userhome, filename)
        except configparser.Error as e:
            raise SALVEException(
                'Encountered an error while parsing your ' +
                'configuration file(s).\n%s' % e.message,
                FileContext(filename))
        sections = conf.sections()
        # the loaded configuration is stored in the config object as a
        # dict mapping section names to a dict of (key,value) items
        # all keys are converted the lowercase for uniformity
        self.attributes = dict((s.lower(),
                                dict((k.lower(), v)
                                     for (k, v)
                                     in conf.items(s)))
                               for s in sections)

        self._apply_environment_overrides()

        self._set_context_globals()

    def _apply_environment_overrides(self):
        # Grab all of the mappings from the environment that
        # start with the SALVE prefix and are uppercase
        # prevents XYz=a and XYZ=b from being ambiguous
        salve_env = dict((k, self.env[k]) for k in self.env
                         if k.startswith(SALVE_ENV_PREFIX)
                         and k.isupper())

        # Walk through these environment variables and overwrite
        # the existing configuration with them if present
        prefixes = dict((SALVE_ENV_PREFIX + s.upper(), s)
                        for s in self.attributes)

        for key in salve_env:
            for p in prefixes:
                if key.startswith(p):
                    # pull out the dictionary of values in the matching
                    # section
                    subdict = self.attributes[prefixes[p]]
                    # environment vars are uppercase
                    subkey = key[(len(p) + 1):].lower()
                    subdict[subkey] = salve_env[key]

    def _set_context_globals(self):
        # set globals in the execution context as shared variables
        for key in self.attributes['global']:
            # do templating to the string value to put environment
            # variables in place
            val = self.template(self.attributes['global'][key])

            # special handling for the run_log
            # convert to a file open in 'w' mode
            if key == 'run_log':
                salve.log.add_logfile(salve.logger, logging.NOTSET, val)

            # special handling for the log_level
            # convert to a log level from logging
            if key == 'log_level':
                val = salve.log.str_to_level(val)
                salve.logger.setLevel(val)

            ExecutionContext()[key] = val

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

        # set any unset attrs in the config
        for key in relevant_attrs:
            if key not in block.attrs:
                block[key] = relevant_attrs[key]

        # set any remaining unspecified attributes using defaults
        for key in self.attributes['default']:
            if key not in block.attrs:
                block[key] = self.attributes['default'][key]

        # template any block attrs
        for key in block.attrs:
            block[key] = self.template(block[key])
