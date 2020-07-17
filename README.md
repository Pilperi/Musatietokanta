Tietokantajärjestelmä ja soitin biisien kuunteluun etänä.

Monasti on ollut erinäisiä ongelmia, kun biisejä on soiteltu ns. tien päällä sshfs:n yli.
Milloin yhteys katkeaa ja koko kansioselain menee ihan täysin juntturaan, milloin siirtonopeus ei riitä FLAC:ien pyörittämiseen, milloin hakutoiminto kaataa kaiken... Monen moista.
Tämän vuoksi olisi varmaan varmempaa jos olisi softa, jolla yksi tietokantatiedosto johon kirjattu missä etäkoneen biisit sijaitsevat (sikäläisessä järjestelmässä), ja scp:ttäisi ne mitä tarvitaan paikalliseen väliaikaiskansioon.

	Asioita joita tarvitsee tehdä:
		[x] Luokkien määritelmät
			[x] Haluttujen tietojen määrittely
			[x] Tietojen täyttö tiedostosta
			[x] Tietokantaluokka, joka käärii biisit fiksusti
			[x] Kirjoitus- ja lukufunktiot
			[x] Hakufunktiot (RAM, ei suoraan tiedostosta)

		[/] Pythonin kautta pyöritettävä SCP

		[ ] Soitinohjelman kanssa juttelu (komentorivikäskyt, ez)

		[ ] Graafinen käyttöliittymä (Qt)
			[ ] Hakukentät (mitä kaikkea halutaan hakea, ks. Hakukriteerit)
				[ ] Biisin nimi
				[ ] Artistin nimi
				[ ] Tiedostopolun osa
				[ ] Raitanumero (tarviiko?)
				[ ] Vapaahaku (kopsaa vaan saman stringin kaikkiin)
				[ ] Hakusanojen ja/tai-toggle
			[ ] Valitun biisin tietojen näyttö (ei varmaan kansikuvaa)
