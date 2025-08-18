# script_descobre_monitores.py
import mss
import pprint # Usado para imprimir dicionários de forma mais legível

with mss.mss() as sct:
    monitores = sct.monitors
    print("Monitores detectados:")
    pprint.pprint(monitores)