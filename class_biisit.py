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
import multiprocessing

TULOSTA = True
#TULOSTA = False

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
	def __init__(self, kansio=None, edellinenkansio=None, syvennystaso=0):
		if TULOSTA:
			print(kansio)
		self.edellinentaso  = edellinenkansio	# edellinen kansio (Tiedostopuu tai None)
		self.syvennystaso   = syvennystaso		# int, monesko kerros menossa
		self.kansio         = kansio 			# str, pelkkä kansionimi jollei ylin kansio
		self.biisit         = [] 				# Lista biisejä
		self.alikansiot     = [] 				# Lista Tiedostopuita

	def kansoita(self):
		'''
		Lado kansion biisit biisilistaan ja
		alikansiot alikansiolistaan.
		'''
		nykyinen_polku = self.hae_nykyinen_polku()
		biisit, alikansiot = kfun.kansion_sisalto(self.hae_nykyinen_polku(), kvak.MUSATIEDOSTOT)
		# Biisit biisilistaan
		for biisi in biisit:
			self.biisit.append(Biisi(os.path.join(self.hae_nykyinen_polku(), biisi)))
		# Alikansiot yhtä tasoa syvemmällä, ole näiden 'edellinenkansio'
		for kansio in alikansiot:
			puu = Tiedostopuu(kansio, self, self.syvennystaso+1)
			puu.kansoita()
			self.alikansiot.append(puu)

	def lue_tiedostosta(self, tiedosto):
		'''
		Lue puurakenne tietokantatiedostosta.
		Huom. 'tiedosto' on tiedostokahva (vai mikälie), ei tiedostopolku str
		'''
		rivi = tiedosto.readline()
		# Jos pääkansio, lue tietokannan pääkansion nimi
		# ekalta riviltä ja siirry seuraavalle
		if self.syvennystaso == 0 and rivi and rivi[1] == "\"":
			kansionimi = ""
			i = 2
			while rivi[i] != "\"":
				kansionimi += rivi[i]
				i += 1
			self.kansio = kansionimi
			rivi = tiedosto.readline()
		# print("\nKansio: {}\nEdellinen: {}\nSyvennystaso: {}".format(self.kansio, self.edellinentaso, self.syvennystaso))
		while rivi:
			# Laske syvennystaso: rivin alussa luvut ilmaisemassa
			syvennys = ""
			i = 0
			while rivi[i].isnumeric():
				syvennys += rivi[i]
				i += 1
			syvennys = int(syvennys)
			# print("Asian taso: {}".format(syvennys))
			if syvennys == self.syvennystaso+1:
				# Tapaus biisi nykyisellä syvennystasolla: lisää biisilistaan
				if rivi[i] == "{":
					# print("Tämän kansion biisi")
					diktibiisi = json.loads(rivi[i:-1])
					self.biisit.append(Biisi(diktibiisi))
					rivi = tiedosto.readline()
				# Tapaus kansio: lisää Tiedostopuu alikansioihin
				elif rivi[i] == "\"":
					# Lue kansion nimi, joka on "" välissä
					i += 1
					kansionimi = ""
					while rivi[i] != "\"":
						kansionimi += rivi[i]
						i += 1
					# print("Kansion {} alikansio {}".format(self.kansio, kansionimi))
					alipuu = Tiedostopuu(kansionimi, self, self.syvennystaso+1)
					rivi = alipuu.lue_tiedostosta(tiedosto)
					self.alikansiot.append(alipuu)
			else:
				# Palauta viimeisin rivi, koska sitä tarvitaan vielä ylemmällä tasolla
				# print("Alemman tason asia.")
				return(rivi)

	def hae_nykyinen_polku(self):
		'''
		Hae nykyisen tason koko polku edeltävistä tasoista latomalla.
		'''
		polku = [self.kansio]
		ylempitaso = self.edellinentaso
		while ylempitaso is not None:
			if type(ylempitaso) is str:
				print(ylempitaso)
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
		st = "{:d}\"{:s}\"\n".format(self.syvennystaso, self.kansio)
		for biisi in self.biisit:
			# print(biisi.biisinimi)
			st += "{:d}{:s}\n".format((self.syvennystaso+1), str(biisi))
		for kansio in self.alikansiot:
			# print(type(kansio))
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
			self.lue_diktista(kohteesta)

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
				raitatiedot = self.raitatiedot(tagit.get("tracknumber"))
				if raitatiedot:
					self.raita			= raitatiedot[0]
				if raitatiedot and raitatiedot[1] is not None:
					self.raitoja = raitatiedot[1]
				elif tagit.get("tracktotal") and all([a.isnumeric for a in tagit.get("tracktotal")[0]]):
					try:
						self.raitoja		= int(tagit.get("tracktotal")[0])
					except ValueError:
						self.raitoja 		= 0
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
				try:
					raita = int(splitattu[0])
				except ValueError:
					raita = 0
			if len(splitattu) > 1 and all([a.isnumeric for a in splitattu[1]]):
				try:
					raitoja = int(splitattu[1])
				except ValueError:
					raitoja = 0
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


class Hakukriteerit:
	'''
	Hakukriteerien luokka.
	Helpompi että kriteerinäätitelmät on täällä
	piilossa kuin että roikkuvat jossain
	erillisessä funktiossa tmv. (?)
	'''
	def __init__(self, dikti={}):
		self.ehtona_ja       = dikti.get("ehtona_ja")   # onko str-haut ja- vai tai-rakenteisia
		self.artistinimessa  = dikti.get("artistissa")  # lista stringejä
		self.biisinimessa    = dikti.get("biisissa")    # lista stringejä
		self.albuminimessa   = dikti.get("albumissa")   # lista stringejä
		self.tiedostonimessa = dikti.get("tiedostossa") # lista stringejä
		self.raitanumero     = dikti.get("raitanumero") # tuple inttejä

		self.hakukriteereita = len(dikti.keys())-1
		self.tulospuu        = None                     # Tiedostopuu hakutuloksille
		self.hakutuloksia    = 0                        # Montako tulosta löytyi

	def tarkista_biisi(self, biisi, puu):
		'''
		Tarkista biisistä, täyttääkö se annetut hakuehdot.
		Jos jokin annetuista hakuehdoista ei täsmää, palauta False.
		Jos mikään ei palauta Falsea, ehdot täyttyvät.
		'''
		tayttyneet_kriteerit = 0
		# Artistin nimellä haku
		if self.artistinimessa is not None and type(biisi.esittaja) is str:
			if self.ehtona_ja:
				if not(all([a in biisi.esittaja.lower() for a in self.artistinimessa])):
					# print("{}: artistin nimi ei täsmää".format(biisi.esittaja))
					return(False)
			else:
				if not(any([a in biisi.esittaja.lower() for a in self.artistinimessa])):
					# print("{}: artistin nimi ei täsmää".format(biisi.esittaja))
					return(False)
			tayttyneet_kriteerit += 1
		# Biisin nimellä haku
		if self.biisinimessa is not None and type(biisi.biisinimi) is str:
			if self.ehtona_ja:
				if not(all([a in biisi.biisinimi.lower() for a in self.biisinimessa])):
					# print("{}: biisin nimi ei täsmää".format(biisi.biisinimi))
					return(False)
			else:
				if not(any([a in biisi.biisinimi.lower() for a in self.biisinimessa])):
					# print("{}: biisin nimi ei täsmää".format(biisi.biisinimi))
					return(False)
			tayttyneet_kriteerit += 1
		# Albumin nimellä haku
		if self.albuminimessa is not None and type(biisi.albuminimi) is str:
			if self.ehtona_ja:
				if not(all([a in biisi.albuminimi.lower() for a in self.albuminimessa])):
					# print("{}: albumin nimi ei täsmää".format(biisi.albuminimi))
					return(False)
			else:
				if not(any([a in biisi.albuminimi.lower() for a in self.albuminimessa])):
					# print("{}: albumin nimi ei täsmää".format(biisi.albuminimi))
					return(False)
			tayttyneet_kriteerit += 1
		# Tiedoston nimellä haku (biisin tiedostonimi tai kansionimi)
		if self.tiedostonimessa is not None and type(biisi.tiedostonimi) is str:
			if not self.tarkista_kansio(puu):
				if self.ehtona_ja:
					if not all([a in biisi.tiedostonimi.lower() for a in self.tiedostonimessa]):
						# print("{}: tiedostonimi ei täsmää".format(biisi.tiedostonimi))
						return(False)
				else:
					if not any([a in biisi.tiedostonimi.lower() for a in self.tiedostonimessa]):
						# print("{}: tiedostonimi ei täsmää".format(biisi.tiedostonimi))
						return(False)
			tayttyneet_kriteerit += 1
		# Raitanumeron perusteella haku
		if self.raitanumero is not None and type(biisi.raita) is int:
			if biisi.raita not in range(self.raitanumero[0], self.raitanumero[1]+1):
				# print("{}: raitanumero ei täsmää".format(biisi.raita))
				return(False)
			tayttyneet_kriteerit += 1
		# Kaikki annetut ehdot täyttyivät:
		if tayttyneet_kriteerit >= self.hakukriteereita:
			# print("MÄTSI {}".format(biisi.biisinimi))
			return(True)
		# print("Ei riittävästi täyttyneitä kriteereitä: {}/{}".format(tayttyneet_kriteerit, self.hakukriteereita))
		return(False)

	def tarkista_kansio(self, puu):
		'''
		Joskus on paikallaan hakea stringiä tiedostopolusta
		mukaanlukien kansion nimi. Simppeli funktio erillään
		biisitarkastuksesta, koska biisien tiedoissa ei ole tietoa
		kansiopolusta.
		'''
		if self.tiedostonimessa is not None:
			puupolku = puu.hae_nykyinen_polku().lower()
			if self.ehtona_ja and not all([a in puupolku for a in self.tiedostonimessa]):
				return(False)
			elif (not self.ehtona_ja) and (not any([a in puupolku for a in self.tiedostonimessa])):
				return(False)
			return True
		return(False)


	def etsi_tietokannasta(self, puu, uusipuu=None):
		'''
		Etsi annetusta tiedostopuusta kaikki biisit jotka täyttävät
		hakukriteerit, Tiedostopuun muodossa (karsittu versio annetusta puusta)
		'''
		tuloksia = False # Onko annetussa puussa käypiä hakutuloksia vai ei (rekursiota varten)
		if self.tulospuu is None:
			self.tulospuu = Tiedostopuu(puu.kansio)
		for biisi in puu.biisit:
			if self.tarkista_biisi(biisi, puu):
				self.hakutuloksia += 1
				# print("{} täyttää hakuehdot".format(biisi.biisinimi))
				tuloksia = True
				if uusipuu is None:
					# Juuripuu
					self.tulospuu.biisit.append(biisi)
				else:
					# Alikansio
					uusipuu.biisit.append(biisi)
		for alikansio in puu.alikansiot:
			# Katso rekursiivisesti, onko alikansiossa yhtään osumaa.
			# Jos on, lisää tulospuun alikansio-osastolle.
			# On myös mahdollista että koko alikansio on validi,
			# koska kansion nimessä on 'tiedostonimi'-hakustringin osuma.
			if uusipuu is None:
				alipuu = Tiedostopuu(alikansio.kansio, puu, puu.syvennystaso+1)
			else:
				alipuu = Tiedostopuu(alikansio.kansio, uusipuu, uusipuu.syvennystaso+1)
			kansiossa_oli, tuloskansio = self.etsi_tietokannasta(alikansio, uusipuu=alipuu)
			if kansiossa_oli and uusipuu is None:
				tuloksia = True
				self.tulospuu.alikansiot.append(tuloskansio)
			elif kansiossa_oli:
				tuloksia = True
				uusipuu.alikansiot.append(tuloskansio)
		if uusipuu is None:
			uusipuu = self.tulospuu
		return(tuloksia, uusipuu)


def kirjaa():
	'''
	Kirjaa musiikkitiedot tietokantatiedostoihin.
	'''
	t1 = time.time()
	for i,lokaali_musakansio in enumerate(kvak.LOKAALIT_MUSIIKIT):
		puu = Tiedostopuu(lokaali_musakansio)
		puu.kansoita()
		tietokantatiedosto = kvak.LOKAALIT_TIETOKANNAT[i]
		f = open(tietokantatiedosto, "w+")
		f.write(str(puu))
		f.close()
	t2 = time.time()
	print("Aikaa kului {:.2f} s".format(t2-t1))

def lukutesti():
	'''
	Lue tietokannat tiedostoista Tiedostopuiksi
	ja kirjaa puut toisiin tietokantoihin, jotta voidaan
	testata onnistuuko toisiminen yks yhteen.
	'''
	for tiedosto in kvak.LOKAALIT_TIETOKANNAT:
		puu = Tiedostopuu()
		f = open(tiedosto, "r")
		puu.lue_tiedostosta(f)
		f.close()
		o = open(tiedosto.replace(".tietokanta", "_kopio.tietokanta"), "w+")
		o.write(str(puu))
		o.close()

if __name__ == "__main__":
	pass
	# Testaa hakukriteereiden käyttöä:
	#hakudikti = {
	#			"ehtona_ja":     False,
	#			# "artistissa":    ["妖精", "亭刻"],
	#			# "biisissa":      ["ノゾム", "神"],
	#			# "albumissa":     ["神"],
	#			# "tiedostossa":   ["eroge"],
	#			"raitanumero":   (1,3)
	#			}
	#haku = Hakukriteerit(hakudikti)
	#oli_tuloksia, tulokset = haku.etsi_tietokannasta(puu)
	#print("Tuloksia: {:d}".format(haku.hakutuloksia))
	# Kirjaa tulokset tiedostoon
	#f = open(kvak.LOKAALIT_TIETOKANNAT[0].replace(".tietokanta", "_hakutulokset.tietokanta"), "w+")
	#f.write(str(tulokset))
	#f.close()
