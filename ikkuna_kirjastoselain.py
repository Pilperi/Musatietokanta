import os
import sys
import time
import class_biisit as cb
import funktiot_kansiofunktiot as kfun
import vakiot_kansiovakiot as kvak
from class_tiedostopuu import Tiedostopuu
from PyQt5 import Qt, QtCore, QtWidgets, QtGui

os.environ['QT_IM_MODULE'] = 'fcitx' # japski-input

# Ikkunan asioiden mitat
IKKUNAMITAT    = (700,700)
MARGINAALIT    = (10,10)
HAKUMITAT      = (MARGINAALIT[0], 205, MARGINAALIT[1], 35)
HAKULABEL      = 20
HAKUNAPPI      = 80
PUUMITAT       = (MARGINAALIT[0], HAKUMITAT[1]*2, 2*MARGINAALIT[1]+HAKUMITAT[2]+HAKUMITAT[3], IKKUNAMITAT[1]-(3*MARGINAALIT[1]+HAKUMITAT[2]+HAKUMITAT[3]))
TAULUKKOMITAT  = (PUUMITAT[0]+PUUMITAT[1], IKKUNAMITAT[0]-PUUMITAT[0]-PUUMITAT[1]-MARGINAALIT[0], PUUMITAT[2], 210)
LATAUSNAPPI    = (TAULUKKOMITAT[0], TAULUKKOMITAT[1], TAULUKKOMITAT[2]+TAULUKKOMITAT[3], 50)
ASETUSVALITSIN = (HAKUMITAT[1]+MARGINAALIT[0], HAKUMITAT[3]-5, 175, HAKUMITAT[3])
ASETUSPAIVITYS = (ASETUSVALITSIN[0]+ASETUSVALITSIN[2], HAKUMITAT[3]-5, 28, ASETUSVALITSIN[3])
# TIETOKANTAVALITSIN = (TAULUKKOMITAT[0], TAULUKKOMITAT[2]-HAKUMITAT[3], TAULUKKOMITAT[1]-ASETUSPAIVITYS[2]-10, HAKUMITAT[3]-ASETUSPAIVITYS[3]-2)
TIETOKANTAVALITSIN = (ASETUSPAIVITYS[0]+ASETUSPAIVITYS[2], ASETUSPAIVITYS[1], IKKUNAMITAT[0]-ASETUSPAIVITYS[0]-ASETUSPAIVITYS[2]-ASETUSPAIVITYS[2]-MARGINAALIT[0], ASETUSVALITSIN[3])
TIETOKANTAPAIVITYS = (TIETOKANTAVALITSIN[0]+TIETOKANTAVALITSIN[2], TIETOKANTAVALITSIN[1], ASETUSPAIVITYS[2], ASETUSPAIVITYS[3])
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

class Worker(Qt.QRunnable):
	'''
	Worker thread
	'''
	def __init__(self, ikkuna):
		super(Worker, self).__init__()
		self.asia = ikkuna.asia
		self.ikkuna = ikkuna
		self.setAutoDelete(True)

	def run(self):
		print("Ladataan ja lisätään soittolistalle.")
		if type(self.asia) is Kansioelementti:
			# Jos samanniminen kansio on jo biisikansiossa (ex. CD1),
			# läimäise loppuun riittävän iso juokseva numero
			kansionimi = self.asia.puu.kansio
			i = 0
			while os.path.exists(os.path.join(kvak.BIISIKANSIO, kansionimi)):
				kansionimi = f"{self.asia.puu.kansio}-{i}"
				print(kansionimi)
			kfun.lataa_ja_lisaa_soittolistaan(vaintiedosto=False,\
                                              lahdepalvelin=kvak.ETAPALVELIN,
                                              lahdepolku=self.asia.tiedostopolku(),
                                              kohdepalvelin=None,
                                              kohdepolku=os.path.join(kvak.BIISIKANSIO, kansionimi))
		else:
			# Jos samanniminen biisi on jo biisikansiossa (ex. track01.mp3),
			# läimäise loppuun riittävän iso juokseva numero
			tiedostonimi_runko, tiedostonimi_paate = kfun.paate(self.asia.tiedosto.tiedostonimi)
			tiedostonimi = f"{tiedostonimi_runko}.{tiedostonimi_paate}"
			i = 0
			print(tiedostonimi)
			while os.path.exists(os.path.join(kvak.BIISIKANSIO, tiedostonimi)):
				tiedostonimi = f"{tiedostonimi_runko}-{i}.{tiedostonimi_paate}"
				print(tiedostonimi)
				i += 1
			print(f"-> {tiedostonimi}")
			kfun.lataa_ja_lisaa_soittolistaan(vaintiedosto=True,\
                                              lahdepalvelin=kvak.ETAPALVELIN,
                                              lahdepolku=self.asia.tiedostopolku(),
                                              kohdepalvelin=None,
                                              kohdepolku=os.path.join(kvak.BIISIKANSIO, tiedostonimi))
		print("Sulje latausikkuna")
		self.ikkuna.close()

class Latausikkuna(QtWidgets.QMessageBox):
	def __init__(self, asia, timeout=120):
		super().__init__()
		self.setWindowTitle('Ladataan')
		# self.setStandardButtons(QtWidgets.QMessageBox.Yes)
		self.setStandardButtons(QtWidgets.QMessageBox.NoButton)
		self.setText("Ladataan kappaleita")
		self.asia = asia
		self.show()
		self.threadpool = QtCore.QThreadPool()
		worker = Worker(self)
		self.threadpool.globalInstance().start(worker)

class Selausikkuna(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.initflag = True
		self.setStyleSheet("background-color: #31363b")
		# Lataa tietokannat
		self.tietokantatiedostot = []
		for tietokanta in kvak.ETAPALVELIN_TIETOKANNAT:
			koodi = kfun.lataa(vaintiedosto=True,\
							   lahdepalvelin=kvak.ETAPALVELIN,\
							   lahdepolku=tietokanta,\
							   kohdepalvelin=None,\
							   kohdepolku=os.path.basename(tietokanta))
			if koodi:
				self.tietokantatiedostot.append(os.path.basename(tietokanta))

		# Määritä puu
		self.puu = QtWidgets.QTreeView(self)
		self.puu.setGeometry(QtCore.QRect(PUUMITAT[0], PUUMITAT[2], PUUMITAT[1], PUUMITAT[3]))
		self.puu.setHeaderHidden(True)
		self.puumalli = Qt.QStandardItemModel()
		self.juurisolmu = self.puumalli.invisibleRootItem()
		self.puu.setModel(self.puumalli)
		self.puu.expand(self.puumalli.index(0,0))
		# Tietoja inee
		self.tiedostopuu = Tiedostopuu(tiedostotyyppi=cb.Biisi)
		if len(self.tietokantatiedostot):
			tietokanta = open(self.tietokantatiedostot[0], "r")
			self.tiedostopuu.lue_tiedostosta(tietokanta)
			tietokanta.close()
			self.kansoita_puu(self.tiedostopuu)
		self.puu.selectionModel().selectionChanged.connect(self.nayta_tiedot)

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
		self.etsi.setToolTip("Lainausmerkit täsmähakuun")
		self.etsi.setText("Etsi")
		self.etsi.setShortcut("Return")     # normi
		# self.Etsi.setShortcut("Enter")    # kp
		# self.Etsi.setObjectName("pushButton")
		self.etsi.clicked.connect(self.hae)

		# self.taulukko = QtWidgets.QLineEdit(self)
		self.taulukko = QtWidgets.QTextEdit(self)
		self.taulukko.setGeometry(QtCore.QRect(TAULUKKOMITAT[0], TAULUKKOMITAT[2], TAULUKKOMITAT[1], TAULUKKOMITAT[3]))
		self.taulukko.setText("")
		self.taulukko.setReadOnly(True)
		self.taulukko.setAlignment(QtCore.Qt.AlignTop)
		self.taulukko.setWordWrapMode(0)
		self.taulukko.setStyleSheet("background-color: #31363b")

		# Asetusvalitsin
		self.asetusvalitsin = QtWidgets.QComboBox(self)
		self.asetusvalitsin.setGeometry(QtCore.QRect(*ASETUSVALITSIN))
		self.asetusvalitsin.addItems([a for a in kvak.config.keys() if a != "DEFAULT"])
		self.asetusvalitsin.currentIndexChanged.connect(self.vaihda_asetuksia)
		# Päivitä palvelinvalikoima
		self.asetusnappi = QtWidgets.QPushButton(self)
		self.asetusnappi.setStyleSheet("background-color: #373c41; color: white; font-weight: bold")
		self.asetusnappi.setGeometry(QtCore.QRect(*ASETUSPAIVITYS))
		self.asetusnappi.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.asetusnappi.setFocusPolicy(QtCore.Qt.NoFocus)
		self.asetusnappi.setToolTip("Päivitä palvelinvalikoima")
		if os.path.exists('.refreshicon.svg'):
			self.asetusnappi.setIcon(QtGui.QIcon('.refreshicon.svg'))
		else:
			self.asetusnappi.setText("p")
		self.asetusnappi.clicked.connect(self.paivita_asetukset)

		# Tietokantavalitsin
		self.tietokantavalitsin = QtWidgets.QComboBox(self)
		self.tietokantavalitsin.setGeometry(QtCore.QRect(*TIETOKANTAVALITSIN))
		self.tietokantavalitsin.addItems(self.tietokantatiedostot)
		self.tietokantavalitsin.currentIndexChanged.connect(self.vaihda_tietokantaa)
		# Päivitä tietokannat
		self.tietokantanappi = QtWidgets.QPushButton(self)
		self.tietokantanappi.setStyleSheet("background-color: #373c41; color: white; font-weight: bold")
		self.tietokantanappi.setGeometry(QtCore.QRect(*TIETOKANTAPAIVITYS))
		self.tietokantanappi.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.tietokantanappi.setFocusPolicy(QtCore.Qt.NoFocus)
		self.tietokantanappi.setToolTip("Päivitä tietokannat")
		if os.path.exists('.refreshicon.svg'):
			self.tietokantanappi.setIcon(QtGui.QIcon('.refreshicon.svg'))
		else:
			self.tietokantanappi.setText("p")
		self.tietokantanappi.clicked.connect(self.paivita_tietokannat)

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

		self.initflag = False

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

	def parsi_hakutermit(self, teksti):
		'''
		Parsii hakukentän tekstin hakuargumenteiksi.
		Tätä kutsutaan ei-tyhjillä stringeillä.

		Teksti splitataan niin että hakutermit on erotettu
		välilyönneillä, poislukien "lainausmerkeillä ympäröidyt pätkät",
		jotka muodostavat yksittäisen hakutermin.
		'''
		# Rullataan merkki kerrallaan läpi
		hakutermit = []
		hipsut_auki = teksti[0] == "\"" # alkaako hipsuilla?
		termi = ""
		if not hipsut_auki:
			termi = teksti[0]
		i = 1
		while i < len(teksti):
			# Rullataan eteenpäin kunnes vastaan tulee välilyönti
			# jollei olla aloitettu hipsumerkeillä ympäröityä pätkää
			j = 0
			while i+j < len(teksti):
				if kvak.VERBOOSI:
					print(f"Hakutermi: {termi}")
				# Vastassa välilyönti eikä hipsut ole auki: katkaistaan
				if teksti[i+j] == " " and not hipsut_auki:
					j += 1
					break
				# Hipsut on auki ja vastassa hipsu: katkaistaan ja vaihdetaan hipsutilaa
				if teksti[i+j] == "\"":
					hipsut_auki = not hipsut_auki
					j += 1
					break
				termi += teksti[i+j]
				j += 1
			# Lisätään listaan ja resetoidaan termikasaus
			if len(termi):
				if kvak.VERBOOSI:
					print(f"Lisätään \"{termi}\" hakutermeihin")
				hakutermit.append(termi)
			termi = ""
			i += j
		return(hakutermit)

	def hae(self):
		'''
		Suorita haku.
		'''
		hakudikti = {}
		oli_tuloksia = False
		# Sarjan nimi
		hakutermit = None
		if self.nimihaku.text() and self.nimihaku.text() != "Vapaahaku":
			teksti = self.nimihaku.text()
			# Asiat splitattu välilyönneillä, lainausmerkkien
			# välissä olevat asiat omia entiteettejään.
			# Vähän sekamelska niin parsitaan erillisen funktion puolella.
			hakutermit = self.parsi_hakutermit(teksti)
		print(f"Vapaahaku termeillä: {hakutermit}")
		hakudikti = {
					"vapaahaku":     hakutermit
					# "ehtona_ja":     False,
					# "artistissa":    artistinnimessa,
					# "biisissa":      artistinnimessa,
					# "albumissa":     artistinnimessa,
					# "tiedostossa":   artistinnimessa
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
		if type(asia) is Kansioelementti:
			biiseja = asia.puu.sisallon_maara()[0]
			latauslupa = False
			# Monta kappaletta, varmistetaan
			if biiseja > kvak.VAROITURAJA:
				vaaraikkuna = Vaara_monta(biiseja)
				if vaaraikkuna.clickedButton() is vaaraikkuna.juu:
					latauslupa = True
			# Ei kovin montaa kappaletta
			else:
				latauslupa = True
			if latauslupa:
				# latausikkuna = Latausikkuna(asia)
				print("Ladataan ja lisätään soittolistalle.")
				# Jos samanniminen kansio on jo biisikansiossa (ex. CD1),
				# läimäise loppuun riittävän iso juokseva numero
				kansionimi = asia.puu.kansio
				i = 0
				while os.path.exists(os.path.join(kvak.BIISIKANSIO, kansionimi)):
					print(f"{kansionimi} on jo biisikansiossa")
					kansionimi = f"{asia.puu.kansio}-{i}"
					i += 1
				print(f"-> {kansionimi} on vapaa nimi kansiolle")
				kfun.lataa_ja_lisaa_soittolistaan(vaintiedosto=False,\
	                                              lahdepalvelin=kvak.ETAPALVELIN,
	                                              lahdepolku=asia.tiedostopolku(),
	                                              kohdepalvelin=None,
	                                              kohdepolku=os.path.join(kvak.BIISIKANSIO, kansionimi))
		elif type(asia) is Tiedostoelementti:
			# latausikkuna = Latausikkuna(asia)
			# Jos samanniminen biisi on jo biisikansiossa (ex. track01.mp3),
			# läimäise loppuun riittävän iso juokseva numero
			tiedostonimi_runko, tiedostonimi_paate = kfun.paate(asia.tiedosto.tiedostonimi)
			tiedostonimi = f"{tiedostonimi_runko}.{tiedostonimi_paate}"
			i = 0
			print(tiedostonimi)
			while os.path.exists(os.path.join(kvak.BIISIKANSIO, tiedostonimi)):
				print(f"{tiedostonimi} on jo biisikansiossa")
				tiedostonimi = f"{tiedostonimi_runko}-{i}.{tiedostonimi_paate}"
				i += 1
			print(f"-> {tiedostonimi} on vapaa tiedostonimi")
			kfun.lataa_ja_lisaa_soittolistaan(vaintiedosto=True,\
                                              lahdepalvelin=kvak.ETAPALVELIN,
                                              lahdepolku=asia.tiedostopolku(),
                                              kohdepalvelin=None,
                                              kohdepolku=os.path.join(kvak.BIISIKANSIO, tiedostonimi))

	def nayta_tiedot(self):
		'''
		Näytä valitun biisin tai kansion tiedot.
		'''
		st = ""
		if type(self.puumalli.itemFromIndex(self.puu.currentIndex())) in [Kansioelementti, Tiedostoelementti]:
			st = str(self.puumalli.itemFromIndex(self.puu.currentIndex()))
			print(st)
		self.taulukko.setText(st)

	def vaihda_tietokantaa(self):
		'''
		Vaihda mitä tietokantaa käytetään pohjana.
		'''
		tietokantatiedosto = self.tietokantavalitsin.currentText()
		if not self.initflag:
			self.juurisolmu.removeRow(0)
		self.tiedostopuu = Tiedostopuu(tiedostotyyppi=cb.Biisi)
		tietokanta = open(tietokantatiedosto, "r")
		self.tiedostopuu.lue_tiedostosta(tietokanta)
		tietokanta.close()
		self.kansoita_puu(self.tiedostopuu)

	def paivita_tietokannat(self):
		'''
		Lataa palvelimelta uudet tietokannat.
		'''
		self.tietokantatiedostot = []
		for tietokanta in kvak.ETAPALVELIN_TIETOKANNAT:
			koodi = kfun.lataa(vaintiedosto=True,\
							   lahdepalvelin=kvak.ETAPALVELIN,\
							   lahdepolku=tietokanta,\
							   kohdepalvelin=None,\
							   kohdepolku=os.path.basename(tietokanta))
			if koodi:
				self.tietokantatiedostot.append(os.path.basename(tietokanta))
		self.tietokantavalitsin.clear()
		self.tietokantavalitsin.addItems(self.tietokantatiedostot)
		self.vaihda_tietokantaa()

	def paivita_asetukset(self):
		'''
		Päivitä asetuskattaus (as in, joku kirjoitellut INI-tiedostoon uutta kamaa)
		'''
		kvak.paivita_asetukset()
		self.asetusvalitsin.clear()
		self.asetusvalitsin.addItems([a for a in kvak.config.keys() if a != "DEFAULT"])

	def vaihda_asetuksia(self):
		'''
		Vaihtaa asetuskantaa (läh. palvelinta).
		'''
		# Lue asetussetin nimi ja vaihda vakiot
		asetussetti = self.asetusvalitsin.currentText()
		kvak.vaihda_asetuskokoonpanoa(asetussetti)
		# Uusi tietokantatiedostot
		self.tietokantatiedostot = []
		for tietokanta in kvak.ETAPALVELIN_TIETOKANNAT:
			if not os.path.exists(f"./{os.path.basename(tietokanta)}"):
				if kvak.VERBOOSI:
					print(f"Tietokantaa ./{os.path.basename(tietokanta)} ei ole ladattu, ladataan.")
				koodi = kfun.lataa(vaintiedosto=True,\
								   lahdepalvelin=kvak.ETAPALVELIN,\
								   lahdepolku=tietokanta,\
								   kohdepalvelin=None,\
								   kohdepolku=os.path.basename(tietokanta))
				if koodi:
					self.tietokantatiedostot.append(os.path.basename(tietokanta))
			else:
				if kvak.VERBOOSI:
					print(f"Tietokanta ./{os.path.basename(tietokanta)} löytyy jo. Päivitä erikseen jos haluat.")
				self.tietokantatiedostot.append(os.path.basename(tietokanta))
		# Uusi tiedostopuu
		self.tiedostopuu = Tiedostopuu(tiedostotyyppi=cb.Biisi)
		if len(self.tietokantatiedostot):
			tietokanta = open(self.tietokantatiedostot[0], "r")
			self.tiedostopuu.lue_tiedostosta(tietokanta)
			tietokanta.close()
			self.juurisolmu.removeRow(0)
			self.kansoita_puu(self.tiedostopuu)
			self.puu.setModel(self.puumalli)
			self.puu.expand(self.puumalli.index(0,0))

	def closeEvent(self, event):
		'''
		Tallenna asetukset ennen sulkemista.
		'''
		kvak.tallenna_asetukset()
		event.accept()
