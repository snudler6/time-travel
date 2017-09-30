"""Utils for time travel testings."""


def _t(rel=0.0):
    """Return an absolute time from the relative time given.

    The minimal allowed time in windows is 86400 seconds, for some reason. In
    stead of doing the arithmetic in the tests themselves, this function should
    be used.

    The value `86400` is exported in `time_travel.MIN_START_TIME`, but I shant
    use it for it is forbidden to test the code using the code that is being
    tested.
    """
    return 86400.0 + rel
