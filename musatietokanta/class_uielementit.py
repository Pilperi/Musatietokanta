'''
UI-elementit siististi samassa kasassa, poissa tieltä.
Lähinnä taustalla, piilossa pysyvien datatyyppien määritelmiä.
'''
import os

from PyQt5 import Qt, QtCore, QtGui

from tiedostohallinta import funktiot_kansiofunktiot as kfun

OLETUSVARI    = (255,255,255)
ALBUMIVARI    = (155,155,255)
BIISIVARI     = (155,255,155)
KOROSTUSVARI  = (255, 0, 255)
OLETUSFONTTI  = 12
OLETUSBOLDAUS = False
OLETUSARVOT = (OLETUSFONTTI, OLETUSBOLDAUS, OLETUSVARI)

class PuuElementti(Qt.QStandardItem):
    '''
    Pohjaluokka hierarkisten puiden selaamiselle.
    '''
    FONTTIKOKO = OLETUSFONTTI
    BOLDATTU = OLETUSBOLDAUS
    VARI = OLETUSVARI

    def __init__(self, fonttikoko=FONTTIKOKO, boldattu=BOLDATTU, vari=VARI):
        super().__init__()
        fontti = QtGui.QFont("Open Sans", fonttikoko)
        fontti.setBold(boldattu)
        self.setEditable(False)
        self.setForeground(QtGui.QColor(*vari))
        self.setFont(fontti)
        self.setText("")

    def latauslistateksti(self):
        return self.text()

    def __str__(self):
        return ""


class Kansioelementti(PuuElementti):
    '''
    Kansio kansiohierarkiassa.
    Sisältää biisejä ja kansioita.
    '''
    FONTTIKOKO, BOLDATTU, VARI = OLETUSARVOT

    def __init__(self,
        puu,
        fonttikoko=FONTTIKOKO,
        boldattu=BOLDATTU,
        vari=VARI
        ):
        '''Inittifunktio'''
        super().__init__(fonttikoko, boldattu, vari)
        self.setText(str(puu.kansio))
        self.puu = puu

    def __str__(self):
        '''
        Kuvaus kansiosta tietoikkunaan.
        '''
        st  = "Kansio\t{}".format(self.puu.kansio)
        st += "\nSyvyydellä\t{}{}".format(
            self.puu.syvennystaso,
            "    (juuri)"*(self.puu.syvennystaso==0)
            )
        lukumaara = self.puu.sisallon_maara()
        st += "\nBiisejä\t{}    ({} + {})".format(
            lukumaara[0], lukumaara[1], lukumaara[2]
            )
        st += "\nKansioita\t{}".format(len(self.puu.alikansiot))
        return st


class Tiedostoelementti(PuuElementti):
    FONTTIKOKO = 10
    BOLDATTU = OLETUSBOLDAUS
    VARI = OLETUSVARI

    def __init__(self,
        tiedosto,
        fonttikoko=FONTTIKOKO,
        boldattu=BOLDATTU,
        vari=VARI
        ):
        '''Inittifunktio'''
        super().__init__(fonttikoko, boldattu, vari)
        self.setText(str(tiedosto.tiedostonimi))
        self.tiedosto = tiedosto

    def __str__(self):
        '''
        Näytä biisin tiedot.
        '''
        st = ""
        st += "{} - {}\n\n\n".format(self.tiedosto.esittaja, self.tiedosto.biisinimi)
        st += "Esittäjä:"
        if self.tiedosto.esittaja:
            st += "\t{}".format(self.tiedosto.esittaja)
        st += "\nKappale:"
        if self.tiedosto.biisinimi:
            st += "\t{}".format(self.tiedosto.biisinimi)
        st += "\nAlbumi:"
        if self.tiedosto.albuminimi:
            st += "\t{}".format(self.tiedosto.albuminimi)
        st += "\nVuosi:"
        if self.tiedosto.vuosi:
            st += "\t{}".format(self.tiedosto.vuosi)
        st += "\nRaita:"
        if self.tiedosto.vuosi:
            st += "\t{}{}".format(self.tiedosto.raita, f"/{self.tiedosto.raitoja}"*(self.tiedosto.raitoja not in [0,None]))
        st += "\nAlb.es.:"
        if self.tiedosto.albumiesittaja:
            st += "\t{}".format(self.tiedosto.albumiesittaja)
        st += "\nLisätty:"
        if self.tiedosto.lisayspaiva:
            pilkottu = self.tiedosto.paivays(self.tiedosto.lisayspaiva)[1]
            st += "\t{:04d}-{:02d}-{:02d} / {:02d}:{:02d}".format(pilkottu[0], pilkottu[1], pilkottu[2], pilkottu[3], pilkottu[4])
        return(st)

    def tiedostopolku(self):
        '''
        Antaa tiedoston polun.
        Vanhempana aina jokin kansio,
        haetaan siitä kansiopolku ja tiedostosta tiedostonimi.
        '''
        vanhempi = self.parent()
        if vanhempi is not None:
            kansiopolku  = vanhempi.puu.hae_nykyinen_polku()
            tiedostonimi = self.tiedosto.tiedostonimi
            return os.path.join(kansiopolku, tiedostonimi)
        return None

class Artistielementti(PuuElementti):
    '''
    Data jaoteltuna artisti -> albumi
    koska nipan tiedostot on ihan miten sattuu.
    '''
    FONTTIKOKO, BOLDATTU, VARI = OLETUSARVOT

    def __init__(self,
        artistipuu,
        artisti,
        fonttikoko=FONTTIKOKO,
        boldattu=BOLDATTU,
        vari=VARI
        ):
        '''Inittifunktio'''
        super().__init__(fonttikoko, boldattu, vari)

        self.setText(str(artisti))
        self.artisti = artisti # str
        self.dikti   = {} # {albuminnimi: [Biisejä]}
        if artistipuu.artistit.get(artisti) is not None:
            self.dikti = artistipuu.artistit.get(artisti)
            # Lisää albumit lapsiksi
            for albumi in artistipuu.artistit[artisti]:
                albumielementti = Albumielementti(artistipuu, artisti, albumi, vari=ALBUMIVARI)
                self.appendRow(albumielementti)

    def __str__(self):
        '''
        Kuvaus kansiosta tietoikkunaan.
        '''
        st  = "Artisti\t{}".format(self.artisti)
        st += "\nAlbumeita\t{}".format(len(self.dikti.keys()))
        lukumaara = 0
        for albumi in self.dikti:
            lukumaara += len(self.dikti[albumi])
        st += "\nBiisejä\t{}".format(lukumaara)
        return st

class Albumielementti(PuuElementti):
    '''
    Albumi Artistielementin alla.
    '''
    FONTTIKOKO, BOLDATTU, VARI = OLETUSARVOT

    def __init__(self,
        artistipuu,
        artisti,
        albumi,
        fonttikoko=FONTTIKOKO,
        boldattu=BOLDATTU,
        vari=VARI
        ):
        '''Inittifunktio'''
        super().__init__(fonttikoko, boldattu, vari)
        self.setText(str(albumi))
        self.artisti = artisti
        self.albumi  = albumi  # str
        self.biisit  = []      # lista (Tiedostopuu, Biisi) tupleja
        if artistipuu.artistit.get(artisti) is not None and artistipuu.artistit[artisti].get(albumi) is not None:
            self.biisit = artistipuu.artistit[artisti][albumi]
            # Lisää raidat lapsiksi
            for raitatuple in artistipuu.artistit[artisti][albumi]:
                boldattu = False
                vari = BIISIVARI
                if raitatuple[1].esittaja is not None and raitatuple[1].esittaja == artisti:
                    boldattu = True
                    vari = KOROSTUSVARI
                raita = Raitaelementti(raitatuple, boldattu=boldattu, vari=vari)
                self.appendRow(raita)

    def __str__(self):
        '''
        Kuvaus kansiosta tietoikkunaan.
        '''
        st  = "Albumi\t{} - {}".format(self.artisti, self.albumi)
        st += "\nBiisejä\t{}".format(len(self.biisit))
        return st

class Raitaelementti(PuuElementti):
    '''
    Raita albumilla.
    '''
    FONTTIKOKO = 10
    BOLDATTU = OLETUSBOLDAUS
    VARI = OLETUSVARI

    def __init__(self,
        tiedostotuple,
        fonttikoko=FONTTIKOKO,
        boldattu=BOLDATTU,
        vari=VARI):
        super().__init__(fonttikoko, boldattu, vari)

        if None not in (tiedostotuple[1].esittaja, tiedostotuple[1].biisinimi):
            puuteksti = f"{tiedostotuple[1].esittaja} - {tiedostotuple[1].biisinimi}"
        else:
            puuteksti = str(tiedostotuple[1].tiedostonimi)

        self.setText(puuteksti)
        self.tiedostotuple = tiedostotuple

    def __str__(self):
        '''
        Näytä biisin tiedot.
        '''
        st = ""
        st += "{} - {}\n\n\n".format(self.tiedostotuple[1].esittaja, self.tiedostotuple[1].biisinimi)
        st += "Esittäjä:"
        if self.tiedostotuple[1].esittaja:
            st += "\t{}".format(self.tiedostotuple[1].esittaja)
        st += "\nKappale:"
        if self.tiedostotuple[1].biisinimi:
            st += "\t{}".format(self.tiedostotuple[1].biisinimi)
        st += "\nAlbumi:"
        if self.tiedostotuple[1].albuminimi:
            st += "\t{}".format(self.tiedostotuple[1].albuminimi)
        st += "\nVuosi:"
        if self.tiedostotuple[1].vuosi:
            st += "\t{}".format(self.tiedostotuple[1].vuosi)
        st += "\nRaita:"
        if self.tiedostotuple[1].vuosi:
            st += "\t{}{}".format(self.tiedostotuple[1].raita, f"/{self.tiedostotuple[1].raitoja}"*(self.tiedostotuple[1].raitoja not in [0,None]))
        st += "\nAlb.es.:"
        if self.tiedostotuple[1].albumiesittaja:
            st += "\t{}".format(self.tiedostotuple[1].albumiesittaja)
        st += "\nLisätty:"
        if self.tiedostotuple[1].lisayspaiva:
            pilkottu = self.tiedostotuple[1].paivays(self.tiedostotuple[1].lisayspaiva)[1]
            st += "\t{:04d}-{:02d}-{:02d} / {:02d}:{:02d}".format(pilkottu[0], pilkottu[1], pilkottu[2], pilkottu[3], pilkottu[4])
        return(st)

    def tiedostopolku(self):
        '''
        Antaa tiedoston polun.
        Vanhempana aina jokin kansio,
        haetaan siitä kansiopolku ja tiedostosta tiedostonimi.
        '''
        kansiopolku  = self.tiedostotuple[0].hae_nykyinen_polku()
        tiedostonimi = self.tiedostotuple[1].tiedostonimi
        return os.path.join(kansiopolku, tiedostonimi)
