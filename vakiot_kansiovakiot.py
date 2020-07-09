'''
Musatietokannan vakiot kootussa paikkaa.
Sallitut tiedostotyypit, kielletyt sanat (?),
relevanttien kansioiden sijainnit eri tietokoneilla.
'''
import os

MUSATIEDOSTOT = ["mp3", "flac", "wma"]
KIELLETYT = []

# Tunnista käytettävä kone kotikansion perusteella.
LOKAALI_KONE = None
if os.path.exists("/home/pilperi"):
	LOKAALI_KONE = "Murakumo"
elif os.path.exists("/home/taira"):
	LOKAALI_KONE = "Pettan"
elif os.path.exists("/home/olkkari"):
	LOKAALI_KONE = "Olkkari"

if LOKAALI_KONE is None:
	print("Käytettävää tietokonetta ei kyetty määrittämään...")
else:
	print(f"Lokaali kone: {LOKAALI_KONE}")

# Musiikkien sijainnit
MUSAKANSIOT = {
			  None:		  [],
			  "Murakumo": ["/mnt/Suzuya/Suzuyajako/Musiikki/"],
			  "Pettan":   ["/mnt/data/Jouni/Musiikki/",
			               "/mnt/data/Nipa/Musiikki/",
			               "/mnt/data/Tursa/Musiikki/",],
			  "Olkkari":  ["/mnt/Data/Jouni/Musiikki/"],
			  }
# Sijainteja vastaavien tietokantatiedostojen sijainnit
TIETOKANTATIEDOSTOT = {
			  		  None:		  [],
					  "Murakumo": ["/home/pilperi/Tietokannat/Musiikit/musiikit.tietokanta"],
					  "Pettan":   ["/home/taira/tietokannat/Musakirjasto/jounimusat.tietokanta",
					  			   "/home/taira/tietokannat/Musakirjasto/nipamusat.tietokanta",
					  			   "/home/taira/tietokannat/Musakirjasto/tursamusat.tietokanta"
					  			  ],
					  "Olkkari":  ["/home/olkkari/Tietokannat/Musiikit/musiikit.tietokanta"]
					  }
LOKAALIT_MUSIIKIT    = MUSAKANSIOT.get(LOKAALI_KONE)
LOKAALIT_TIETOKANNAT = TIETOKANTATIEDOSTOT.get(LOKAALI_KONE)
# Jos pituuksissa hämminkiä, täytä nulleilla (ei kyl saisi olla)
if all(type(a) is list for a in [LOKAALIT_MUSIIKIT, LOKAALIT_MUSIIKIT]) and len(LOKAALIT_MUSIIKIT) != len(LOKAALIT_MUSIIKIT):
	while len(LOKAALIT_MUSIIKIT) < len(LOKAALIT_TIETOKANNAT):
		LOKAALIT_MUSIIKIT.append(None)
	while len(LOKAALIT_MUSIIKIT) > len(LOKAALIT_TIETOKANNAT):
		LOKAALIT_TIETOKANNAT.append(None)