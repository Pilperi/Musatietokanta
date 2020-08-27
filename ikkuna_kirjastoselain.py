import os
import sys
import class_biisit as cb
from class_tiedostopuu import Tiedostopuu
from PyQt5 import Qt, QtCore, QtWidgets, QtGui

os.environ['QT_IM_MODULE'] = 'fcitx' # japski-input

# Ikkunan asioiden mitat
IKKUNAMITAT   = [700,700]
MARGINAALIT   = [10,10]
HAKUMITAT     = [MARGINAALIT[0], 205, MARGINAALIT[1], 35]
HAKULABEL     = 20
HAKUNAPPI     = 80
PUUMITAT      = [MARGINAALIT[0], HAKUMITAT[1]*2, 2*MARGINAALIT[1]+HAKUMITAT[2]+HAKUMITAT[3], IKKUNAMITAT[1]-(3*MARGINAALIT[1]+HAKUMITAT[2]+HAKUMITAT[3])]
TAULUKKOMITAT = [PUUMITAT[0]+PUUMITAT[1], IKKUNAMITAT[0]-PUUMITAT[0]-PUUMITAT[1]-MARGINAALIT[0], PUUMITAT[2], 210]
LATAUSNAPPI   = [TAULUKKOMITAT[0], TAULUKKOMITAT[1], TAULUKKOMITAT[2]+TAULUKKOMITAT[3], 50]

# Puun muotoiluparametrit
PAATASOT      = 2


class Kansioelementti(Qt.QStandardItem):
	def __init__(self, puu, fonttikoko=12, boldattu=False, vari=(255,255,255)):
		super().__init__()
		fontti = QtGui.QFont("Open Sans", fonttikoko)
		fontti.setBold(boldattu)

		puuteksti = str(puu.kansio)

		self.setEditable(False)
		self.setForeground(QtGui.QColor(*vari))
		self.setFont(fontti)
		self.setText(puuteksti)
		self.puu = puu

		self.tiedostopolku = self.puu.hae_nykyinen_polku # funktiopointteri

	def __str__(self):
		'''
		Kuvaus kansiosta tietoikkunaan.
		'''
		st  = "Kansio\t{}".format(self.puu.kansio)
		st += "\nSyvyydellä\t{}{}".format(self.puu.syvennystaso, "    (juuri)"*(self.puu.syvennystaso==0))
		lukumaara = self.puu.sisallon_maara()
		st += "\nBiisejä\t{}    ({} + {})".format(lukumaara[0], lukumaara[1], lukumaara[2])
		st += "\nKansioita\t{}".format(len(self.puu.alikansiot))
		return(st)


class Tiedostoelementti(Qt.QStandardItem):
	def __init__(self, tiedosto, fonttikoko=10, boldattu=False, vari=(255,255,255)):
		super().__init__()
		fontti = QtGui.QFont("Open Sans", fonttikoko)
		fontti.setBold(boldattu)

		# if type(tiedosto) is cb.Biisi and tiedosto.biisinimi is not None:
		# 	puuteksti = tiedosto.biisinimi
		# 	if type(tiedosto.raita) is int:
		# 		puuteksti = "{:02d}. {:s}".format(tiedosto.raita, puuteksti)
		# else:
		# 	puuteksti = str(tiedosto.tiedostonimi)
		puuteksti = str(tiedosto.tiedostonimi)

		self.setEditable(False)
		self.setForeground(QtGui.QColor(*vari))
		# self.setForeground(vari)
		self.setFont(fontti)
		self.setText(puuteksti)
		self.tiedosto = tiedosto

	def tiedostopolku(self):
		'''
		Antaa tiedoston polun.
		Vanhempana aina jokin kansio, 
		haetaan siitä kansiopolku ja tiedostosta tiedostonimi.
		'''
		vanhempi = self.parent()
		if vanhempi is not None:
			kansiopolku  = vanhempi.puu.hae_nykyinen_polku()
			tiedostonimi = self.tiedosto.tiedostonimi
			return(os.path.join(kansiopolku, tiedostonimi))
		return(None)

	def __str__(self):
		'''
		Näytä biisin tiedot.
		'''
		st = ""
		st += "{} - {}\n\n\n".format(self.tiedosto.esittaja, self.tiedosto.biisinimi)
		st += "Esittäjä:"
		if self.tiedosto.esittaja:
			st += "\t{}".format(self.tiedosto.esittaja)
		st += "\nKappale:"
		if self.tiedosto.biisinimi:
			st += "\t{}".format(self.tiedosto.biisinimi)
		st += "\nAlbumi:"
		if self.tiedosto.albuminimi:
			st += "\t{}".format(self.tiedosto.albuminimi)
		st += "\nVuosi:"
		if self.tiedosto.vuosi:
			st += "\t{}".format(self.tiedosto.vuosi)
		st += "\nRaita:"
		if self.tiedosto.vuosi:
			st += "\t{}{}".format(self.tiedosto.raita, f"/{self.tiedosto.raitoja}"*(self.tiedosto.raitoja not in [0,None]))
		st += "\nAlb.es.:"
		if self.tiedosto.albumiesittaja:
			st += "\t{}".format(self.tiedosto.albumiesittaja)
		st += "\nLisätty:"
		if self.tiedosto.lisayspaiva:
			pilkottu = self.tiedosto.paivays(self.tiedosto.lisayspaiva)[1]
			st += "\t{:04d}-{:02d}-{:02d} / {:02d}:{:02d}".format(pilkottu[0], pilkottu[1], pilkottu[2], pilkottu[3], pilkottu[4])

		return(st)


class Vaara_monta(QtWidgets.QMessageBox):
	'''
	Danger zone varoitusikkuna,
	ei klikata 10k biisin kansissa vahingossa "lataa"
	ja sit jouduta tappamaan ohjelmaa väkisin kun menis ikuisuus.
	'''
	def __init__(self, biiseja):
		super().__init__()
		self.width  = 500
		self.height = 500
		self.setWindowTitle('Näit biisejä on aika monta')
		self.setText(f'Olet lataamassa {biiseja} biisiä, haluutko oikeesti?')
		self.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
		self.juu = self.button(QtWidgets.QMessageBox.Yes)
		self.juu.setText('Kyllä')
		self.eikyl = self.button(QtWidgets.QMessageBox.No)
		self.eikyl.setText('Emmää joo')
		self.exec_()


class Selausikkuna(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Musiikkikirjastoselain")
		self.resize(IKKUNAMITAT[0], IKKUNAMITAT[1])
		self.setMinimumSize(IKKUNAMITAT[0], IKKUNAMITAT[1])
		self.setMaximumSize(IKKUNAMITAT[0], IKKUNAMITAT[1])

		# Tekstikentän otsikkoteksti
		self.label_nimihaku = QtWidgets.QLabel(self)
		self.label_nimihaku.setGeometry(QtCore.QRect(HAKUMITAT[0], HAKUMITAT[2], HAKUMITAT[1]-HAKUNAPPI, HAKUMITAT[3]))
		# self.label_nimihaku.setFrameShape(QtWidgets.QFrame.Box)
		self.label_nimihaku.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
		self.label_nimihaku.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
		self.label_nimihaku.setText("Vapaahaku")

		# Tekstikenttä
		self.nimihaku = QtWidgets.QLineEdit(self)
		self.nimihaku.setGeometry(QtCore.QRect(HAKUMITAT[0], HAKUMITAT[2]+HAKULABEL, HAKUMITAT[1]-HAKUNAPPI, HAKUMITAT[3]))
		self.nimihaku.setObjectName("nimihaku")
		self.nimihaku.setClearButtonEnabled(True)
		self.nimihaku.setText("Vapaahaku")
		self.nimihaku.selectAll()
		self.nimihaku.setCompleter(None)

		# Hakunappi
		self.etsi = QtWidgets.QPushButton(self)
		self.etsi.setGeometry(QtCore.QRect(HAKUMITAT[0]+HAKUMITAT[1]-HAKUNAPPI, HAKUMITAT[2]+HAKULABEL, HAKUNAPPI, HAKUMITAT[3]))
		self.etsi.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.etsi.setFocusPolicy(QtCore.Qt.NoFocus)
		self.etsi.setText("Etsi")
		self.etsi.setShortcut("Return")     # normi
		# self.Etsi.setShortcut("Enter")    # kp
		# self.Etsi.setObjectName("pushButton")
		self.etsi.clicked.connect(self.hae)

		self.puu = QtWidgets.QTreeView(self)
		self.puu.setGeometry(QtCore.QRect(PUUMITAT[0], PUUMITAT[2], PUUMITAT[1], PUUMITAT[3]))
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
		self.puu.selectionModel().selectionChanged.connect(self.nayta_tiedot)

		# self.taulukko = QtWidgets.QLineEdit(self)
		self.taulukko = QtWidgets.QTextEdit(self)
		self.taulukko.setGeometry(QtCore.QRect(TAULUKKOMITAT[0], TAULUKKOMITAT[2], TAULUKKOMITAT[1], TAULUKKOMITAT[3]))
		self.taulukko.setText("")
		self.taulukko.setReadOnly(True)
		self.taulukko.setAlignment(QtCore.Qt.AlignTop)
		self.taulukko.setWordWrapMode(0)

		# Latausnappi
		self.latausnappi = QtWidgets.QPushButton(self)
		self.latausnappi.setStyleSheet("background-color: #373c41; color: white; font-weight: bold")
		self.latausnappi.setGeometry(QtCore.QRect(LATAUSNAPPI[0], LATAUSNAPPI[2], LATAUSNAPPI[1], LATAUSNAPPI[3]))
		self.latausnappi.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.latausnappi.setFocusPolicy(QtCore.Qt.NoFocus)
		self.latausnappi.setText("Lataa")
		# self.latausnappi.setShortcut("Return")     # normi
		# self.latausnappi.setShortcut("Enter")    # kp
		self.latausnappi.clicked.connect(self.lataa)

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
		sortatutbiisit = sorted(puu.tiedostot, key = lambda t: t.tiedostonimi)
		for biisi in sortatutbiisit:
			biisielementti = Tiedostoelementti(biisi)
			elementti.appendRow(biisielementti)

	def hae(self):
		'''
		Suorita haku.
		'''
		hakudikti = {}
		oli_tuloksia = False
		# Sarjan nimi
		artistinnimessa = None
		if self.nimihaku.text() and self.nimihaku.text() != "Artistin nimi":
			artistinnimessa = self.nimihaku.text().split(" ")
		print(f"artisti: {artistinnimessa}")
		hakudikti = {
					"vapaahaku":     artistinnimessa,
					"ehtona_ja":     False,
					"artistissa":    artistinnimessa,
					"biisissa":      artistinnimessa,
					"albumissa":     artistinnimessa,
					"tiedostossa":   artistinnimessa
					# "raitanumero":   (1,3)
					}
		haettavaa = any([hakudikti[a] is not None for a in hakudikti])
		self.puu.setCurrentIndex(self.puu.rootIndex())
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

	def lataa(self):
		'''
		Lataa valittu asia.
		'''
		asia = self.puumalli.itemFromIndex(self.puu.currentIndex())
		if type(asia) in [Tiedostoelementti, Kansioelementti]:
			print(asia.tiedostopolku())
			if type(asia) is Kansioelementti:
				biiseja = asia.puu.sisallon_maara()
				vaaraikkuna = Vaara_monta(biiseja[0])
				if vaaraikkuna.clickedButton() is vaaraikkuna.juu:
					print("I love danger zone")
				else:
					print("Pelottaa")

	def nayta_tiedot(self):
		'''
		Näytä valitun biisin tai kansion tiedot.
		'''
		st = ""
		if type(self.puumalli.itemFromIndex(self.puu.currentIndex())) in [Kansioelementti, Tiedostoelementti]:
			st = str(self.puumalli.itemFromIndex(self.puu.currentIndex()))
			print(st)
		self.taulukko.setText(st)


if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	ikkuna = Selausikkuna()
	ikkuna.show()

	sys.exit(app.exec_())