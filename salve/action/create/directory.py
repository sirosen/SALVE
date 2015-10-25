from salve import logger
from salve.action.create.base import CreateAction

from salve.context import ExecutionContext


class DirCreateAction(CreateAction):
    """
    An action to create a directory.
    """
    def __str__(self):
        return ("DirCreateAction(dst=" + self.dst + ",context=" +
                repr(self.file_context) + ")")

    def verify_can_exec(self, filesys):
        """
        Checks if the target dir already exists, or if its parent is writable.
        """
        ExecutionContext().transition(ExecutionContext.phases.VERIFICATION)

        logstr = 'DirCreate: Checking if target exists, \"%s\"' % self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        # creation of existing dirs is always OK
        if filesys.exists(self.dst):
            return self.verification_codes.OK

        logstr = 'DirCreate: Checking target is writable, \"%s\"' % self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        if not filesys.writable_path_or_ancestor(self.dst):
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

        ExecutionContext().transition(ExecutionContext.phases.EXECUTION)

        logstr = 'Performing Directory Creation of \"%s\"' % self.dst
        logger.info('{0}: {1}'.format(self.file_context, logstr))

        # make the directory
        filesys.mkdir(self.dst)
