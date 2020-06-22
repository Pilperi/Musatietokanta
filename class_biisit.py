'''
Biisien ja biisikirjastojen luokkamääritelmät,
biisien metadatan lukuun tarvittavat funktiot,
ja näiden tietojen luku ja kirjoitus tietokantatiedostosta.

Pohjaa lähinnä moduuleihin 'mutagen' (metadatan luku)
ja 'json' (tiedon jäsentely).
'''

import mutagen as mtg
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
	def __init__(self, kansio=None):
		pass


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

		# Lukukohteena tiedostopolku (str)
		if type(kohteesta) is str:
			lue_tiedostosta(tiedostopolku)

		# Lukukohteena dikti (luettu tiedostosta tmv)
		elif type(kohteesta) is dict:
			lue_diktista(dikti)

	def lue_tiedostosta(self, tiedostopolku):
		'''
		Lue biisin tiedot tiedostosta.
		Metadatan tyyppi arvataan päätteestä
		ja mietitään sit myöhemmin jos asiat ei toimikaan.
		'''
		paate = kfun.paate(tiedostopolku)[1].lower()
		if paate in kvak.MUSATIEDOSTOT:
			if paate == "mp3":
				pass
			elif paate == "flac":
				data = mtg.File(tiedostopolku)
			elif paate == "wav":
				pass

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