from salve.action.base import Action


class ActionList(Action):
    """
    An ActionList, often referred to internally as an "AL", is one of
    the basic Action types.

    It is used to provide a sequential list of other actions to execute.
    """
    def __init__(self, act_lst, file_context):
        """
        ActionList constructor.

        Args:
            @act_list
            A list of Action objects. No checking is performed, the
            class assumes that what it is handed is in fact a list of
            Action objects.

            @file_context
            The FileContext.
        """
        Action.__init__(self, file_context)
        self.actions = act_lst

    def __iter__(self):
        """
        Iterating over an AL iterates over its sub-actions.
        """
        for act in self.actions:
            yield act

    def __str__(self):
        return '{0}([{1}],context={2!r})'.format(
            self.prettyname, ','.join(str(a) for a in self.actions),
            self.file_context)

    def append(self, act):
        """
        Append a new Action to the AL.

        Args:
            @act
            The action to append.
        """
        assert isinstance(act, Action)
        self.actions.append(act)

    def prepend(self, act):
        """
        Prepend a new Action to the AL.

        Args:
            @act
            The action to prepend.
        """
        assert isinstance(act, Action)
        self.actions.insert(0, act)

    def execute(self, filesys):
        """
        Execute the AL. Consists of a walk over the AL executing each
        of its sub-actions.

        Args:
            @filesys
            The filesystem on which the action should be executed. Used to
            transition actions between operation on the real and virtualized
            filesystem.
        """
        for act in self:
            act(filesys)


def action_list_merge(original, new, prepend=False):
    """
    A helper method to merge actions into ALs when it is unknown
    if the original action is an AL. Returns the merged action,
    and makes no guarantees about preserving the originals.

    Args:
        @original
        The original action to be extended with @new
        @new
        The action being appended or prepended to @original

    KWArgs:
        @prepend=False
        When True, prepend @new to @original. When False, append
        instead.
    """
    # if original is falsey, then @new is the entire "merged" action --
    # typically useful to do an action_list_merge(None, XYZ)
    if not original:  # pragma: no cover
        return new

    # otherwise, check if @original is an AL, and convert
    # it into one if it is not
    if not isinstance(original, ActionList):
        original = ActionList([original], original.file_context)

    # prepend or append @new, as per the @prepend arg
    if prepend:
        original.prepend(new)
    else:
        original.append(new)

    # original action may have been modified or replaced, return the result
    # either way
    return original
