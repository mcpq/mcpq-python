from ._proto import minecraft_pb2 as pb
from .language import use_german

__all__ = [
    "MCPQError",
    "UnknownError",
    "MissingArgument",
    "InvalidArgument",
    "NotImplementedOrAvailable",
    "WorldNotFound",
    "PlayerNotFound",
    "BlockTypeNotFound",
    "EntityTypeNotFound",
    "EntityNotSpawnable",
    "EntityNotFound",
]


class MCPQError(Exception):
    pass


class UnknownError(MCPQError):
    pass


class MissingArgument(MCPQError):
    pass


class InvalidArgument(MCPQError):
    pass


class NotImplementedOrAvailable(MCPQError):
    pass


class WorldNotFound(MCPQError):
    pass


class PlayerNotFound(MCPQError):
    pass


class BlockTypeNotFound(MCPQError):
    pass


class EntityTypeNotFound(MCPQError):
    pass


class EntityNotSpawnable(MCPQError):
    pass


class EntityNotFound(MCPQError):
    pass


# Mapping must correspond to .proto errors
exc_de = {
    1: (
        UnknownError,
        "Ein unbekannter Fehler ist aufgetreten",
        "Ein unbekannter Fehler ist mit '{}' aufgetreten",
    ),
    2: (
        MissingArgument,
        "Ein Argument war nicht gesetzt oder hat gefehlt",
        "Das Argument '{}' war nicht gesetzt oder hat gefehlt",
    ),
    3: (
        InvalidArgument,
        "Ein Argument war ungültig oder wurde falsch verwendet",
        "Das Argument '{}' war ungültig oder wurde falsch verwendet",
    ),
    4: (
        NotImplementedOrAvailable,
        "Die Verwendung einer Funktion oder eines Feldes wurde noch nicht implementiert",
        "Die Verwendung von Funktion oder Feld '{}' wurde noch nicht implementiert",
    ),
    5: (
        WorldNotFound,
        "Eine angegebene Welt konnte nicht gefunden werden",
        "Die Welt '{}' konnte nicht gefunden werden",
    ),
    6: (
        PlayerNotFound,
        "Ein Spieler konnte nicht gefunden werden (vielleicht offline?)",
        "Der Spieler '{}' konnte nicht gefunden werden (vielleicht offline?)",
    ),
    7: (
        BlockTypeNotFound,
        "Ein angegebener Blocktyp konnte nicht gefunden werden",
        "'{}' entspricht keinem bekannten Blocktyp",
    ),
    8: (
        EntityTypeNotFound,
        "Ein angegebener Wesentyp konnte nicht gefunden werden",
        "'{}' entspricht keinem bekannten Wesentyp",
    ),
    9: (
        EntityNotSpawnable,
        "Ein angegebenes Wesen ist nicht spawnbar",
        "'{}' ist nicht spawnbar",
    ),
    10: (
        EntityNotFound,
        "Ein angegebenes Wesen konnte nicht gefunden werden",
        "Das Wesen mit id '{}' konnte nicht gefunden werden",
    ),
}

# Mapping must correspond to .proto errors
exc_en = {
    1: (
        UnknownError,
        "An unknown error occured",
        "An unknown error occured with '{}'",
    ),
    2: (
        MissingArgument,
        "An argument was missing",
        "The argument '{}' was missing",
    ),
    3: (
        InvalidArgument,
        "An argument was invalid or was used incorrectly",
        "The argument '{}' was invalid or was used incorrectly",
    ),
    4: (
        NotImplementedOrAvailable,
        "The usage of a function or of an attribute was not implemented",
        "The usage of the function or attribute '{}' was not implemented",
    ),
    5: (
        WorldNotFound,
        "A specified world does not exist",
        "The world '{}' does not exist",
    ),
    6: (
        PlayerNotFound,
        "A player does not exist (maybe offline?)",
        "The player '{}' does not exist (maybe offline?)",
    ),
    7: (
        BlockTypeNotFound,
        "A specified block type does not exist",
        "The block type '{}' does not exist",
    ),
    8: (
        EntityTypeNotFound,
        "A specified entity type does not exist",
        "The entity type '{}' does not exist",
    ),
    9: (
        EntityNotSpawnable,
        "A specified entity is not spawnable",
        "The entity '{}' is not spawnable",
    ),
    10: (
        EntityNotFound,
        "A specified entity does not exist",
        "The entity with id '{}' does not exist",
    ),
}


def exception_from_status(status: pb.Status) -> Exception:
    exc = exc_de if use_german() else exc_en
    if status.code in exc.keys():
        e, default, default_extra = exc[status.code]
        if status.extra:
            return e(default_extra.format(status.extra))
        else:
            return e(default)
    else:
        return NotImplementedError(f"The error code {status.code} is not implemented")


def raise_on_error(status: pb.Status) -> None:
    if status.code:
        raise exception_from_status(status)
