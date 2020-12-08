'''
Musatietokannan vakiot kootussa paikkaa.
Sallitut tiedostotyypit, kielletyt sanat (?),
relevanttien kansioiden sijainnit eri tietokoneilla.
'''
import os

MUSATIEDOSTOT = ["mp3", "flac", "wma"]
KIELLETYT = []
BUFFERI			= 65536 # tiedostoja RAM:iin 64kb paloissa
MERKKIBUFFERI	= 4000	# jsoneita RAM:iin 4000 merkin paloissa

# Tunnista käytettävä kone kotikansion perusteella.
LOKAALI_KONE = None
ETAPALVELIN = "pettankone" # etäpalvelimen nimi (as in, 'ssh ETAPALVELIN' päästää suoraan sisään)
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

# Musiikkien sijainnit
MUSAKANSIOT = {
			  None:		    [],
			  "Murakumo":   ["/mnt/Suzuya/Suzuyajako/Musiikki/Aikatsu/"],
			  "pettankone": ["/mnt/data/Jouni/Musiikki/",
			                 "/mnt/data/Nipa/Musiikki/",
			                 "/mnt/data/Tursa/Musiikki/",],
			  "Olkkari":    ["/mnt/Data/Jouni/Musiikki/"],
			  }
# Tietokantatiedostojen sijainnit eri koneilla,
# voidaan käyttää tietokannan scp:ttämiseen paikalliselle koneelle
TIETOKANTATIEDOSTOT = {
			  		  None:		   [],
					  "Murakumo":  ["/home/pilperi/Tietokannat/Musiikit/musiikit.tietokanta"],
					  # "Murakumo":  ["/home/pilperi/Tietokannat/Musiikit/aikatsu_musiikit.tietokanta"],
					  "pettankone":["/home/taira/tietokannat/Musakirjasto/jounimusat.tietokanta",
					  			    "/home/taira/tietokannat/Musakirjasto/nipamusat.tietokanta",
					  			    "/home/taira/tietokannat/Musakirjasto/tursamusat.tietokanta"
					  			   ],
					  "olkkari":   ["/home/olkkari/Tietokannat/Musiikit/musiikit.tietokanta"]
					  }

# Temppikansion sijainnit:
BIISIKANSIOT = {
			  "Murakumo": "Biisit",
			  }
BIISIKANSIO = BIISIKANSIOT.get(LOKAALI_KONE)
if BIISIKANSIO is None:
	BIISIKANSIO = "Biisit"
if not os.path.exists(BIISIKANSIO):
	os.mkdir(BIISIKANSIO)

LOKAALIT_MUSIIKIT    = MUSAKANSIOT.get(LOKAALI_KONE)
LOKAALIT_TIETOKANNAT = TIETOKANTATIEDOSTOT.get(LOKAALI_KONE)
if type(LOKAALIT_TIETOKANNAT) is not list:
	LOKAALIT_TIETOKANNAT = []

# Etäpalvelimen tietokantatiedosto(t)
ETAPALVELIN_TIETOKANNAT = TIETOKANTATIEDOSTOT.get(ETAPALVELIN)
if type(ETAPALVELIN_TIETOKANNAT) is not list:
	ETAPALVELIN_TIETOKANNAT = []

# Jos pituuksissa hämminkiä, täytä nulleilla (ei kyl saisi olla) (???)
if all(type(a) is list for a in [LOKAALIT_MUSIIKIT, LOKAALIT_MUSIIKIT]) and len(LOKAALIT_MUSIIKIT) != len(LOKAALIT_MUSIIKIT):
	while len(LOKAALIT_MUSIIKIT) < len(LOKAALIT_TIETOKANNAT):
		LOKAALIT_MUSIIKIT.append(None)
	while len(LOKAALIT_MUSIIKIT) > len(LOKAALIT_TIETOKANNAT):
		LOKAALIT_TIETOKANNAT.append(None)
