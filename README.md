Tietokantajärjestelmä ja soitin biisien kuunteluun etänä.

Monasti on ollut erinäisiä ongelmia, kun biisejä on soiteltu ns. tien päällä sshfs:n yli.
Milloin yhteys katkeaa ja koko kansioselain menee ihan täysin juntturaan, milloin siirtonopeus ei riitä FLAC:ien pyörittämiseen, milloin hakutoiminto kaataa kaiken... Monen moista.
Tämän vuoksi olisi varmaan varmempaa jos olisi softa, jolla yksi tietokantatiedosto johon kirjattu missä etäkoneen biisit sijaitsevat (sikäläisessä järjestelmässä), ja scp:ttäisi ne mitä tarvitaan paikalliseen väliaikaiskansioon.

	Asioita joita tarvitsee tehdä:
		[/] Luokkien määritelmät
			[x] Haluttujen tietojen määrittely
			[x] Tietojen täyttö tiedostosta
			[x] Tietokantaluokka, joka käärii biisit fiksusti
			[/] Kirjoitus- ja lukufunktiot
			[ ] Hakufunktiot

		[ ] Pythonin kautta pyöritettävä SCP

		[ ] Soitinohjelman kanssa juttelu (komentorivikäskyt, ez)

		[ ] Graafinen käyttöliittymä (Qt)
			[ ] Hakukentät (mitä kaikkea halutaan hakea)
			[ ] Valitun biisin tietojen näyttö (kansikuva?)

