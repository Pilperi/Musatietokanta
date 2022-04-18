import sys
import logging
import argparse
from PyQt5 import QtWidgets

LOGGER = logging.getLogger("musatietokanta")
parseri = argparse.ArgumentParser(description='Musan latailu etänä.')
parseri.add_argument('-v', '--verboosi', action='count', default=0)
args = parseri.parse_args()
if args.verboosi:
    handleri = logging.StreamHandler()
    formaatti = logging.Formatter(
        '%(asctime)s %(name)s [%(levelname)s]: %(message)s')
    handleri.setFormatter(formaatti)
    LOGGER.addHandler(handleri)
    LOGGER.setLevel("DEBUG")
    LOGGER.debug("Loggeri asetettu rinttailemaan.")

from musatietokanta.ikkuna_kirjastoselain import Selausikkuna

def main():
	app = QtWidgets.QApplication([])
	ikkuna = Selausikkuna()
	ikkuna.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
