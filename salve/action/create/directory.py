from salve import logger
from salve.action.base import Action
from salve.action.create.base import CreateAction

from salve.filesys import access_codes
from salve.context import ExecutionContext


class DirCreateAction(CreateAction):
    """
    An action to create a directory.
    """
    def __init__(self, dst, file_context):
        """
        DirCreateAction constructor.

        Args:
            @dst
            Destination path.
            @file_context
            The FileContext.
        """
        Action.__init__(self, file_context)
        self.dst = dst

    def __str__(self):
        return ("DirCreateAction(dst=" + self.dst + ",context=" +
                repr(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        """
        Checks if the target dir already exists, or if its parent is writable.
        """
        # transition to the action verification phase,
        # confirming execution will work
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        def writable_target():
            """
            Checks if the target is in a writable directory.
            """
            ancestor = filesys.get_existing_ancestor(self.dst)
            return filesys.access(ancestor, access_codes.W_OK)

        logstr = 'DirCreate: Checking if target exists, \"%s\"' % self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        # creation of existing dirs is always OK
        if filesys.exists(self.dst):
            return self.verification_codes.OK

        logstr = 'DirCreate: Checking target is writable, \"%s\"' % self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        if not writable_target():
            return self.verification_codes.UNWRITABLE_TARGET

        return self.verification_codes.OK

    def execute(self, filesys):
        """
        Create a directory and any necessary parents.
        """
        vcode = self.verify_can_exec(filesys)

        if vcode == self.verification_codes.UNWRITABLE_TARGET:
            logstr = ("DirCreate: Non-Writable target dir \"%s\"" %
                      self.dst)
            logger.warn('{0}: {1}'.format(self.file_context, logstr))
            return

        # transition to the execution phase
        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logstr = 'Performing Directory Creation of \"%s\"' % self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        # make the directory
        filesys.mkdir(self.dst)
