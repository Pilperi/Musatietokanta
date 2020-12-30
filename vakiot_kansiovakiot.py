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

# Luetaan asetukset INI-tiedostosta
config = configparser.ConfigParser()
# Jos asetustiedostoa ei ole olemassa, tehdään sellainen
if not os.path.exists("./asetukset.ini"):
	print("Asetustiedostoa ei löytynyt, tehdään sellainen.")
	# Tiedostosijainnit sun muut
	config['Kansiorakenteet'] = {}
	config.set("Kansiorakenteet", "musakansiot", "[\"/polku/kansioon\"]")
	config.set("Kansiorakenteet", "sallitut_tiedostomuodot", "[\"mp3\", \"flac\", \"wma\", \"ogg\"]")
	config.set("Kansiorakenteet", "kielletyt_tiedostomuodot", "[]")
	config.set("Kansiorakenteet", "etapalvelin", "pettankone")
	config.set("Kansiorakenteet", "tietokantatiedostot_lokaalit", "[\"/tietokantakansio/esimerkki.tietokanta\"]")
	config.set("Kansiorakenteet", "tietokantatiedostot_etakone", json.dumps(["/home/taira/tietokannat/Musakirjasto/jounimusat.tietokanta",\
                                  "/home/taira/tietokannat/Musakirjasto/nipamusat.tietokanta",\
                                  "/home/taira/tietokannat/Musakirjasto/tursamusat.tietokanta"]))
	config.set("Kansiorakenteet", "latauskansio", "./Biisit")
	# Komennot
	config['Komennot'] = {}
	config.set("Komennot", "soitin", "ls")
	config.set("Komennot", "lisayskomento_kappale", "-l")
	config.set("Komennot", "lisayskomento_kansio", "--help")
	with open('./asetukset.ini', 'w+') as configfile:
		config.write(configfile)
else:
	config.read("./asetukset.ini")
# Asetetaan vakioihin
# [Kansiorakenteet]
LOKAALIT_MUSIIKIT                   = json.loads(config.get("Kansiorakenteet","musakansiot"))
MUSATIEDOSTOT                       = json.loads(config.get("Kansiorakenteet","sallitut_tiedostomuodot"))
KIELLETYT                           = json.loads(config.get("Kansiorakenteet","kielletyt_tiedostomuodot"))
ETAPALVELIN                         = config.get("Kansiorakenteet","etapalvelin")
LOKAALIT_TIETOKANNAT                = json.loads(config.get("Kansiorakenteet","tietokantatiedostot_lokaalit"))
ETAPALVELIN_TIETOKANNAT             = json.loads(config.get("Kansiorakenteet","tietokantatiedostot_etakone"))
BIISIKANSIO                         = config.get("Kansiorakenteet","latauskansio")
# [Komennot]
SOITIN                              = config.get("Komennot","soitin")
KOMENTO_LISAA_KAPPALE_SOITTOLISTAAN = SOITIN + " " + config.get("Komennot","lisayskomento_kappale")
KOMENTO_LISAA_KANSIO_SOITTOLISTAAN  = SOITIN + " " + config.get("Komennot","lisayskomento_kansio")

# Jos latauskansiota ei ole, yritetään tehdä se
if not os.path.exists(BIISIKANSIO):
	print(f"Latauskansiota {BIISIKANSIO} ei ole, tehdään")
	os.mkdir(BIISIKANSIO)
