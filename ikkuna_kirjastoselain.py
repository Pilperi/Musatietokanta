import os
import sys
import class_biisit as cb
from class_tiedostopuu import Tiedostopuu
from PyQt5 import Qt, QtCore, QtWidgets, QtGui

os.environ['QT_IM_MODULE'] = 'fcitx' # japski-input
IKKUNAMITAT = [500,700]
PUUMITAT    = [400, 600]
MARGINAALIT = [10,10]
PAATASOT    = 2


class Kansioelementti(Qt.QStandardItem):
	def __init__(self, puu, fonttikoko=12, boldattu=False, vari=(255,255,255)):
		super().__init__()
		fontti = QtGui.QFont("Open Sans", fonttikoko)
		fontti.setBold(boldattu)

		puuteksti = str(puu.kansio)
		# print(puuteksti)

		self.setEditable(False)
		self.setForeground(QtGui.QColor(*vari))
		# self.setForeground(vari)
		self.setFont(fontti)
		self.setText(puuteksti)


class Tiedostoelementti(Qt.QStandardItem):
	def __init__(self, tiedosto, fonttikoko=10, boldattu=False, vari=(255,255,255)):
		super().__init__()
		fontti = QtGui.QFont("Open Sans", fonttikoko)
		fontti.setBold(boldattu)

		if False:
		# if type(tiedosto) is cb.Biisi and tiedosto.biisinimi is not None:
			puuteksti = tiedosto.biisinimi
			if type(tiedosto.raita) is int:
				puuteksti = "{:02d}. {:s}".format(tiedosto.raita, puuteksti)
		else:
			puuteksti = str(tiedosto.tiedostonimi)
		# print(puuteksti)

		self.setEditable(False)
		self.setForeground(QtGui.QColor(*vari))
		# self.setForeground(vari)
		self.setFont(fontti)
		self.setText(puuteksti)


class Selausikkuna(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Musiikkikirjastoselain")
		self.resize(IKKUNAMITAT[0], IKKUNAMITAT[1])
		self.setMinimumSize(IKKUNAMITAT[0], IKKUNAMITAT[1])
		self.setMaximumSize(IKKUNAMITAT[0], IKKUNAMITAT[1])

		# Tekstikenttä
		self.nimihaku = QtWidgets.QLineEdit(self)
		self.nimihaku.setGeometry(QtCore.QRect(10, 35, 205, 35))
		self.nimihaku.setObjectName("nimihaku")
		self.nimihaku.setClearButtonEnabled(True)
		self.nimihaku.setText("Artistin nimi")
		self.nimihaku.selectAll()
		self.nimihaku.setCompleter(None)

		# Tekstikentän otsikkoteksti
		self.label_nimihaku = QtWidgets.QLabel(self)
		self.label_nimihaku.setGeometry(QtCore.QRect(10, 10, 205, 35))
		# self.label_nimihaku.setFrameShape(QtWidgets.QFrame.Box)
		self.label_nimihaku.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
		self.label_nimihaku.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
		self.label_nimihaku.setText("Artistin nimi")

		# Hakunappi
		self.etsi = QtWidgets.QPushButton(self)
		self.etsi.setGeometry(QtCore.QRect(205, 35, 100, 35))
		self.etsi.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.etsi.setFocusPolicy(QtCore.Qt.NoFocus)
		self.etsi.setText("Etsi")
		self.etsi.setShortcut("Return")     # normi
		# self.Etsi.setShortcut("Enter")    # kp
		# self.Etsi.setObjectName("pushButton")
		self.etsi.clicked.connect(self.hae)

		self.puu = QtWidgets.QTreeView(self)
		self.puu.setGeometry(QtCore.QRect(MARGINAALIT[0], IKKUNAMITAT[1]-MARGINAALIT[1]-PUUMITAT[1], PUUMITAT[0], PUUMITAT[1]))
		self.puu.setHeaderHidden(True)

		self.puumalli = Qt.QStandardItemModel()
		self.juurisolmu = self.puumalli.invisibleRootItem()

		self.tiedostopuu = Tiedostopuu(tiedostotyyppi=cb.Biisi)
		tietokanta = open("musiikit.tietokanta", "r")
		self.tiedostopuu.lue_tiedostosta(tietokanta)
		tietokanta.close()
		self.kansoita_puu(self.tiedostopuu)

		self.puu.setModel(self.puumalli)
		self.puu.expand(self.puumalli.index(0,0))

	def kansoita_puu(self, puu, juuri=0, edellinen=None):
		'''
		Täytä puu annetun Tiedostopuun sisällöllä,
		boldaa ylimpien tasojen elementit.
		'''
		fkoko = 10
		if juuri < PAATASOT:
			fkoko = 12

		# Elementin väri
		r = min(255,max(255+(-1+2*(juuri%2))*juuri*25, 0))
		g = min(255,max(255+(1-2*(juuri%2))*juuri*25, 0))
		b = min(255,max(255-juuri*25, 0))
		elementti = Kansioelementti(puu, fonttikoko=fkoko, vari=(r, g, b))
		if edellinen is None:
			edellinen = self.juurisolmu
		edellinen.appendRow(elementti)
		for alikansio in puu.alikansiot:
			self.kansoita_puu(alikansio, juuri+1, elementti)
		for biisi in puu.tiedostot:
			biisielementti = Tiedostoelementti(biisi)
			elementti.appendRow(biisielementti)

	def hae(self):
		'''
		Suorita haku.子
		'''
		hakudikti = {}
		oli_tuloksia = False
		# Sarjan nimi
		artistinnimessa = None
		if self.nimihaku.text() and self.nimihaku.text() != "Artistin nimi":
			artistinnimessa = self.nimihaku.text().split(" ")
		print(f"artisti: {artistinnimessa}")
		hakudikti = {
					"ehtona_ja":     False,
					"artistissa":    artistinnimessa,
					# "biisissa":      ["ノゾム", "神"],
					# "albumissa":     ["神"],
					# "tiedostossa":   ["eroge"],
					# "raitanumero":   (1,3)
					}
		haettavaa = any([hakudikti[a] is not None for a in hakudikti])
		if haettavaa:
			haku = cb.Hakukriteerit(hakudikti)
			oli_tuloksia, tulokset = haku.etsi_tietokannasta(self.tiedostopuu)
			# print(oli_tuloksia)
			if oli_tuloksia:
				self.juurisolmu.removeRow(0)
				self.kansoita_puu(tulokset)
				self.puu.setModel(self.puumalli)
				self.puu.expandAll()
		if not haettavaa or not oli_tuloksia:
			self.juurisolmu.removeRow(0)
			self.kansoita_puu(self.tiedostopuu)
			self.puu.setModel(self.puumalli)
			self.puu.expand(self.puumalli.index(0,0))


if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	ikkuna = Selausikkuna()
	ikkuna.show()

	sys.exit(app.exec_())