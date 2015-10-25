# python 2/3 compatible use of configparser
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from salve import paths


class SALVEConfigParser(configparser.ConfigParser):
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
        configparser.ConfigParser.__init__(self)

        # first read the defaults
        # either read the user's rc file, if not given a filename
        # or read the given file
        filenames = [paths.get_default_config(),
                     paths.pjoin(userhome, '.salverc'),
                     filename]
        # filter out filename if it is None
        self.read(f for f in filenames if f is not None)
