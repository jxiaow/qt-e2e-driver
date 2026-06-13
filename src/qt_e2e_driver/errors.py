class QtE2EError(RuntimeError):
    """Base class for qt-e2e-driver failures."""


class E2EConnectionError(QtE2EError):
    """The Python driver could not connect to the Qt test endpoint."""


class E2EInfraError(QtE2EError):
    """The Qt test endpoint responded, but the protocol command failed."""


class EmptyAliasCatalog(E2EInfraError):
    """The Qt test endpoint returned no aliases."""


class DuplicateAliasError(E2EInfraError):
    """The alias catalog contains the same alias more than once."""


class InvalidAliasCatalog(E2EInfraError):
    """The alias catalog payload or one of its entries is malformed."""


class UnknownAliasInCatalog(QtE2EError):
    """A test requested an alias that was not published by list-aliases."""
