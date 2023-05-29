from gym.error import ResetNeeded


class BeamNGEnvsError(Exception):
    pass


class OutOfTimeException(BeamNGEnvsError):
    pass


class AlreadyFinishedException(BeamNGEnvsError):
    pass


class ResetNeededException(BeamNGEnvsError, ResetNeeded):
    pass
