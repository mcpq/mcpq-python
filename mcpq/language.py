from locale import getlocale as _getlocale

LOCALE_OVERWRITE: str | None = None
"""overwrite locale that should be used instead of module `locale`, e.g., ``"de_DE"`` or ``"en_US"``"""


def use_german():
    """Whether to use german for some translatable strings (based on locale).

    If you want to change the locale (whether to use german):

    .. code-block:: python

       import locale
       locale.setlocale(locale.LC_ALL, ("de_DE", "utf-8"))  # switch to german
       locale.setlocale(locale.LC_ALL, ("en_US", "utf-8"))  # switch to english

       # alternatively, an overwrite variable is available in `mcpq.language`
       import mcpq
       mcpq.language.LOCALE_OVERWRITE = "de_DE"  # this trumps the `locale` module
    """
    lc = LOCALE_OVERWRITE or _getlocale()[0]
    if lc is not None:
        lc = lc.lower()
        return lc.startswith("de") or lc.startswith("german")
    return False
