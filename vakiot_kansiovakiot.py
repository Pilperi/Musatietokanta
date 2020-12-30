'''
Musatietokannan vakiot kootussa paikkaa.
Sallitut tiedostotyypit, kielletyt sanat (?),
relevanttien kansioiden sijainnit eri tietokoneilla.
'''
import os
import json
import configparser

BUFFERI         = 65536 # tiedostoja RAM:iin 64kb paloissa
MERKKIBUFFERI   = 4000	# jsoneita RAM:iin 4000 merkin paloissa

# Tunnista käytettävä kone kotikansion perusteella.
LOKAALI_KONE = None
if os.path.exists("/home/pilperi"):
	LOKAALI_KONE = "Murakumo"
elif os.path.exists("/home/taira"):
	LOKAALI_KONE = "pettankone"
elif os.path.exists("/home/olkkari"):
	LOKAALI_KONE = "olkkari"
if LOKAALI_KONE is None:
	print("Käytettävää tietokonetta ei kyetty määrittämään...")
else:
	print(f"Lokaali kone: {LOKAALI_KONE}")

# Luetaan asetukset INI-tiedostosta, jos sellainen löytyy.
config = configparser.ConfigParser()
if os.path.exists("./asetukset.ini"):
	print("Luetaan asetukset .ini-tiedostosta")
	config.read("./asetukset.ini")
# Tarkistetaan että tarvittavat asiat löytyy initiedostosta. Jos ei, laitetaan oletukset mukaan.
# Tiedostosijainnit sun muut
# Koko osio uupuu
if "Kansiorakenteet" not in config:
	config['Kansiorakenteet'] = {}
# Musakansio uupuu
if "musakansiot" not in config['Kansiorakenteet']:
	print("Musakansion sijaintia ei määritelty, laitetaan tilapäisarvo")
	config.set("Kansiorakenteet", "musakansiot", "[\"/polku/kansioon\"]")
# Sallitut tiedostomuodot uupuu
if "sallitut tiedostomuodot" not in config['Kansiorakenteet']:
	print("Sallittuja tiedostomuotoja ei määritelty, asetetaan oletusarvot")
	config.set("Kansiorakenteet", "sallitut tiedostomuodot", "[\"mp3\", \"flac\", \"wma\", \"ogg\"]")
# Kielletyt tiedostomuodot uupuu (tätä ei oikeestaan tarttis)
if "kielletyt tiedostomuodot" not in config['Kansiorakenteet']:
	print("Kiellettyjä tiedostomuotoja ei määritelty, asetetaan oletusarvot muodon vuoksi")
	config.set("Kansiorakenteet", "kielletyt tiedostomuodot", "[]")
# Etäpalvelin uupuu
if "etapalvelin" not in config['Kansiorakenteet']:
	print("Etäpalvelinta ei määritelty, laitetaan \'pettankone\'")
	config.set("Kansiorakenteet", "etapalvelin", "pettankone")
# Paikalliset tietokannat uupuu
if "tietokantatiedostot lokaalit" not in config['Kansiorakenteet']:
	print("Paikallisten tietokantojen sijaintia ei määritelty, laitetaan tilapäisarvo")
	config.set("Kansiorakenteet", "tietokantatiedostot lokaalit", "[\"/tietokantakansio/esimerkki.tietokanta\"]")
# Etätietokannat uupuu
if "tietokantatiedostot etakone" not in config['Kansiorakenteet']:
	print("Etäkoneen tietokantasijainteja ei määritelty, laitetaan pettanin")
	config.set("Kansiorakenteet", "tietokantatiedostot etakone", json.dumps(["/home/taira/tietokannat/Musakirjasto/jounimusat.tietokanta",\
                              "/home/taira/tietokannat/Musakirjasto/nipamusat.tietokanta",\
                              "/home/taira/tietokannat/Musakirjasto/tursamusat.tietokanta"], indent=4))
# Latauskansio uupuu
if "latauskansio" not in config['Kansiorakenteet']:
	print("Latausten kohdekansiota ei määritelty, laitetaan \'./Biisit\'")
	config.set("Kansiorakenteet", "latauskansio", "./Biisit")

# Komennot
if "Komennot" not in config:
	config["Komennot"] = {}
# Latausmäärän varoitusrajaa ei asetettu
if "raja latausvaroitus" not in config["Komennot"]:
	print("Varoitusrajaa monen tiedoston lataamiselle ei määritelty, laitetaan 5")
	config.set("Komennot", "raja latausvaroitus", "5")
# Soitinohjelmaa ei määritelty
if "soitin" not in config["Komennot"]:
	print("Soitinohjelmaa ei määritelty, laitetaan \'ls\' (as in, näytä vain tiedot komentorivillä)")
	config.set("Komennot", "soitin", "ls")
# Listalle lisäämisen komentoa ei määritelty
if "lisayskomento kappale" not in config["Komennot"]:
	print("Soitinohjelman listaanlisäyskomentoa ei määritelty, laitetaan \'-l\' (as in, näytä tiedoston tiedot)")
	config.set("Komennot", "lisayskomento kappale", "-l")
# Listalle lisäämisen komentoa ei määritelty
if "lisayskomento kansio" not in config["Komennot"]:
	print("Soitinohjelman komentoa, jolla lisätään kokonainen kansio listaan, ei ole määritelty, laitetaan \'--size\' (as in, näytä tiedoston koko)")
	config.set("Komennot", "lisayskomento kansio", "--human-readable")

# Kirjoitetaan (takaisin) tiedostoon
with open('./asetukset.ini', 'w+') as configfile:
	print("Tallennetaan asetukset tiedostoon")
	config.write(configfile)

# Asetetaan vakioihin
# [Kansiorakenteet]
LOKAALIT_MUSIIKIT                   = json.loads(config.get("Kansiorakenteet","musakansiot"))
MUSATIEDOSTOT                       = json.loads(config.get("Kansiorakenteet","sallitut tiedostomuodot"))
KIELLETYT                           = json.loads(config.get("Kansiorakenteet","kielletyt tiedostomuodot"))
ETAPALVELIN                         = config.get("Kansiorakenteet","etapalvelin")
LOKAALIT_TIETOKANNAT                = json.loads(config.get("Kansiorakenteet","tietokantatiedostot lokaalit"))
ETAPALVELIN_TIETOKANNAT             = json.loads(config.get("Kansiorakenteet","tietokantatiedostot etakone"))
BIISIKANSIO                         = config.get("Kansiorakenteet","latauskansio")
# [Komennot]
VAROITURAJA                         = config.getint("Komennot","raja latausvaroitus")
SOITIN                              = config.get("Komennot","soitin")
KOMENTO_LISAA_KAPPALE_SOITTOLISTAAN = SOITIN + " " + config.get("Komennot","lisayskomento kappale")
KOMENTO_LISAA_KANSIO_SOITTOLISTAAN  = SOITIN + " " + config.get("Komennot","lisayskomento kansio")

# Jos latauskansiota ei ole, yritetään tehdä se
if not os.path.exists(BIISIKANSIO):
	print(f"Latauskansiota {BIISIKANSIO} ei ole, tehdään")
	os.mkdir(BIISIKANSIO)
