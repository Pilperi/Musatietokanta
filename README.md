Tietokantajärjestelmä ja soitin biisien kuunteluun etänä.

Monasti on ollut erinäisiä ongelmia, kun biisejä on soiteltu ns. tien päällä sshfs:n yli.
Milloin yhteys katkeaa ja koko kansioselain menee ihan täysin juntturaan, milloin siirtonopeus ei riitä FLAC:ien pyörittämiseen, milloin hakutoiminto kaataa kaiken... Monen moista.
Tämän vuoksi olisi varmaan varmempaa jos olisi softa, jolla yksi tietokantatiedosto johon kirjattu missä etäkoneen biisit sijaitsevat (sikäläisessä järjestelmässä), ja scp:ttäisi ne mitä tarvitaan paikalliseen väliaikaiskansioon.

Tää alkaa olla jo suht koht käyttökunnossa, joten käyttöohjeet lienee paikallaan:

- Riippuvuudet on aika kevyet, ks. `setup.py` jos kinostaa.

- Setit saa asennettua `pip`illä kun laittaa siihen että `pip install git+https://github.com/Pilperi/Musatietokanta`

- Tämän jälkeen sitä voi kutsua pakettina. Käytön kannalta kinostavin tapa on flow
  ```python
  from musatietokanta import main
  main.main()
  ```
  jonka seurauksena se ajaa perusprosessit suhtkoht tuttuun tapaan ja avaa ohjausikkunan. Voit vaikka kirjoittaa skriptitiedostoon ja laittaa sen kutsumiselle jonkun kivan aliaksen.

- Perusflow on se, että ohjelma lataa etäpalvelimelta tietokannat siitä, mitä biisejä siellä sijaitsee missäkin ja rakentaa niistä simuloidun kansiopuun. Sieltä sitten etsitään kappale, albumi tai kansio jonka haluaa ladata ja `Lataa`-nappia painamalla ohjelma kiskoo sen etäpalvelimelta paikalliselle koneelle ja lisää sitten määritellyn soitinohjelman soittolistalle. Latausjono mukaanlukien meneillään olevat lataus näkyy latausnapin alapuolella ja biisin/kansion/minkälie tiedot yläpuolella. Jonosta saa poistettua asioita oikealla klikkaamalla ja niiden järjestystä saa muutettua.

- Hakutoiminto on ns. "vapaahaku", eli se etsii annetulla tekstillä tiedostopoluista, metadatan esittäjä-, kappaleennimi- ja albuminnimitiedoista. Oletuksena hakusanat on eroteltu välilyönneillä, täsmäilmauksen saa kun laittaa sanat hipsujen väliin.

- Käytettävää etäpalvelinta (tai muuten vaan asetuskokoonpanoa) voi vaihtaa lennosta ylärivin vasemmanpuolimmaisesta pudotusvalikosta. Laitan sen listapäivitystoiminnon joskus myöhemmin.

- Asetukset on tiedostossa `~/.Musatietokanta/asetukset.ini`, laitan ohjelman kirjoittamaan esimerkkiyksilön Joskus Myöhemmin.
  - Kenttinä tulee olla (kannattaa käyttää täysiä polkuja tiedostopoluissa)
	  - `[Asetuskokoonpanon nimi]`: Näiden välillä voi vaihdella, läh. lennosta vaihtaa palvelinta
		- `etapalvelin`: Etäpalvelimen nimi tai ip, esim. http://12.34.123.45:5000/
		- `tyyppi`: http. Ajatuksena oli pitää messissä rinnalla ssh, mutta se odottaa implementointia.
		- `latauskansio`: Kun biisejä ladataan, minne ne sijoitetaan. Mieluiten täyspitkä polku.
		- `raja latausvaroitus`: Jos on lataamassa kovin montaa kappaletta kerralla, ohjelma varoittaa. Ei vielä implementoitu joten ihassama.
		- `lisayskomento`: Komento, jolla musiikinsoitinohjelmaa kutsutaan, ts. "\*komento\* \*biisin tiedostopolku\*" -> lisää kappaleen soittolistalle.
		- `ylikirjoita`: Booleflagi. Jos false, vältetään (monet) tapaukset joissa sama kappale ladataan moneen kertaan.
		- `tietokantojen sijainti`: Minne palvelimelta ladatut tietokannat tallennetaan (ei tarvii moneen kertaan ladata).
