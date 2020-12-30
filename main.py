import sys
from PyQt5 import QtWidgets
from ikkuna_kirjastoselain import Selausikkuna

if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	ikkuna = Selausikkuna()
	ikkuna.show()
	sys.exit(app.exec_())
