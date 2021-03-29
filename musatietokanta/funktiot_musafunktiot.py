import os
import shutil
import subprocess
import hashlib
from . import vakiot_musavakiot as mvak
from tiedostohallinta import funktiot_kansiofunktiot as kfun

def lisaa_soittolistaan(tyyppi="kansio", sijainti=mvak.BIISIKANSIO):
	'''
	Lisää kappale tai kansio soitinohjelman soittolistalle,
	komennolla joka määritelty vakioiden puolella.
	'''
	koodi = False
	if tyyppi == "kansio":
		koodi = subprocess.call([*mvak.KOMENTO_LISAA_KANSIO_SOITTOLISTAAN, sijainti])
		print(koodi)
	elif len(paate(sijainti)[1]) and kfun.paate(sijainti)[1].lower() in mvak.MUSATIEDOSTOT:
		koodi = subprocess.call([*mvak.KOMENTO_LISAA_KAPPALE_SOITTOLISTAAN, sijainti])
		print(koodi)
	return(koodi)

def lataa_ja_lisaa_soittolistaan(vaintiedosto, lahdepalvelin, lahdepolku, kohdepalvelin, kohdepolku):
	'''
	Lataa biisi tai kansio paikalliselle kovalevylle ja sen jälkeen lisää soittolistaan.

	Ottaa:
	vaintiedosto: bool
		Jos True, yksittäinen tiedosto. Muutoin kansio.
	lahdepalvelin: str tai Falseksi kääntyvä
		Lähdepalvelimen nimi. Jos "tyhjä"" (bool->False), paikallinen sijainti.
	lahdepolku: str
		Kansiopolku ladattavalle asialle, oli se sitten paikallinen tai etäjuttu.
	kohdepalvelin: str tai Falseksi kääntyvä
		Kohdepalvelin. Jos "tyhjä" (bool->False), paikallinen sijainti.
	kohdepolku: str
		Kansiopolku jonne kopioidaan.
	'''
	# Polku palvelimella
	if lahdepalvelin:
		kansiopolku = "{}".format(kfun.siisti_tiedostonimi(lahdepolku))
	# Paikallinen polku
	else:
		kansiopolku = "{}".format(kfun.siisti_tiedostonimi(lahdepolku))
	# Polku palvelimella
	if kohdepalvelin:
		kohde = "{}:{}".format(kohdepalvelin, kfun.siisti_tiedostonimi(kohdepolku))
	# Paikallinen polku
	else:
		kohde = kohdepolku.replace("\"", "\\\"")
	skripti_sijainti = os.path.join(mvak.TYOKANSIO "lataa_ja_lisaa.sh") # kun tavallinen purkka ei riitä
	if vaintiedosto and len(kfun.paate(kohde)[1]) and kfun.paate(kohde)[1].lower() in mvak.MUSATIEDOSTOT:
		print(f"Ladataan tiedosto \n{kansiopolku}\nkohteeseen\n{kohde}")
		subprocess.run([skripti_sijainti, lahdepalvelin, kansiopolku, kohde, str(int(vaintiedosto)), mvak.KOMENTO_LISAA_KAPPALE_SOITTOLISTAAN])
		# subprocess.Popen(["scp", "-T", kansiopolku, kohde, *kvak.KOMENTO_LISAA_KANSIO_SOITTOLISTAAN, kohde])
	else:
		print(f"Ladataan kansio \n{kansiopolku}\nkohteeseen\n{kohde}")
		subprocess.run([skripti_sijainti, lahdepalvelin, kansiopolku, kohde, str(int(vaintiedosto)), mvak.KOMENTO_LISAA_KANSIO_SOITTOLISTAAN])
		# subprocess.Popen(["scp","-r", "-T", kansiopolku, kohde, *kvak.KOMENTO_LISAA_KAPPALE_SOITTOLISTAAN, kohde])
