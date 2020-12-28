import os
import shutil
import subprocess
import hashlib
import vakiot_kansiovakiot as kvak

def lataa(vaintiedosto, lahdepalvelin, lahdepolku, kohdepalvelin, kohdepolku):
	'''
	Lataa SCP:llä biisi tai kansio kansiopolusta (/lokaali/polku tai servu:/polku/servulla)
	määränpäähän (/lokaali/polku tai servu:/polku/servulla)
	'''
	# Polku palvelimella
	if lahdepalvelin:
		kansiopolku = "{}:{}".format(lahdepalvelin, siisti_tiedostonimi(lahdepolku))
	# Paikallinen polku
	else:
		# kansiopolku = "\"{}\"".format(lahdepolku)
		kansiopolku = "{}".format(siisti_tiedostonimi(lahdepolku))
	# Polku palvelimella
	if kohdepalvelin:
		kohde = "{}:{}".format(kohdepalvelin, siisti_tiedostonimi(kohdepolku))
	# Paikallinen polku
	else:
		# kohde = "\"{}\"".format(kohdepolku)
		kohde = "{}".format(kohdepolku)

	print(kansiopolku)
	print(kohde)
	if vaintiedosto:
		koodi = subprocess.call(["scp", "-T", kansiopolku, kohde])
		# koodi = subprocess.call(["scp", kansiopolku, kohde])
	else:
		koodi = subprocess.call(["scp","-r", "-T", kansiopolku, kohde])
	if koodi != 1:
		return(True)
	return(False)

def siisti_tiedostonimi(nimi):
	'''
	Siisti tiedostonimen hankalat merkit scp-yhteensopiviksi,
	koska ähhh.
	
	Ottaa:
	nimi : str
		Stringi jonka ikävät merkit muokataan vähemmän ikäviksi.

	Palauttaa:
	nimi : str
		Siivottu stringi.
	'''
	nimi = nimi.replace("\"", "\\\"")\
		      .replace(" ", "\\ ")\
		      .replace("\'", "\\\'")\
		      .replace("!", "\\!")\
		      .replace("(", "\\(")\
		      .replace(")", "\\)")\
		      .replace("&", "\\&")\
		      .replace(";", "\\;")
	return(nimi)

def hanki_hash(tiedosto, binmode=True):
	'''
	Laskee annetun tiedoston md5-summan heksana,
	lukemalla sitä sopivan kokoinen palanen kerrallaan.
	Parametri 'binmode' määrittää, luetaanko tiedostoa
	binäärimuodossa (metadatoineen kaikkineen) vai
	tiedoston varsinaista sisältöä utf8-merkkeinä.
	Oletuksena 64kb binääripaloina,
	binmode=False -> 4000 merkkiä kerrallaan.
	'''
	md5 = hashlib.md5()
	if os.path.exists(tiedosto):
		if binmode:
			with open(tiedosto, 'rb') as filu:
				while True:
					data = filu.read(kvak.BUFFERI)
					if not data:
						break
					md5.update(data)
		else:
			with open(tiedosto, 'r') as filu:
				while True:
					data = filu.read(kvak.MERKKIBUFFERI)
					if not data:
						break
					md5.update(data.encode("utf-8"))
	return(md5.hexdigest())

def lisaa_soittolistaan(tyyppi="kansio", sijainti=kvak.BIISIKANSIO):
	'''
	Lisää kappale tai kansio soitinohjelman soittolistalle,
	komennolla joka määritelty vakioiden puolella.
	'''
	koodi = False
	if tyyppi == "kansio":
		print("kansio")
		koodi = subprocess.call([*kvak.KOMENTO_LISAA_KANSIO_SOITTOLISTAAN, sijainti])
		print(koodi)
	elif len(paate(sijainti)[1]) and paate(sijainti)[1].lower() in kvak.MUSATIEDOSTOT:
		print("kappale")
		koodi = subprocess.call([*kvak.KOMENTO_LISAA_KAPPALE_SOITTOLISTAAN, sijainti])
		print(koodi)
	return(koodi)

#------------Funktiot kansiorakenteiden läpikäymiseen--------------------------
def paate(tiedosto):
	'''
	Pilkkoo tiedoston filu.pääte osiin 'filu' ja 'pääte'
	'''
	paate = tiedosto.split(".")[-1]
	if len(paate) < len(tiedosto):
		alkuosa = tiedosto[:-1*len(paate)-1]
		return(alkuosa, paate)
	return(tiedosto, "")


def joinittuonko(*lista):
	'''
	Liittää argumenttistringit toisiinsa ja tarkistaa onko lopputulos olemassaoleva kansio.
	Aika tosi usein tarvitsee rakennetta os.path.exists(os.path.join(a,b,c)) eikä
	sitä jaksaisi jok'ikinen kerta naputella uusiksi...
	'''
	joinittu = ""
	for a in lista:
		joinittu = os.path.join(joinittu, a)
	return(os.path.exists(joinittu))


def kansion_sisalto(kansio, tiedostomuodot=[]):
	'''
	Käy kansion läpi ja palauttaa listat
	sen sisältämistä tiedostoista
	sekä alikansioista
	'''
	tiedostot = []
	kansiot = []
	if os.path.exists(kansio):
		asiat = os.listdir(kansio)
		tiedostot = [a for a in asiat if os.path.isfile(os.path.join(kansio,a)) and (not(tiedostomuodot) or paate(a)[1].lower() in tiedostomuodot)]
		kansiot = [a for a in asiat if os.path.isdir(os.path.join(kansio,a))]
	return(tiedostot,kansiot)


def hanki_kansion_tiedostolista(kansio, tiedostomuodot=[], KIELLETYT=kvak.KIELLETYT):
	'''
	Palauttaa annetun kansion tiedostolistan,
	ts. listan kaikista tiedostoista kansiossa ja sen alikansioista
	täysinä tiedostopolkuina
	'''
	tiedostolista = []
	if os.path.exists(kansio):
		for tiedosto in os.listdir(kansio):
			# Oikeassa tiedostomuodossa oleva tiedosto:
			if os.path.isfile(os.path.join(kansio, tiedosto)) and (not(tiedostomuodot) or paate(tiedosto)[1].lower() in tiedostomuodot):
				# Käy läpi kielletyt sanat
				ban = False
				for sana in KIELLETYT:
					if sana in tiedosto.lower():
						ban = True
						break
				if not ban:
					tiedostolista.append(os.path.join(kansio, tiedosto))
			# Kansio:
			elif os.path.isdir(os.path.join(kansio, tiedosto)):
				tiedostolista += hanki_kansion_tiedostolista(os.path.join(kansio, tiedosto))
	return(tiedostolista)


def kay_kansio_lapi(source_path, dest_path, level):
	'''
	Käy läpi kansiot 'source_path' ja 'dest_path', ja katsoo mitkä
	source_pathista löytyvät tiedostot ja kansiot puuttuvat dest_pathista.
	Eli ei, tämä ei osaa katsoa, onko tiedostoja tai kansiota uudelleennimetty
	tai siirrelty kansion sisällä toisiin alikansioihin.
	Käy rekursiivisesti läpi myös yhteiset alikansiot.
	'''

	kopioituja = 0
	kopioarvo = 0
	if os.path.exists(source_path) and os.path.exists(dest_path):
		try:
			source_objects = os.listdir(source_path) # Noutokansion tiedostot ja alikansiot, nettikatkeamisvaralla
		except OSError:
			return(-1)
		dest_objects = os.listdir(dest_path) # Kohdekansion tiedostot ja alikansiot

		prlen = max(5, 69 - 15*level)
		i = 0
		j = prlen
		while j < len(str(os.path.basename(source_path))):
			#print("{:s}{:s}".format("\t"*level, str(os.path.basename(source_path))[i:j]))
			i = j
			j += prlen
		#print("{:s}{:s}".format("\t"*level, str(os.path.basename(source_path))[i:]))
		print("{:s}".format(str(os.path.basename(source_path))))
		#print("{:s}|\n{:s}|".format("\t"*(level+1), "\t"*(level+1)))

		# Käydään läpi noutokansion tiedostot ja alikansiot
		for object in source_objects:
			# Kansio joka on molemmissa: käy läpi ja katso löytyykö kaikki tiedostot (ja rekursiivisesti alikansiot
			if os.path.isdir(os.path.join(source_path, object)) and object in dest_objects:
				kopioarvo = kay_kansio_lapi(os.path.join(source_path, object), os.path.join(dest_path, object), level+1)
				if kopioarvo >= 0:
					kopioituja += kopioarvo
				elif not kopioituja:
					kopioituja = -1
					break

			# Kansio tai tiedosto joka ei ole kohdekansiossa: kopsaa kohdekansioon
			elif object not in dest_objects:
				# Puuttuva kansio
				if os.path.isdir(os.path.join(source_path, object)):
					print("\nKopioi kansio: {:s}\n".format(os.path.join(source_path, object)))
					shutil.copytree(os.path.join(source_path, object), os.path.join(dest_path, object))
					kopioituja += 1
				# Puuttuva tiedosto
				elif os.path.isfile(os.path.join(source_path, object)):
					print("\nKopioi tiedosto: {:s}\n".format(os.path.join(source_path, object)))
					shutil.copy2(os.path.join(source_path, object), os.path.join(dest_path, object))
					kopioituja += 1
	else:
		print("Huono polku:\n{:s}\n{:s}".format("[{:s}] Source: {:s}".format(str(os.path.exists(source_path)), source_path), "[{:s}] Dest: {:s}".format(str(os.path.exists(dest_path)), dest_path)))
	return(kopioituja)


def luo_tiedostolista(kansio):
	tiedostopolkulista = []
	for tiedosto in os.listdir(kansio):
		if os.path.isfile(os.path.join(kansio, tiedosto)):
			tiedostopolkulista.append(os.path.join(kansio,tiedosto))
		else:
			tiedostopolkulista += luo_tiedostolista(os.path.join(kansio, tiedosto))
	return(tiedostopolkulista)
