'''
Biisien ja biisikirjastojen luokkamääritelmät,
biisien metadatan lukuun tarvittavat funktiot,
ja näiden tietojen luku ja kirjoitus tietokantatiedostosta.

Pohjaa lähinnä moduuleihin 'mutagen' (metadatan luku)
ja 'json' (tiedon jäsentely).
'''

import os
import time
import json
import mutagen as mtg
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
import vakiot_kansiovakiot as kvak
import funktiot_kansiofunktiot as kfun

class Tiedostopuu():
	'''
	Tiedostopuun luokka.
	Käytännössä sisältää tiedot kansioista
	ja siitä, mitä biisejä on minkäkin kansion alla,
	jottei tarvitse roikottaa täysiä tiedostopolkuja
	koko aikaa messissä.
	Pääpointti lähinnä siinä, että asiat saadaan
	kirjoitettua tiedostoon fiksusti ja luettua sieltä ulos.
	'''
	def __init__(self, kansio, edellinenkansio=None, syvennystaso=0):
		self.edellinentaso  = edellinenkansio	# edellinen kansio (Tiedostopuu tai None)
		self.syvennystaso	= syvennystaso		# int, monesko kerros menossa
		self.kansio			= kansio 			# str, pelkkä kansionimi jollei ylin kansio
		self.biisit 		= [] 				# Lista biisejä
		self.alikansiot		= [] 				# Lista Tiedostopuita

		self.kansoita()

	def kansoita(self):
		'''
		Lado kansion biisit biisilistaan ja
		alikansiot alikansiolistaan.
		'''
		biisit, alikansiot = kfun.kansion_sisalto(self.hae_nykyinen_polku(), kvak.MUSATIEDOSTOT)
		# Biisit biisilistaan
		for biisi in biisit:
			self.biisit.append(Biisi(os.path.join(self.hae_nykyinen_polku(), biisi)))
		# Alikansiot yhtä tasoa syvemmällä, ole näiden 'edellinenkansio'
		for kansio in alikansiot:
			self.alikansiot.append(Tiedostopuu(kansio, self, self.syvennystaso+1))

	def hae_nykyinen_polku(self):
		'''
		Hae nykyisen tason koko polku edeltävistä tasoista latomalla.
		'''
		polku = [self.kansio]
		ylempitaso = self.edellinentaso
		while ylempitaso is not None:
			polku.append(ylempitaso.kansio)
			ylempitaso = ylempitaso.edellinentaso
		polku.reverse()
		polkustringi = ""
		for osa in polku:
			polkustringi += osa+"/"
		return(polkustringi)

	def __str__(self):
		'''
		Rekursiivinen str-operaatio, käydään kaikki alikansiotkin läpi.
		Kansiot ja biisit erottaa siitä että biisien tiedot on {} välissä
		ja kansioiden nimet eivät ala "{" ja lopu "}" (...eihän?)
		'''
		st = "{:s}{:s}\n".format(" "*self.syvennystaso, self.kansio)
		for biisi in self.biisit:
			st += "{:s}{:s}\n".format(" "*(self.syvennystaso+1), str(biisi))
		for kansio in self.alikansiot:
			st += str(kansio)
		return(st)



class Biisi():
	'''
	Biisitietojen perusluokka.
	Biiseistä ei tarvitse ihan kauheaa
	määrää tietoa, kenttiä voi "helposti"
	lisäillä sitten jälkikäteen jos tarvitsee.
	'''
	def __init__(self, kohteesta=None):
		'''
		Alustetaan biisi nulleilla,
		ja jos (kun) 'kohteesta'-parametri on määritelty,
		täytetään tiedot sen mukaan.
		'''
		# Tiedostopolusta pelkkä loppuosa,
		# turha toistaa samoja pätkiä moneen kertaan
		# (pidetään kirjaa muualla)
		self.tiedostonimi	= None
		self.albuminimi		= None
		self.albumiesittaja = None
		self.esittaja		= None
		self.biisinimi		= None
		self.vuosi			= None
		self.raita			= None
		self.raitoja		= None
		self.lisayspaiva	= None

		# Lukukohteena tiedostopolku (str)
		if type(kohteesta) is str:
			self.lue_tiedostosta(kohteesta)

		# Lukukohteena dikti (luettu tiedostosta tmv)
		elif type(kohteesta) is dict:
			self.lue_diktista(dikti)

	def lue_tiedostosta(self, tiedostopolku):
		'''
		Lue biisin tiedot tiedostosta.
		Metadatan tyyppi arvataan päätteestä
		ja mietitään sit myöhemmin jos asiat ei toimikaan.
		Hitto kun kaikki mutagenin paluuarvot on yhden alkion listoja...
		'''
		paate = kfun.paate(tiedostopolku)[1].lower()
		if paate in kvak.MUSATIEDOSTOT:
			if paate == "mp3":
				tagit = EasyID3(tiedostopolku)
				# print(tagit)
				self.tiedostonimi	= os.path.basename(tiedostopolku)
				if tagit.get("album"):
					self.albuminimi		= tagit.get("album")[0]
				if tagit.get("albumartist"):
					self.albumiesittaja = tagit.get("albumartist")[0]
				if tagit.get("artist"):
					self.esittaja		= tagit.get("artist")[0]
				if tagit.get("title"):
					self.biisinimi		= tagit.get("title")[0]
				if tagit.get("date"):
					self.vuosi			= tagit.get("date")[0]
				self.raita			= self.raitatiedot(tagit.get("tracknumber"))[0]
				self.raitoja		= self.raitatiedot(tagit.get("tracknumber"))[1]
				self.lisayspaiva	= self.paivays()[0]
			elif paate == "flac":
				tagit = FLAC(tiedostopolku)
				self.tiedostonimi	= os.path.basename(tiedostopolku)
				if tagit.get("album"):
					self.albuminimi		= tagit.get("album")[0]
				if tagit.get("albumartist"):
					self.albumiesittaja = tagit.get("albumartist")[0]
				if tagit.get("artist"):
					self.esittaja		= tagit.get("artist")[0]
				if tagit.get("title"):
					self.biisinimi		= tagit.get("title")[0]
				if tagit.get("date"):
					self.vuosi			= tagit.get("date")[0]
				if tagit.get("tracknumber") and all([a.isnumeric for a in tagit.get("tracknumber")[0]]):
					self.raita			= int(tagit.get("tracknumber")[0])
				if tagit.get("tracktotal") and all([a.isnumeric for a in tagit.get("tracktotal")[0]]):
					self.raitoja		= int(tagit.get("tracktotal")[0])
				self.lisayspaiva	= self.paivays()[0]
			elif paate == "wma":
				# Tää on kamala eikä pitäisi olla vuonna 2020
				tagit = mtg.File(tiedostopolku)
				self.tiedostonimi	= os.path.basename(tiedostopolku)
				if tagit.get("Author"):
					self.albumiesittaja = tagit.get("Author")[0].value
					self.esittaja		= self.albumiesittaja
				if tagit.get("Title"):
					self.biisinimi		= tagit.get("Title")[0].value
				if tagit.get("WM/TrackNumber"):
					self.raita			= tagit.get("WM/TrackNumber")[0].value
					self.raitoja		= self.raita
				self.lisayspaiva	= self.paivays()[0]

	def raitatiedot(self, raitatagi):
		'''
		Lue raitanumero ja kokonaisraitamäärä
		metadatasta. Data hankalasti joko muotoa
		'n' (raidannumero) tai 'n/m' (raita/raitoja),
		niin täytyy vähän parsia.
		'''
		(raita, raitoja) = (None, None)
		# Pitäisi olla ei-tyhjä lista
		if raitatagi:
			splitattu = raitatagi[0].split("/")
			if all([a.isnumeric for a in splitattu[0]]):
				raita = int(splitattu[0])
			if len(splitattu) > 1 and all([a.isnumeric for a in splitattu[1]]):
				raitoja = int(splitattu[1])
		return((raita, raitoja))

	def paivays(self, lue=None):
		'''
		Muodosta tai lue päiväys, formaatissa
		(inttimuoto yyyymmdd, (yyyy, mm, dd))-tuple
		'''
		kokoversio	= 0
		vuosi		= 0
		kuukausi	= 0
		paivays		= 0
		# Pilko annettu päiväys
		if type(lue) in [int, str]:
			stringiversio = str(lue)
			if len(stringiversio) == 8 and all([a.isnumeric for a in stringiversio]):
				kokoversio	= int(stringiversio)
				vuosi		= int(stringiversio[:4])
				kuukausi	= int(stringiversio[4:6])
				paivays		= int(stringiversio[6:8])
		# Nykyhetken päiväys
		else:
			paivays  = time.localtime()
			vuosi    = paivays.tm_year
			kuukausi = paivays.tm_mon
			paivays  = paivays.tm_mday
			kokoversio = int("{:04d}{:02d}{:02d}".format(vuosi,kuukausi,paivays))
		return((kokoversio, (vuosi, kuukausi, paivays)))

	def lue_diktista(self, dikti):
		'''
		Koetetaan lukea diktistä metadatat.
		'''
		self.tiedostonimi	= dikti.get("tiedostonimi")
		self.albuminimi		= dikti.get("albuminimi")
		self.albumiesittaja = dikti.get("albumiesittaja")
		self.esittaja		= dikti.get("esittaja")
		self.biisinimi		= dikti.get("biisinimi")
		self.vuosi			= dikti.get("vuosi")
		self.raita			= dikti.get("raita")
		self.raitoja		= dikti.get("raitoja")
		self.lisayspaiva	= dikti.get("lisayspaiva")

	def __str__(self):
		diktiversio = {
					"tiedostonimi":		self.tiedostonimi,
					"esittaja":			self.esittaja,
					"biisinimi":		self.biisinimi,
					"albuminimi":		self.albuminimi,
					"raita":			self.raita,
					"raitoja":			self.raitoja,
					"vuosi":			self.vuosi,
					"albumiesittaja":	self.albumiesittaja,
					"lisayspaiva":		self.lisayspaiva
					}
		return(json.dumps(diktiversio))


if __name__ == "__main__":
	testikansio = "/home/pilperi/Scripts/Musatietokanta/Testikansio/"
	puu = Tiedostopuu(testikansio)
	# print(puu)
	tietokantatiedosto = "/home/pilperi/Scripts/Musatietokanta/ulosanti.tietokanta"
	f = open("ulosanti.tietokanta", "w+")
	f.write(str(puu))
	f.close()