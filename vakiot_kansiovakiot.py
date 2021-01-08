'''
Musatietokannan vakiot kootussa paikkaa.
Sallitut tiedostotyypit, kielletyt sanat (?),
relevanttien kansioiden sijainnit eri tietokoneilla.
'''
import os
import sys
import json
import configparser

VERBOOSI = "-v" in sys.argv or "--verbose" in sys.argv # ei turhaa printtailua

BUFFERI         = 65536 # tiedostoja RAM:iin 64kb paloissa
MERKKIBUFFERI   = 4000	# jsoneita RAM:iin 4000 merkin paloissa

# TBD
LOKAALIT_MUSIIKIT = []
MUSATIEDOSTOT = []
KIELLETYT = ""
ETAPALVELIN = ""
LOKAALIT_TIETOKANNAT = ""
ETAPALVELIN_TIETOKANNAT = ""
BIISIKANSIO = ""
VAROITURAJA = 5
SOITIN = ""
KOMENTO_LISAA_KAPPALE_SOITTOLISTAAN = ""
KOMENTO_LISAA_KANSIO_SOITTOLISTAAN  = ""

# Tunnista käytettävä kone kotikansion perusteella.
LOKAALI_KONE = None
if os.path.exists("/home/pilperi"):
	LOKAALI_KONE = "Murakumo"
elif os.path.exists("/home/taira"):
	LOKAALI_KONE = "pettankone"
elif os.path.exists("/home/olkkari"):
	LOKAALI_KONE = "olkkari"
if VERBOOSI and LOKAALI_KONE is None:
	print("Käytettävää tietokonetta ei kyetty määrittämään...")
elif VERBOOSI:
	print(f"Lokaali kone: {LOKAALI_KONE}")

# Luetaan asetukset INI-tiedostosta, jos sellainen löytyy.
config = configparser.ConfigParser(default_section="Pettankone")
if os.path.exists("./asetukset.ini"):
	if VERBOOSI:
		print("Luetaan asetukset .ini-tiedostosta")
	config.read("./asetukset.ini")
# Luetaan määrittelyt configista
# Mitään ei ole määritelty: laitetaan Pettan
if not [a for a in config.keys() if a != "DEFAULT"]:
	ASETUSKOKOONPANO = "Pettankone"
	if VERBOOSI:
		print(f"Tyhjä asetustiedosto, käytetään arvoja {ASETUSKOKOONPANO}")
	config[ASETUSKOKOONPANO] = {}
# Muutoin otetaan eka avain
else:
	ASETUSKOKOONPANO = list(config.keys())[0]
	if VERBOOSI:
		print(f"Käytetään arvoja {ASETUSKOKOONPANO}")

def tarkasta_config():
	'''
	Tarkastetaan että käytössä oleva asetuskokoonpano
	on järkevästi määritelty. Jos jokin asia on hölmösti,
	laitetaan oletusarvo (pettankoneen arvot, audacious)
	'''
	global ASETUSKOKOONPANO
	global config
	if VERBOOSI:
		print(f"Asetuskokoonpano {ASETUSKOKOONPANO}")
	# Tarkistetaan että kokoonpano ylipäätään on configissa
	if ASETUSKOKOONPANO not in config.keys():
		config[ASETUSKOKOONPANO] = {}
	# Tarkistetaan että tarvittavat asiat löytyy initiedostosta. Jos ei, laitetaan oletukset mukaan.
	# Musakansio uupuu
	if "musakansiot" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Musakansion sijaintia ei määritelty, laitetaan tilapäisarvo")
		config.set(ASETUSKOKOONPANO, "musakansiot", "[\"/polku/kansioon\"]")
	# Sallitut tiedostomuodot uupuu
	if "sallitut tiedostomuodot" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Sallittuja tiedostomuotoja ei määritelty, asetetaan oletusarvot")
		config.set(ASETUSKOKOONPANO, "sallitut tiedostomuodot", "[\"mp3\", \"flac\", \"wma\", \"ogg\"]")
	# Kielletyt tiedostomuodot uupuu (tätä ei oikeestaan tarttis)
	if "kielletyt tiedostomuodot" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Kiellettyjä tiedostomuotoja ei määritelty, asetetaan oletusarvot muodon vuoksi")
		config.set(ASETUSKOKOONPANO, "kielletyt tiedostomuodot", "[]")
	# Etäpalvelin uupuu
	if "etapalvelin" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Etäpalvelinta ei määritelty, laitetaan \'pettankone\'")
		config.set(ASETUSKOKOONPANO, "etapalvelin", "pettankone")
	# Paikalliset tietokannat uupuu
	if "tietokantatiedostot lokaalit" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Paikallisten tietokantojen sijaintia ei määritelty, laitetaan tilapäisarvo")
		config.set(ASETUSKOKOONPANO, "tietokantatiedostot lokaalit", "[\"/tietokantakansio/esimerkki.tietokanta\"]")
	# Etätietokannat uupuu
	if "tietokantatiedostot etakone" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Etäkoneen tietokantasijainteja ei määritelty, laitetaan pettanin")
		config.set(ASETUSKOKOONPANO, "tietokantatiedostot etakone", json.dumps(["/home/taira/tietokannat/Musakirjasto/jounimusat.tietokanta",\
	                                 "/home/taira/tietokannat/Musakirjasto/nipamusat.tietokanta",\
	                                 "/home/taira/tietokannat/Musakirjasto/tursamusat.tietokanta"], indent=4))
	# Latauskansio uupuu
	if "latauskansio" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Latausten kohdekansiota ei määritelty, laitetaan \'./Biisit\'")
		config.set(ASETUSKOKOONPANO, "latauskansio", "./Biisit")
	# Latausmäärän varoitusrajaa ei asetettu
	if "raja latausvaroitus" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Varoitusrajaa monen tiedoston lataamiselle ei määritelty, laitetaan 5")
		config.set(ASETUSKOKOONPANO, "raja latausvaroitus", "5")
	# Soitinohjelmaa ei määritelty
	if "soitin" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Soitinohjelmaa ei määritelty, laitetaan \'audacious\'")
		config.set(ASETUSKOKOONPANO, "soitin", "audacious")
	# Listalle lisäämisen komentoa ei määritelty
	if "lisayskomento kappale" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Soitinohjelman listaanlisäyskomentoa ei määritelty, laitetaan audaciouksen \'-e\'")
		config.set(ASETUSKOKOONPANO, "lisayskomento kappale", "-e")
	# Listalle lisäämisen komentoa ei määritelty
	if "lisayskomento kansio" not in config[ASETUSKOKOONPANO]:
		if VERBOOSI:
			print("Soitinohjelman komentoa, jolla lisätään kokonainen kansio listaan, ei ole määritelty, laitetaan \'--enqueue\'")
		config.set(ASETUSKOKOONPANO, "lisayskomento kansio", "--enqueue")

def vaihda_vakiot():
	'''
	Asettaa globaalit vakiot asetuskokoonpanon mukaisiksi.
	'''
	# Asetusmäärittelyt
	global ASETUSKOKOONPANO
	global config
	global VERBOOSI

	# Itse asetukset
	global LOKAALIT_MUSIIKIT
	global MUSATIEDOSTOT
	global KIELLETYT
	global ETAPALVELIN
	global LOKAALIT_TIETOKANNAT
	global ETAPALVELIN_TIETOKANNAT
	global BIISIKANSIO
	global VAROITURAJA
	global SOITIN
	global KOMENTO_LISAA_KAPPALE_SOITTOLISTAAN
	global KOMENTO_LISAA_KANSIO_SOITTOLISTAAN
	# Asetetaan vakioihin, jos asetuskokoonpano määritelty
	if ASETUSKOKOONPANO in config:
		if VERBOOSI:
			print("Asetetaan vakiot")
		# Kansiorakenteet
		LOKAALIT_MUSIIKIT                   = json.loads(config.get(ASETUSKOKOONPANO,"musakansiot"))
		MUSATIEDOSTOT                       = json.loads(config.get(ASETUSKOKOONPANO,"sallitut tiedostomuodot"))
		KIELLETYT                           = json.loads(config.get(ASETUSKOKOONPANO,"kielletyt tiedostomuodot"))
		ETAPALVELIN                         = config.get(ASETUSKOKOONPANO,"etapalvelin")
		LOKAALIT_TIETOKANNAT                = json.loads(config.get(ASETUSKOKOONPANO,"tietokantatiedostot lokaalit"))
		ETAPALVELIN_TIETOKANNAT             = json.loads(config.get(ASETUSKOKOONPANO,"tietokantatiedostot etakone"))
		BIISIKANSIO                         = config.get(ASETUSKOKOONPANO,"latauskansio")
		# Komennot
		VAROITURAJA                         = config.getint(ASETUSKOKOONPANO,"raja latausvaroitus")
		SOITIN                              = config.get(ASETUSKOKOONPANO,"soitin")
		KOMENTO_LISAA_KAPPALE_SOITTOLISTAAN = SOITIN + " " + config.get(ASETUSKOKOONPANO,"lisayskomento kappale")
		KOMENTO_LISAA_KANSIO_SOITTOLISTAAN  = SOITIN + " " + config.get(ASETUSKOKOONPANO,"lisayskomento kansio")
	# Tällaisia asetuksia ei ole, mistä moiset keksit?
	elif VERBOOSI:
		print("Asetuskokoonpanoa {ASETUSKOKOONPANO} ei ole määritelty.")

def tallenna_asetukset():
	'''
	Tallentaa asetukset tiedostoon.
	'''
	global config
	with open('./asetukset.ini', 'w+') as configfile:
		if VERBOOSI:
			print("Tallennetaan asetukset tiedostoon")
			for key in config.keys():
				print(key)
				for asetus in config[key]:
					print(f"  {asetus} = {config[key][asetus]}")
		config.write(configfile)
		if VERBOOSI:
			print("Tallennettu.")

# Tarkasta asetukset
tarkasta_config()
vaihda_vakiot()
# Jos latauskansiota ei ole, yritetään tehdä se
if not os.path.exists(BIISIKANSIO):
	if VERBOOSI:
		print(f"Latauskansiota {BIISIKANSIO} ei ole, tehdään")
	os.mkdir(BIISIKANSIO)
# Tallenna
tallenna_asetukset()

def vaihda_asetuskokoonpanoa(nimi):
	'''
	Vaihda vakiokanta eri asetuskokoonpanoon,
	nimen perusteella kutsuen.
	'''
	global config
	global VERBOOSI
	global ASETUSKOKOONPANO

	if nimi in config:
		if VERBOOSI:
			print(f"Vaihdetaan asetuskokoonpanoa: {ASETUSKOKOONPANO} -> {nimi}")
		ASETUSKOKOONPANO = nimi
		vaihda_vakiot()
		if VERBOOSI:
			print("Asetettu")
		tarkasta_config()

def muokkaa_asetusta(asetus, arvo):
	'''
	Muokkaa yksittäisen asetuksen arvoa.
	'''
	if ASETUSKOKOONPANO in config and asetus in config:
		if kaypa(asetus, arvo):
			config[ASETUSKOKOONPANO][asetus] = arvo
			if VERBOOSI:
				print(f"Arvo \"{arvo}\" asetettu kenttään \"{asetus}\"")
		elif VERBOOSI:
			print(f"Arvo \"{arvo}\" ei ole käypä arvo asetukselle \"{asetus}\"")
	elif VERBOOSI:
		print(f"Asetusta \"{asetus}\" ei ole määritelty.")

def paivita_asetukset():
	'''
	Lue INI-tiedosto uusiksi.
	'''
	global config
	# Luetaan asetukset INI-tiedostosta, jos sellainen löytyy.
	config = configparser.ConfigParser(default_section="Pettankone")
	if os.path.exists("./asetukset.ini"):
		if VERBOOSI:
			print("Luetaan asetukset .ini-tiedostosta")
		config.read("./asetukset.ini")
	# Luetaan määrittelyt configista
	# Mitään ei ole määritelty: laitetaan Pettan
	if not [a for a in config.keys() if a != "DEFAULT"]:
		ASETUSKOKOONPANO = "Pettankone"
		if VERBOOSI:
			print(f"Tyhjä asetustiedosto, käytetään arvoja {ASETUSKOKOONPANO}")
		config[ASETUSKOKOONPANO] = {}
	# Muutoin otetaan eka avain
	else:
		ASETUSKOKOONPANO = list(config.keys())[0]
		if VERBOOSI:
			print(f"Käytetään arvoja {ASETUSKOKOONPANO}")
	tarkasta_config()
	vaihda_vakiot()
	tallenna_asetukset()
	# Jos latauskansio on kadonnut jonnekin, tehdään uusiksi
	if not os.path.exists(BIISIKANSIO):
		if VERBOOSI:
			print(f"Latauskansio {BIISIKANSIO} oli kadonnut. Älä tee tämmösii.")
		os.mkdir(BIISIKANSIO)
