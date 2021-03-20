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
ASETUSVALITSIN = (HAKUMITAT[1]+MARGINAALIT[0], HAKUMITAT[3]-5, 175, HAKUMITAT[3])
ASETUSPAIVITYS = (ASETUSVALITSIN[0]+ASETUSVALITSIN[2], HAKUMITAT[3]-5, 28, ASETUSVALITSIN[3])
TIETOKANTAVALITSIN = (ASETUSPAIVITYS[0]+ASETUSPAIVITYS[2], ASETUSPAIVITYS[1], IKKUNAMITAT[0]-ASETUSPAIVITYS[0]-ASETUSPAIVITYS[2]-ASETUSPAIVITYS[2]-MARGINAALIT[0], ASETUSVALITSIN[3])
TIETOKANTAPAIVITYS = (TIETOKANTAVALITSIN[0]+TIETOKANTAVALITSIN[2], TIETOKANTAVALITSIN[1], ASETUSPAIVITYS[2], ASETUSPAIVITYS[3])

# Puun muotoiluparametrit
PAATASOT      = 2

LABEL_NIMIHAKU  = (HAKUMITAT[0], HAKUMITAT[2], HAKUMITAT[1]-HAKUNAPPI, HAKUMITAT[3])
KENTTA_NIMIHAKU = (HAKUMITAT[0], HAKUMITAT[2]+HAKULABEL, HAKUMITAT[1]-HAKUNAPPI, HAKUMITAT[3])
NAPPI_ETSI      = (HAKUMITAT[0]+HAKUMITAT[1]-HAKUNAPPI, HAKUMITAT[2]+HAKULABEL, HAKUNAPPI, HAKUMITAT[3])
PUUMITAT        = (KENTTA_NIMIHAKU[0], KENTTA_NIMIHAKU[1]+KENTTA_NIMIHAKU[3], ASETUSPAIVITYS[0]+ASETUSPAIVITYS[2]-KENTTA_NIMIHAKU[0], IKKUNAMITAT[1]-(KENTTA_NIMIHAKU[1]+KENTTA_NIMIHAKU[3]+2*MARGINAALIT[1]+50))
KANSIOMOODI     = (PUUMITAT[0], PUUMITAT[1]+PUUMITAT[3], int(0.5*PUUMITAT[2]), IKKUNAMITAT[1]-PUUMITAT[1]-PUUMITAT[3]-MARGINAALIT[1])
ARTISTIMOODI    = (KANSIOMOODI[0]+KANSIOMOODI[2], KANSIOMOODI[1], PUUMITAT[2]-KANSIOMOODI[2], KANSIOMOODI[3])
TAULUKKOMITAT   = (PUUMITAT[0]+PUUMITAT[2], PUUMITAT[1], IKKUNAMITAT[0]-PUUMITAT[0]-PUUMITAT[2]-MARGINAALIT[0], 210)
NAPPI_LATAA     = (TAULUKKOMITAT[0], TAULUKKOMITAT[1]+TAULUKKOMITAT[3], TAULUKKOMITAT[2], 50)
LATAUSLABEL     = (NAPPI_LATAA[0], NAPPI_LATAA[1]+NAPPI_LATAA[3]+MARGINAALIT[1], NAPPI_LATAA[2], 20)
LATAUSLISTA     = (LATAUSLABEL[0], LATAUSLABEL[1]+LATAUSLABEL[3], LATAUSLABEL[2], IKKUNAMITAT[1]-LATAUSLABEL[1]-LATAUSLABEL[3]-MARGINAALIT[1])

print(f"LABEL_NIMIHAKU  {LABEL_NIMIHAKU}")
print(f"KENTTA_NIMIHAKU {KENTTA_NIMIHAKU}")
print(f"NAPPI_ETSI      {NAPPI_ETSI}")
print(f"KANSIOMOODI     {KANSIOMOODI}")
print(f"ARTISTIMOODI    {ARTISTIMOODI}")
print(f"PUUMITAT        {PUUMITAT}")
print(f"TAULUKKOMITAT   {TAULUKKOMITAT}")
print(f"LATAUSLABEL     {LATAUSLABEL}")
print(f"LATAUSLISTA     {LATAUSLISTA}")

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

	def latauslistateksti(self):
		'''
		Anna tekstipätkä jonka voi laittaa latauslistaan
		edustamaan kyseistä kansiota (ts. kansion nimi)
		'''
		st = str(self.puu.kansio)
		return(st)

	def sisallon_maara(self):
		'''
		Kerro kuinka monta biisiä kansio pitää
		yhteensä sisällään.
		'''
		return(self.puu.sisallon_maara()[0])

	def lataa(self):
		print("Ladataan ja lisätään soittolistalle.")
		# Jos samanniminen kansio on jo biisikansiossa (ex. CD1),
		# läimäise loppuun riittävän iso juokseva numero
		kansionimi = self.puu.kansio
		i = 0
		while os.path.exists(os.path.join(kvak.BIISIKANSIO, kansionimi)):
			print(f"{kansionimi} on jo biisikansiossa")
			kansionimi = f"{self.puu.kansio}-{i}"
			i += 1
		print(f"-> {kansionimi} on vapaa nimi kansiolle")
		kfun.lataa_ja_lisaa_soittolistaan(vaintiedosto=False,\
										  lahdepalvelin=kvak.ETAPALVELIN,
										  lahdepolku=self.tiedostopolku(),
										  kohdepalvelin=None,
										  kohdepolku=os.path.join(kvak.BIISIKANSIO, kansionimi))

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

	def latauslistateksti(self):
		'''
		Anna tekstipätkä jonka voi laittaa latauslistaan
		edustamaan kyseistä kansiota (ts. artisti - biisi)
		'''
		st = "{} - {}".format(self.tiedosto.esittaja, self.tiedosto.biisinimi)
		return(st)

	def lataa(self):
		# Jos samanniminen biisi on jo biisikansiossa (ex. track01.mp3),
		# läimäise loppuun riittävän iso juokseva numero
		tiedostonimi_runko, tiedostonimi_paate = kfun.paate(self.tiedosto.tiedostonimi)
		tiedostonimi = f"{tiedostonimi_runko}.{tiedostonimi_paate}"
		i = 0
		while os.path.exists(os.path.join(kvak.BIISIKANSIO, tiedostonimi)):
			print(f"{tiedostonimi} on jo biisikansiossa")
			tiedostonimi = f"{tiedostonimi_runko}-{i}.{tiedostonimi_paate}"
			i += 1
		print(f"-> {tiedostonimi} on vapaa tiedostonimi")
		kfun.lataa_ja_lisaa_soittolistaan(vaintiedosto=True,\
										  lahdepalvelin=kvak.ETAPALVELIN,
										  lahdepolku=self.tiedostopolku(),
										  kohdepalvelin=None,
										  kohdepolku=os.path.join(kvak.BIISIKANSIO, tiedostonimi))

class Artistielementti(Qt.QStandardItem):
	'''
	Data jaoteltuna artisti -> albumi
	koska nipan tiedostot on ihan miten sattuu.
	'''
	def __init__(self, artistipuu, artisti, fonttikoko=12, boldattu=False, vari=(255,255,255)):
		super().__init__()
		fontti = QtGui.QFont("Open Sans", fonttikoko)
		fontti.setBold(boldattu)

		puuteksti = str(artisti)

		self.setEditable(False)
		self.setForeground(QtGui.QColor(*vari))
		self.setFont(fontti)
		self.setText(puuteksti)
		self.artisti = artisti # str
		self.dikti   = {} # {albuminnimi: [Biisejä]}
		if artistipuu.artistit.get(artisti) is not None:
			self.dikti = artistipuu.artistit.get(artisti)

	def __str__(self):
		'''
		Kuvaus kansiosta tietoikkunaan.
		'''
		st  = "Artisti\t{}".format(self.artisti)
		st += "\nAlbumeita\t{}".format(len(self.dikti.keys()))
		lukumaara = 0
		for albumi in self.dikti:
			lukumaara += len(self.dikti[albumi])
		st += "\nBiisejä\t{}".format(lukumaara)
		return(st)

	def sisallon_maara(self):
		'''
		Kerro kuinka monta biisiä artistin
		tuotannossa yhteensä on (+albumien feattaajat)
		'''
		lukumaara = 0
		for albumi in self.dikti:
			lukumaara += len(self.dikti[albumi])
		return(lukumaara)

	def latauslistateksti(self):
		'''
		Anna tekstipätkä jonka voi laittaa latauslistaan
		edustamaan kyseistä kansiota (ts. kansion nimi)
		'''
		st = self.artisti
		return(st)

	def lataa(self):
		print("Ladataan ja lisätään soittolistalle.")
		# Jos samanniminen kansio on jo biisikansiossa (ex. CD1),
		# läimäise loppuun riittävän iso juokseva numero
		kansionimi = self.artisti.replace("/", "-")
		i = 0
		while os.path.exists(os.path.join(kvak.BIISIKANSIO, kansionimi)):
			print(f"{kansionimi} on jo biisikansiossa")
			kansionimi = f"{self.artisti}-{i}".replace("/", "-")
			i += 1
		print(f"-> {kansionimi} on vapaa nimi kansiolle")
		os.mkdir(os.path.join(kvak.BIISIKANSIO, kansionimi))
		for albumi in self.dikti:
			albumikansio = os.path.join(kvak.BIISIKANSIO, kansionimi, albumi)
			os.mkdir(albumikansio)
			for tiedostopuu, biisi in self.dikti[albumi]:
				lahdepolku = os.path.join(tiedostopuu.hae_nykyinen_polku(), biisi.tiedostonimi)
				kfun.lataa_ja_lisaa_soittolistaan(vaintiedosto=True,\
										  lahdepalvelin=kvak.ETAPALVELIN,
										  lahdepolku=lahdepolku,
										  kohdepalvelin=None,
										  kohdepolku=os.path.join(albumikansio, biisi.tiedostonimi))

class Albumielementti(Qt.QStandardItem):
	'''
	Albumi Artistielementin alla.
	'''
	def __init__(self, artistipuu, artisti, albumi, fonttikoko=12, boldattu=False, vari=(255,255,255)):
		super().__init__()
		fontti = QtGui.QFont("Open Sans", fonttikoko)
		fontti.setBold(boldattu)

		puuteksti = str(albumi)

		self.setEditable(False)
		self.setForeground(QtGui.QColor(*vari))
		self.setFont(fontti)
		self.setText(puuteksti)
		self.artisti = artisti # str
		self.albumi  = albumi  # str
		self.biisit  = []      # lista (Tiedostopuu, Biisi) tupleja
		if artistipuu.artistit.get(artisti) is not None and artistipuu.artistit[artisti].get(albumi) is not None:
			self.biisit = artistipuu.artistit[artisti][albumi]

	def __str__(self):
		'''
		Kuvaus kansiosta tietoikkunaan.
		'''
		st  = "Albumi\t{} - {}".format(self.artisti, self.albumi)
		st += "\nBiisejä\t{}".format(len(self.biisit))
		return(st)

	def sisallon_maara(self):
		'''
		Kerro kuinka monta biisiä albumi pitää
		yhteensä sisällään.
		'''
		return(len(self.biisit))

	def latauslistateksti(self):
		'''
		Anna tekstipätkä jonka voi laittaa latauslistaan
		edustamaan kyseistä kansiota (ts. kansion nimi)
		'''
		st = "{} - {}".format(self.artisti, self.albumi)
		return(st)

	def lataa(self):
		print("Ladataan ja lisätään soittolistalle.")
		# Jos samanniminen kansio on jo biisikansiossa (ex. CD1),
		# läimäise loppuun riittävän iso juokseva numero
		kansionimi = f"{self.artisti} - {self.albumi}".replace("/", "-")
		i = 0
		while os.path.exists(os.path.join(kvak.BIISIKANSIO, kansionimi)):
			print(f"{kansionimi} on jo biisikansiossa")
			kansionimi = f"{self.artisti} - {self.albumi} {i}".replace("/", "-")
			i += 1
		print(f"-> {kansionimi} on vapaa nimi kansiolle")
		albumikansio = os.path.join(kvak.BIISIKANSIO, kansionimi)
		os.mkdir(albumikansio)
		for tiedostopuu, biisi in self.biisit:
			lahdepolku = os.path.join(tiedostopuu.hae_nykyinen_polku(), biisi.tiedostonimi)
			kfun.lataa_ja_lisaa_soittolistaan(vaintiedosto=True,\
										  lahdepalvelin=kvak.ETAPALVELIN,
										  lahdepolku=lahdepolku,
										  kohdepalvelin=None,
										  kohdepolku=os.path.join(albumikansio, biisi.tiedostonimi))

class Raitaelementti(Qt.QStandardItem):
	'''
	Raita albumilla.
	'''
	def __init__(self, tiedostotuple, boldattu=False, fonttikoko=10, vari=(255,255,255)):
		super().__init__()
		fontti = QtGui.QFont("Open Sans", fonttikoko)

		puuteksti = str(tiedostotuple[1].tiedostonimi)

		self.setEditable(False)
		self.setForeground(QtGui.QColor(*vari))
		self.setFont(fontti)
		self.setText(puuteksti)
		self.tiedostotuple = tiedostotuple

	def tiedostopolku(self):
		'''
		Antaa tiedoston polun.
		Vanhempana aina jokin kansio,
		haetaan siitä kansiopolku ja tiedostosta tiedostonimi.
		'''
		vanhempi = self.parent()
		kansiopolku  = self.tiedostotuple[0].hae_nykyinen_polku()
		tiedostonimi = self.tiedostotuple[1].tiedostonimi
		return(os.path.join(kansiopolku, tiedostonimi))

	def __str__(self):
		'''
		Näytä biisin tiedot.
		'''
		st = ""
		st += "{} - {}\n\n\n".format(self.tiedostotuple[1].esittaja, self.tiedostotuple[1].biisinimi)
		st += "Esittäjä:"
		if self.tiedostotuple[1].esittaja:
			st += "\t{}".format(self.tiedostotuple[1].esittaja)
		st += "\nKappale:"
		if self.tiedostotuple[1].biisinimi:
			st += "\t{}".format(self.tiedostotuple[1].biisinimi)
		st += "\nAlbumi:"
		if self.tiedostotuple[1].albuminimi:
			st += "\t{}".format(self.tiedostotuple[1].albuminimi)
		st += "\nVuosi:"
		if self.tiedostotuple[1].vuosi:
			st += "\t{}".format(self.tiedostotuple[1].vuosi)
		st += "\nRaita:"
		if self.tiedostotuple[1].vuosi:
			st += "\t{}{}".format(self.tiedostotuple[1].raita, f"/{self.tiedostotuple[1].raitoja}"*(self.tiedostotuple[1].raitoja not in [0,None]))
		st += "\nAlb.es.:"
		if self.tiedostotuple[1].albumiesittaja:
			st += "\t{}".format(self.tiedostotuple[1].albumiesittaja)
		st += "\nLisätty:"
		if self.tiedostotuple[1].lisayspaiva:
			pilkottu = self.tiedostotuple[1].paivays(self.tiedostotuple[1].lisayspaiva)[1]
			st += "\t{:04d}-{:02d}-{:02d} / {:02d}:{:02d}".format(pilkottu[0], pilkottu[1], pilkottu[2], pilkottu[3], pilkottu[4])
		return(st)

	def latauslistateksti(self):
		'''
		Anna tekstipätkä jonka voi laittaa latauslistaan
		edustamaan kyseistä kansiota (ts. artisti - biisi)
		'''
		st = "{} - {}".format(self.tiedostotuple[1].esittaja, self.tiedostotuple[1].biisinimi)
		return(st)

	def lataa(self):
		# Jos samanniminen biisi on jo biisikansiossa (ex. track01.mp3),
		# läimäise loppuun riittävän iso juokseva numero
		tiedostonimi_runko, tiedostonimi_paate = kfun.paate(self.tiedostotuple[1].tiedostonimi)
		tiedostonimi = f"{tiedostonimi_runko}.{tiedostonimi_paate}".replace("/", "-")
		i = 0
		while os.path.exists(os.path.join(kvak.BIISIKANSIO, tiedostonimi)):
			print(f"{tiedostonimi} on jo biisikansiossa")
			tiedostonimi = f"{tiedostonimi_runko}-{i}.{tiedostonimi_paate}".replace("/", "-")
			i += 1
		print(f"-> {tiedostonimi} on vapaa tiedostonimi")
		kfun.lataa_ja_lisaa_soittolistaan(vaintiedosto=True,\
										  lahdepalvelin=kvak.ETAPALVELIN,
										  lahdepolku=self.tiedostopolku(),
										  kohdepalvelin=None,
										  kohdepolku=os.path.join(kvak.BIISIKANSIO, tiedostonimi))

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

class Latauslista(QtWidgets.QListWidget):
	'''
	Latausjonolista.
	'''
	def __init__(self, parent=None, asiat=None, mitat=(0,0,100,100)):
		super().__init__(parent=parent)
		self.setGeometry(QtCore.QRect(*mitat))
		self.ladataan = False
		# Lisää asiat listaan
		if type(asiat) in (list, tuple):
			for asia in asiat:
				self.lisaa(asia)

	def lisaa(self, asia):
		# Lisää asia ladattavaksi
		if type(asia) in (Kansioelementti, Tiedostoelementti, Artistielementti, Albumielementti, Raitaelementti):
			listaelementti = QtWidgets.QListWidgetItem()
			teksti = asia.latauslistateksti()
			print(f"Lisätään {teksti} latauslistalle")
			listaelementti.setText(teksti) # tekstimuoto
			listaelementti.setData(QtCore.Qt.UserRole, asia) # itse asia
			self.addItem(listaelementti)
		else:
			print(f"Asia väärää tyyppiä {type(asia)}")

class Orjasignaalit(QtCore.QObject):
	'''
	Signaalit oudossa omassa luokassaan koska
	Qt haluaa olla hankala
	'''
	ladattu = QtCore.pyqtSignal() # Tiedosto ladattu
	valmis  = QtCore.pyqtSignal() # Prosessi valmis

class Latausorja(QtCore.QRunnable):
	def __init__(self, ladattavat=[]):
		super().__init__()
		self.signaalit = Orjasignaalit()
		self.ladattavat = ladattavat

	def run(self):
		for tiedosto in self.ladattavat:
			tiedosto.lataa()
			self.signaalit.ladattu.emit()
		self.signaalit.valmis.emit()

class Selausikkuna(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.initflag = True
		self.setStyleSheet("background-color: #31363b; color: white")
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
		self.puu.setGeometry(QtCore.QRect(*PUUMITAT))
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
		self.artistipuu = None

		# Napit joilla vaihdellaan puumoodien välillä:
		# Kansio/Alikansio/Biisi
		self.nappi_kansiorakenne = QtWidgets.QPushButton(self)
		self.nappi_kansiorakenne.setGeometry(QtCore.QRect(*KANSIOMOODI))
		self.nappi_kansiorakenne.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.nappi_kansiorakenne.setFocusPolicy(QtCore.Qt.NoFocus)
		self.nappi_kansiorakenne.setToolTip("Jäsentele kansiorakenteen mukaan")
		self.nappi_kansiorakenne.setText("Kansio/Alikansio")
		self.nappi_kansiorakenne.clicked.connect(self.vaihda_kansiorakenteeseen)
		# Artisti/Albumi/Biisi
		self.nappi_artistirakenne = QtWidgets.QPushButton(self)
		self.nappi_artistirakenne.setGeometry(QtCore.QRect(*ARTISTIMOODI))
		self.nappi_artistirakenne.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.nappi_artistirakenne.setFocusPolicy(QtCore.Qt.NoFocus)
		self.nappi_artistirakenne.setToolTip("Jäsentele kansiorakenteen mukaan")
		self.nappi_artistirakenne.setText("Artisti/Albumi")
		self.nappi_artistirakenne.clicked.connect(self.vaihda_artistirakenteeseen)
		self.puumoodi = True # True: kansiorakenne, False: artistimoodi

		self.setWindowTitle("Musiikkikirjastoselain")
		self.resize(*IKKUNAMITAT)
		self.setMinimumSize(*IKKUNAMITAT)
		self.setMaximumSize(*IKKUNAMITAT)

		# Tekstikentän otsikkoteksti
		self.label_nimihaku = QtWidgets.QLabel(self)
		self.label_nimihaku.setGeometry(QtCore.QRect(*LABEL_NIMIHAKU))
		self.label_nimihaku.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
		self.label_nimihaku.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
		self.label_nimihaku.setText("Vapaahaku")

		# Tekstikenttä
		self.nimihaku = QtWidgets.QLineEdit(self)
		self.nimihaku.setGeometry(QtCore.QRect(*KENTTA_NIMIHAKU))
		self.nimihaku.setObjectName("nimihaku")
		self.nimihaku.setClearButtonEnabled(True)
		self.nimihaku.setText("Vapaahaku")
		self.nimihaku.selectAll()
		self.nimihaku.setCompleter(None)
		self.nimihaku.setToolTip("Täsmähaku lainausmerkeillä")

		# Hakunappi
		self.etsi = QtWidgets.QPushButton(self)
		self.etsi.setGeometry(QtCore.QRect(*NAPPI_ETSI))
		self.etsi.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.etsi.setFocusPolicy(QtCore.Qt.NoFocus)
		self.etsi.setText("Etsi")
		self.etsi.setShortcut("Return")
		self.etsi.clicked.connect(self.hae)

		# self.taulukko = QtWidgets.QLineEdit(self)
		self.taulukko = QtWidgets.QTextEdit(self)
		self.taulukko.setGeometry(QtCore.QRect(*TAULUKKOMITAT))
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
		self.asetusvalitsin.setToolTip("Valitse asetuskokoonpano (@ini)")
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
		self.tietokantavalitsin.setToolTip("Valitse musatietokanta")
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

		# Latausjono, elää omassa threadissään
		self.label_latauslista = QtWidgets.QLabel(self)
		self.label_latauslista.setGeometry(QtCore.QRect(*LATAUSLABEL))
		self.label_latauslista.setText("Latauslista:")
		self.latauslista = Latauslista(self, mitat=LATAUSLISTA)
		self.threadpool = QtCore.QThreadPool()
		self.odottaa = []
		self.lataus_menossa = False

		# Latausnappi
		self.latausnappi = QtWidgets.QPushButton(self)
		self.latausnappi.setStyleSheet("background-color: #373c41; color: white; font-weight: bold")
		self.latausnappi.setGeometry(QtCore.QRect(*NAPPI_LATAA))
		self.latausnappi.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.latausnappi.setFocusPolicy(QtCore.Qt.NoFocus)
		self.latausnappi.setText("Lataa")
		self.latausnappi.clicked.connect(self.lataa)

		# Sulkemistoiminto ctrl+q
		self.quitSc = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Q'), self)
		self.quitSc.activated.connect(QtWidgets.QApplication.instance().quit)

		# Tunnista milloin sovellus on juuri käynnistynyt
		self.initflag = False

	def kansoita_puu(self, puu, juuri=0, edellinen=None):
		'''
		Täytä puu annetun Tiedostopuun sisällöllä,
		boldaa ylimpien tasojen elementit.
		'''
		self.puumoodi = True # kerro muillekin palikoille
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

	def kansoita_puu_artistijako(self, artistipuu=None):
		'''
		Täytä puu annetun Artistipuun sisällöllä.
		Juuri
		 |-Artisti
		   |-Albumi
		     |-Biisi albumilla
			 |-Biisi albumilla
		'''
		if artistipuu is None and self.artistipuu is None:
			print("Jäsennellään tiedostopuu artistien mukaan, saattaa mennä hetki")
			self.artistipuu = cb.Artistipuu(self.tiedostopuu)
			print("Noin.")
			artistipuu = self.artistipuu
		elif artistipuu is None:
			artistipuu = self.artistipuu
		artistivari  = (255,255,255)
		albumivari   = (155,155,255)
		biisivari    = (155,255,155)
		korostusvari = (255, 0, 255)
		for artisti in artistipuu.artistit:
			artistielementti = Artistielementti(artistipuu, artisti, vari=artistivari)
			self.juurisolmu.appendRow(artistielementti)
			for albumi in artistipuu.artistit[artisti]:
				albumielementti = Albumielementti(artistipuu, artisti, albumi, vari=albumivari)
				artistielementti.appendRow(albumielementti)
				for raitatuple in artistipuu.artistit[artisti][albumi]:
					boldattu = False
					vari = biisivari
					if raitatuple[1].esittaja is not None and raitatuple[1].esittaja == artisti:
						boldattu = True
						vari = korostusvari
					raita = Raitaelementti(raitatuple, boldattu=boldattu, vari=vari)
					albumielementti.appendRow(raita)

	def parsi_hakutermit(self, teksti):
		'''
		Parsii hakukentän tekstin hakuargumenteiksi.
		Tätä kutsutaan ei-tyhjillä stringeillä.

		Teksti splitataan niin että hakutermit on erotettu
		välilyönneillä, poislukien "lainausmerkeillä ympäröidyt pätkät",
		jotka muodostavat yksittäisen hakutermin.
		'''
		if len(teksti) == 1:
			return([teksti])
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
			if oli_tuloksia:
				self.puumalli.clear()
				self.juurisolmu = self.puumalli.invisibleRootItem()
				if self.puumoodi:
					self.kansoita_puu(tulokset)
				else:
					alipuu = cb.Artistipuu(tulokset)
					self.kansoita_puu_artistijako(alipuu)
				self.puu.setModel(self.puumalli)
				self.puu.expandAll()
		if not haettavaa or not oli_tuloksia:
			self.puumalli.clear()
			self.juurisolmu = self.puumalli.invisibleRootItem()
			if self.puumoodi:
				self.kansoita_puu(self.tiedostopuu)
				self.puu.expand(self.puumalli.index(0,0))
			else:
				self.kansoita_puu_artistijako()

	def lataa(self):
		'''
		Lataa valittu asia.
		'''
		asia = self.puumalli.itemFromIndex(self.puu.currentIndex())
		latauslupa = False
		if type(asia) in [Kansioelementti, Artistielementti, Albumielementti]:
			biiseja = asia.sisallon_maara()
			latauslupa = False
			# Monta kappaletta, varmistetaan
			if biiseja > kvak.VAROITURAJA:
				vaaraikkuna = Vaara_monta(biiseja)
				if vaaraikkuna.clickedButton() is vaaraikkuna.juu:
					latauslupa = True
			# Ei kovin montaa kappaletta
			else:
				latauslupa = True
		# Yksittäinen kappale aina ok
		elif type(asia) in [Tiedostoelementti, Raitaelementti]:
			latauslupa = True
		# Mene
		if latauslupa:
			self.latauslista.lisaa(asia)
			self.odottaa.append(asia)
			if not self.lataus_menossa:
				self.aloita_lataus()

	def aloita_lataus(self):
		'''
		Aloita latausjonon läpikäyminen.
		'''
		self.lataus_menossa = True
		tyolainen = Latausorja(ladattavat=self.odottaa)
		tyolainen.signaalit.ladattu.connect(self.asia_ladattu)
		tyolainen.signaalit.valmis.connect(self.tyolainen_valmis)
		self.threadpool.start(tyolainen)
		self.odottaa = []

	def asia_ladattu(self):
		'''
		Asia on ladattu, poista se latauslistasta.
		'''
		asia = self.latauslista.takeItem(0)
		if asia is not None:
			print("Ladattiin {}".format(asia.text()))

	def tyolainen_valmis(self):
		'''
		Työläinen on valmis lataustensa kanssa,
		aloita uusi rumba. Vain jos on jotain ladattavaa jonossa.
		'''
		self.lataus_menossa = False
		if len(self.odottaa):
			self.aloita_lataus()

	def nayta_tiedot(self):
		'''
		Näytä valitun biisin tai kansion tiedot.
		'''
		st = ""
		if type(self.puumalli.itemFromIndex(self.puu.currentIndex())) in [Kansioelementti, Tiedostoelementti, Artistielementti, Albumielementti, Raitaelementti]:
			st = str(self.puumalli.itemFromIndex(self.puu.currentIndex()))
			print(st)
		self.taulukko.setText(st)

	def vaihda_kansiorakenteeseen(self):
		'''
		Vaihda selausmoodi kansiorakenteeseen.
		'''
		self.puumoodi = True
		# self.puumalli.clear()
		# self.juurisolmu = self.puumalli.invisibleRootItem()
		self.hae()
		# self.kansoita_puu(self.tiedostopuu)

	def vaihda_artistirakenteeseen(self):
		'''
		Vaihda selausmoodi kansiorakenteeseen.
		'''
		self.puumoodi = False
		# self.puumalli.clear()
		# self.juurisolmu = self.puumalli.invisibleRootItem()
		self.hae()
		# self.kansoita_puu_artistijako(self.artistipuu)

	def vaihda_tietokantaa(self):
		'''
		Vaihda mitä tietokantaa käytetään pohjana.
		'''
		tietokantatiedosto = self.tietokantavalitsin.currentText()
		if os.path.exists(tietokantatiedosto):
			if not self.initflag:
				# self.juurisolmu.removeRow(0)
				self.puumalli.clear()
				self.juurisolmu = self.puumalli.invisibleRootItem()
			self.tiedostopuu = Tiedostopuu(tiedostotyyppi=cb.Biisi)
			tietokanta = open(tietokantatiedosto, "r")
			self.tiedostopuu.lue_tiedostosta(tietokanta)
			tietokanta.close()
			self.artistipuu = None
			if self.puumoodi:
				self.kansoita_puu(self.tiedostopuu)
			else:
				self.kansoita_puu_artistijako()
		elif len(tietokantatiedosto):
			print(f"Tietokantatiedostoa \"{tietokantatiedosto}\" ei ole.")

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
