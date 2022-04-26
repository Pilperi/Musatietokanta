import sys
import logging
import argparse
from PyQt5 import QtWidgets

import musatietokanta
from musatietokanta.ikkuna_kirjastoselain import Selausikkuna

def main():
	app = QtWidgets.QApplication([])
	ikkuna = Selausikkuna()
	ikkuna.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
