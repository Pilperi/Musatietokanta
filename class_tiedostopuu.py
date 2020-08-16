import os
import json
import vakiot_kansiovakiot as kvak

class Tiedostopuu():
	'''
	Tiedostopuun luokka, hyvinni yleinen sellainen.
	Käytännössä sisältää tiedot kansioista
	ja siitä, mitä tiedostoja on minkäkin kansion alla,
	jottei tarvitse roikottaa täysiä tiedostopolkuja
	koko aikaa messissä.
	Pääpointti lähinnä siinä, että asiat saadaan
	kirjoitettua tiedostoon fiksusti ja luettua sieltä ulos.
	'''
	def __init__(self, kansio=None, edellinenkansio=None, syvennystaso=0, tiedostotyyppi=None, TULOSTA=False):
		if TULOSTA:
			print(kansio)
		self.edellinentaso  = edellinenkansio	# edellinen kansio (Tiedostopuu tai None)
		self.syvennystaso   = syvennystaso		# int, monesko kerros menossa
		self.kansio         = kansio 			# str, pelkkä kansionimi jollei ylin kansio
		self.tiedostot      = [] 				# Lista tiedostoja (aika mielivaltaisia, kunhan kääntyy JSON:iksi)
		self.alikansiot     = [] 				# Lista Tiedostopuita
		self.tiedostotyyppi = tiedostotyyppi    # Minkä luokan olioita tiedostolistoihin lykätään

	def kansoita(self):
		'''
		Lado kansion tiedostot tiedostolistaan ja
		alikansiot alikansiolistaan.
		'''
		nykyinen_polku = self.hae_nykyinen_polku()
		tiedostot, alikansiot = kfun.kansion_sisalto(self.hae_nykyinen_polku(), kvak.MUSATIEDOSTOT)
		# Tiedostot tiedostolistaan (tässä vaihtelee, minkä tyyppinen tiedosto kyseessä)
		if type(self.tiedostotyyppi) is type:
			for tiedosto in tiedostot:
				self.tiedostot.append(self.tiedostotyyppi(os.path.join(self.hae_nykyinen_polku(), tiedosto)))
		# Alikansiot yhtä tasoa syvemmällä, ole näiden 'edellinenkansio'
		for kansio in alikansiot:
			puu = Tiedostopuu(kansio, self, self.syvennystaso+1, tiedostotyyppi=self.tiedostotyyppi)
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
				# Tapaus tiedosto nykyisellä syvennystasolla: lisää tiedostolistaan
				if type(self.tiedostotyyppi) is not None and rivi[i] == "{":
					# print("Tämän kansion tiedosto")
					diktitiedosto = json.loads(rivi[i:-1])
					self.tiedostot.append(self.tiedostotyyppi(diktitiedosto))
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
					alipuu = Tiedostopuu(kansionimi, self, self.syvennystaso+1, tiedostotyyppi=self.tiedostotyyppi)
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
		Kansiot ja tiedostot erottaa siitä että tiedostojen tiedot on {} välissä
		ja kansiot "" välissä
		'''
		st = "{:d}\"{:s}\"\n".format(self.syvennystaso, str(self.kansio))
		for tiedosto in self.tiedostot:
			st += "{:d}{:s}\n".format((self.syvennystaso+1), str(tiedosto))
		for kansio in self.alikansiot:
			st += str(kansio)
		return(st)
