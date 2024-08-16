"""In diesem Modul befindet sich die ChatCmd Klasse,
mit der man leicht Chat-Nachrichten in Befehle umwandeln kann.

Zunächst musst du deine eigene Klasse von ChatCmd Ableiten:

>>> from mcpi.minecraft import Minecraft
>>> mc = Minecraft.create()

>>> from extra.chatcmd import ChatCmd

>>> class MeinEigenerChat(ChatCmd):
>>>     def do_meinbefehl(self, spieler, *argumente):
>>>         "Dieser Befehl macht etwas tolles!"
>>>         ...

>>> chatbot = MeinEigenerChat(mc)
>>> chatbot.schleife("Bitte gib deine Befehle ein!")

Jetzt können folgende Befehle im Minecraft Chat eingegeben werden:

!meinbefehl hier sind die argumente

oder:

!help
"""

from __future__ import annotations

import shlex
import time
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import Minecraft, Player

from .. import text


class ChatCmd:
    prefix = "!"
    wartezeit = 0.1
    kein_befehl = text.ROT + "Es gibt keinen Befehl: " + text.GOLD
    keine_hilfe = text.ROT + "Keine Hilfe für Befehl: " + text.GOLD
    intro_hilfe = "Alle Befehle:"
    intro_hilfe_doc = "Dokumentierte Befehle (hilfe <befehl>):"
    intro_hilfe_nodoc = "Undokumentierte Befehle:"
    hilfe_trenner = "="
    hilfe_trenner_farbe = ""
    hilfe_befehl_farbe = text.GOLD + text.FETT
    hilfe_text_farbe = text.GRAU
    text_reset = text.RESET
    fange_fehler = True
    fange_fehler_text = text.ROT + "Der Befehl hat nicht funktioniert!"
    versuche_zahlen_parsen = True

    def __init__(self, mc: Minecraft):
        self.mc = mc

    @staticmethod
    def parse_zu_zahl(word: str):
        try:
            return int(word)
        except ValueError:
            try:
                return float(word)
            except ValueError:
                return word

    def schreibe(self, nachricht: str):
        self.mc.postToChat(nachricht)

    def pre_schleife(self):
        pass

    def schleife(self, intro: str | None = None):
        if intro is not None:
            self.schreibe(intro)
        self.pre_schleife()
        stop = False
        while not stop:
            events = self.mc.pollChatEvents()
            for event in events:
                nachricht = event.message.rstrip("\r\n")
                if nachricht.startswith(self.prefix):
                    nachricht = self.pre_befehl(event.player, nachricht)
                    stop = self.befehl(event.player, nachricht)
                    stop = self.post_befehl(stop, event.player, nachricht)
            else:
                time.sleep(self.wartezeit)

        self.post_schleife()

    def post_schleife(self):
        pass

    def pre_befehl(self, spieler: Player, nachricht: str):
        return nachricht

    def befehl(self, spieler: Player, nachricht: str):
        command, argumente, nachricht = self.parse(nachricht)
        if command is None:
            return False
        try:
            func = getattr(self, "do_" + command)
        except AttributeError:
            return self.default(spieler, nachricht)
        try:
            if self.versuche_zahlen_parsen:
                return func(spieler, *map(self.parse_zu_zahl, argumente))
            return func(spieler, *argumente)
        except Exception:
            if not self.fange_fehler:
                raise
            traceback.print_exc()
            self.schreibe(self.fange_fehler_text)

    def post_befehl(self, stop: bool, spieler: Player, nachricht: str):
        return stop

    def default(self, spieler: Player, nachricht: str):
        self.schreibe(self.kein_befehl + shlex.split(nachricht)[0])
        return False

    def parse(self, nachricht: str):
        nachricht = nachricht[len(self.prefix) :].strip()
        if nachricht:
            args = shlex.split(nachricht)
            cmd, args = args[0], args[1:]
            return cmd, args, nachricht
        return None, None, nachricht

    def do_hilfe(self, spieler: Player, *args):
        "Liste alle verfügbaren Befehle mit 'hilfe' oder detaillierte Hilfe mit 'hilfe befehl'"
        return self.do_help(spieler, *args)

    def do_help(self, spieler: Player, *args):
        "List available commands with 'help' or detailed help with 'help cmd'"
        if args:
            arg = args[0]
            try:
                doc = getattr(self, "do_" + arg).__doc__
                doc = " ".join(map(str.strip, doc.split("\n")))
                if doc:
                    hilfe = self.hilfe_befehl_farbe + arg + ": " + self.text_reset
                    self.schreibe(hilfe + self.hilfe_text_farbe + str(doc))
                    return
            except AttributeError:
                pass
            self.schreibe(str(self.keine_hilfe + arg))
        else:
            names = dir(self.__class__)
            cmds_doc = []
            cmds_undoc = []
            names.sort()
            prevname = ""
            for name in names:
                if name[:3] == "do_":
                    if name == prevname:
                        continue
                    prevname = name
                    cmd = name[3:]
                    if getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)

            colsize = max(len(self.intro_hilfe_doc), len(self.intro_hilfe_nodoc))
            self.schreibe(str(self.intro_hilfe))
            self.print_topics(self.intro_hilfe_doc, cmds_doc, colsize)
            self.print_topics(self.intro_hilfe_nodoc, cmds_undoc, colsize)

    def print_topics(self, header, cmds, maxcol):
        if cmds:
            self.schreibe(str(header))
            if self.hilfe_trenner:
                self.schreibe(self.hilfe_trenner_farbe + (str(self.hilfe_trenner) * len(header)))
            self.columnize(cmds, maxcol - 1)

    def columnize(self, list, displaywidth=80):
        if not list:
            self.schreibe("<keine Befehle>")
            return

        nonstrings = [i for i in range(len(list)) if not isinstance(list[i], str)]
        if nonstrings:
            raise TypeError("list[i] not a string for i in %s" % ", ".join(map(str, nonstrings)))
        size = len(list)
        if size == 1:
            self.schreibe(self.hilfe_befehl_farbe + str(list[0]))
            return
        # Try every row count from 1 upwards
        for nrows in range(1, len(list)):
            ncols = (size + nrows - 1) // nrows
            colwidths = []
            totwidth = -2
            for col in range(ncols):
                colwidth = 0
                for row in range(nrows):
                    i = row + nrows * col
                    if i >= size:
                        break
                    x = list[i]
                    colwidth = max(colwidth, len(x))
                colwidths.append(colwidth)
                totwidth += colwidth + 2
                if totwidth > displaywidth:
                    break
            if totwidth <= displaywidth:
                break
        else:
            nrows = len(list)
            ncols = 1
            colwidths = [0]
        for row in range(nrows):
            texts = []
            for col in range(ncols):
                i = row + nrows * col
                if i >= size:
                    x = ""
                else:
                    x = list[i]
                texts.append(x)
            while texts and not texts[-1]:
                del texts[-1]
            for col in range(len(texts)):
                texts[col] = texts[col].ljust(colwidths[col])
            self.schreibe(self.hilfe_befehl_farbe + str("  ".join(texts)))
