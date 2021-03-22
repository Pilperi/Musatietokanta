Tietokantajärjestelmä ja soitin biisien kuunteluun etänä.

Monasti on ollut erinäisiä ongelmia, kun biisejä on soiteltu ns. tien päällä sshfs:n yli.
Milloin yhteys katkeaa ja koko kansioselain menee ihan täysin juntturaan, milloin siirtonopeus ei riitä FLAC:ien pyörittämiseen, milloin hakutoiminto kaataa kaiken... Monen moista.
Tämän vuoksi olisi varmaan varmempaa jos olisi softa, jolla yksi tietokantatiedosto johon kirjattu missä etäkoneen biisit sijaitsevat (sikäläisessä järjestelmässä), ja scp:ttäisi ne mitä tarvitaan paikalliseen väliaikaiskansioon.

Tää alkaa olla jo suht koht käyttökunnossa, lähinnä tarvii enää muuntaa paketiksi, joten käyttöohjeet lienee paikallaan:

- Riippuvuudet on aika kevyet (setup.py tulossa myöhemmin):

  - `Python` 3.8.X
	- `mutagen`
	- `PyQt5`

- Kutsuttava tiedosto on (vähemmän yllättäen) `main.py`, käynnistää selausikkunan

- Perusflow on se, että ohjelma lataa etäpalvelimelta tietokannat siitä, mitä biisejä siellä sijaitsee missäkin ja rakentaa niistä simuloidun kansiopuun. Sieltä sitten etsitään kappale, albumi tai kansio jonka haluaa ladata ja `Lataa`-nappia painamalla ohjelma kiskoo sen `scp`:llä etäpalvelimelta paikalliselle koneelle ja lisää sitten määritellyn soitinohjelman soittolistalle. Latausjono mukaanlukien meneillään olevat lataus näkyy latausnapin alapuolella ja biisin/kansion/minkälie tiedot yläpuolella.

- Etäpalvelimella voi olla määriteltynä monta eri tietokantaa, esim. `pettanilla` on meitin, Nipan ja Tursan musakansiot kukin omana tietokantanaan. Näistä voisi joskus muodostaa kaveriksi tietokannan, jossa kaikki samassa. Tietokantojen välillä voi vaihdella oikeanpuolimmaisella pudotusvalikolla, ja sen parina olevasta päivitysnamiskasta se uusiksi-imee tietokantatiedostot etäpalvelimelta.

- Hakutoiminto on ns. "vapaahaku", eli se etsii annetulla tekstillä tiedostopoluista, metadatan esittäjä-, kappaleennimi- ja albuminnimitiedoista. Oletuksena hakusanat on eroteltu välilyönneillä, täsmäilmauksen saa kun laittaa sanat hipsujen väliin.

- Käytettävää etäpalvelinta (tai muuten vaan asetuskokoonpanoa) voi vaihtaa lennosta ylärivin vasemmanpuolimmaisesta pudotusvalikosta. Viereisellä päivitysnamiskalla saa ohjelman huomaamaan asetustiedostoon naputellut muutokset (tai ainakin uudet asetuskokoonpanot).

- Asetukset on tiedostossa `asetukset.ini`, ohjelma luo esimerkkiyksilön jos ei moista löydä
  - Kenttien pitäisi olla aika itsensäselittäviä, kannattanee käyttää täysiä polkuja tiedostopoluissa
	  - `[Asetuskokoonpanon nimi]`: Näiden välillä voi vaihdella, läh. lennosta vaihtaa palvelinta
		- `musakansiot`: lokaalien musien sijainti, tarvii vain jos joskus haluu määrittää omista musista tietokannat (vapaaehtoinen)
		- `sallitut tiedostomuodot`: Mitkä tiedostomuodot on sallittuja jos määrittää omaa tietokantaa (vapaaehtoinen)
		- `kielletyt tiedostomuodot`: Turha (pitäis siivota)
		- `etapalvelin`: Etäpalvelimen nimi tai ip. Oletuksena `pettankone`.
		- `tietokantatiedostot lokaalit`: Minne `musakansioista` väsätyt tietokannat dumpataan (vapaaehtoinen)
		- `tietokantatiedostot etakone`: Missä etäpalvelimen tietokantatiedostot sijaitsee, sieltä kun kiskoo niin tietojen pitäisi olla ajan tasalla. Laittaa oletuksena `pettankoneen` tietokantatiedostojen sijainnit.
		- `latauskansio`: Kun biisejä ladataan, minne ne sijoitetaan. Mieluiten täyspitkä polku, vaikka defaulttaa `./Biisit`
		- `raja latausvaroitus`: Jos on lataamassa kovin montaa kappaletta kerralla, ohjelma varoittaa.
		- `soitin`: K

Asioita joita tarvitsee tehdä:

	[x] Luokkien määritelmät
		[x] Haluttujen tietojen määrittely
		[x] Tietojen täyttö tiedostosta
		[x] Tietokantaluokka, joka käärii biisit fiksusti
		[x] Kirjoitus- ja lukufunktiot
		[x] Hakufunktiot (RAM, ei suoraan tiedostosta)

	[x] Pythonin kautta pyöritettävä SCP (tavallaan)
	  [x] Taustalla lataaminen
		[x] Yksi kerrallaan lataaminen

	[x] Soitinohjelman kanssa juttelu (komentorivikäskyt, ez)

	[x] Graafinen käyttöliittymä (Qt)
		[x] Vapaahaku, kattaa
			- Biisin nimi
			- Artistin nimi
			- Tiedostopolun osa
		[x] Vapaahaku täsmällisellä ilmauksella (hipsujen sisään)
		[x] Valitun biisin tietojen näyttö
		[x] Hallittu Sulkemistoiminto
		[x] Vaihto Kansio/Alikansio- ja Artisti/Albumi-jaotteluiden välillä (hidas)
		[x] Latausjonon näyttö

	[x] Asetukset erilliseen INI-tiedostoon

	[ ] Paketointi
	  [ ] Luokkia tarvii muuallakin (synkka), laita ne omaksi paketiksi kansiofunktioiden ymv kanssa
		[ ] `setup.py` jossa vaatimukset ml. edellämainittu
