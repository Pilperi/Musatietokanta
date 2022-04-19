'''
Musatietokantaselaimen taustatoimijat.
Latausfunktiot ja sen sellaiset, jotka pyörii omissa säikeissään.
'''
import os
import json
import logging

# QApplication, QWidget, QLabel, QGridLayout, QPushButton, QMainWindow
from PyQt5 import QtWidgets
# pyqtSlot, QObject, QThread, pyqtSignal
from PyQt5 import QtCore

from tiedostohallinta import funktiot_kansiofunktiot as kfun
from tiedostohallinta.class_http import Vastaus
from tiedostohallinta.class_tiedostopuu import Tiedostopuu
import tiedostohallinta.funktiot_http_musatietokanta as musapet

from musatietokanta import Palvelintiedot

LOGGER = logging.getLogger(__name__)


class Latain(QtCore.QObject):
    '''
    Pohjaluokka erinäisille lataimille.
    Ne kaikki tarvitsee vähintään osoitteen mistä ladata.

    Perusrakenteena kolmijako eri signaalien välillä:
    signaali_valmis
        Kun toimenpide on valmis, oli lopputulos mikä hyvänsä.
        (läh. tiedetään milloin threadista uskaltaa hypätä ulos)
    signaali_virhe : str
        Jos toimenpide ei onnistu (404 tai ei yhteyttä tai mitä ikinä),
        annetaan virhekuvaus tekstinä.
        Käytännössä Vastaus-luokan virhe-kenttä joka täytetty muualla.
    signaali_vastaus : vaihtelee
        Data mitä piti hakea, milloin missäkin muodossa.
    '''
    signaali_valmis = QtCore.pyqtSignal()
    signaali_virhe = QtCore.pyqtSignal(str)
    signaali_vastaus = QtCore.pyqtSignal()

    def __init__(self, asetukset):
        '''Aseta osoite initissä, koska sitä tarvitaan aina.'''
        super().__init__()
        self._asetukset = None
        self._osoite = ""
        self.osoite = asetukset.osoite

        # Kohdepolku (minne ladataan jos ladataan)
        self._kohdejuuri = "./"
        self._polku_kohde = ""
        self._tarvittava_kansio = None

        # Latausfunktio (millä ladataan)
        self._latausfunktio = self.lataa_http
        self.latausfunktio = asetukset.tyyppi
        self._latausfunktion_nimi = asetukset.tyyppi

    @property
    def osoite(self):
        '''Osoite-getteri'''
        return self._osoite
    @osoite.setter
    def osoite(self, uusiarvo):
        '''Osoite-setteri, aina str'''
        if isinstance(uusiarvo, str):
            self._osoite = uusiarvo
        else:
            errmsg = (
                "Odotettiin str osoitteeksi"
                +f", saatiin {type(uusiarvo)} {uusiarvo}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)

    @property
    def asetukset(self):
        '''Asetus-getteri'''
        return self._asetukset
    @asetukset.setter
    def asetukset(self, uusiarvo):
        '''Asetus-setteri, laita samalla osoite kuntoon'''
        if isinstance(uusiarvo, Palvelintiedot):
            self._asetukset = uusiarvo
            self.osoite = uusiarvo.osoite
        else:
            errmsg = (
                "Odotettiin asetuksiksi Palvelintiedot"
                +f", saatiin {type(uusiarvo)} {uusiarvo}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)

    @property
    def kohdejuuri(self):
        '''Kohdepolun getteri.'''
        return self._kohdejuuri
    @kohdejuuri.setter
    def kohdejuuri(self, uusiarvo):
        '''Kohdejuuren setteri.
        Uuden arvon pitää olla kansio joka on jo olemassa.
        '''
        if isinstance(uusiarvo, str) and os.path.exists(uusiarvo):
            self._kohdejuuri = uusiarvo
        else:
            errmsg = (
                "Odotettiin olemassaolevaa str poluksi"
                +f", saatiin {type(uusiarvo)} {uusiarvo}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)

    @property
    def polku_kohde(self):
        '''Kohdepolun getteri.'''
        return self._polku_kohde
    @polku_kohde.setter
    def polku_kohde(self, uusiarvo):
        '''Kohdepolun setteri.'''
        if isinstance(uusiarvo, str):
            self._polku_kohde = uusiarvo
        else:
            errmsg = (
                "Odotettiin str poluksi"
                +f", saatiin {type(uusiarvo)} {uusiarvo}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)

    @property
    def tarvittava_kansio(self):
        '''Kohdepolun getteri.'''
        return self._tarvittava_kansio
    @tarvittava_kansio.setter
    def tarvittava_kansio(self, uusiarvo):
        '''Kohdejuuren setteri.
        Uuden arvon pitää olla kansio joka on jo olemassa.
        '''
        if isinstance(uusiarvo, (str,type(None))):
            self._tarvittava_kansio = uusiarvo
        else:
            errmsg = (
                "Odotettiin tarvittaviksi alikansioiksi str tai None"
                +f", saatiin {type(uusiarvo)} {uusiarvo}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)

    @property
    def latausfunktio(self):
        '''Latausfunktion getteri.'''
        return self._latausfunktio
    @latausfunktio.setter
    def latausfunktio(self, uusiarvo):
        '''Vaihda lataukseen käytettävää funktiota.'''
        VAIHTOEHDOT = {
            "http": self.lataa_http,
            "ssh": self.lataa_ssh,
            }
        # Nimen perusteella
        if isinstance(uusiarvo, str) and uusiarvo in VAIHTOEHDOT:
            self._latausfunktio = VAIHTOEHDOT[uusiarvo]
            self._latausfunktion_nimi = uusiarvo
            return
        # Valmis funktiopointteri
        for nimi,funktio in VAIHTOEHDOT.items():
            if uusiarvo is funktio:
                self._latausfunktio = uusiarvo
                self._latausfunktion_nimi = nimi
                return
        # Ei käy
        errmsg = (
            f"{uusiarvo} ei ole käypä latausfunktio."
            +" Käypiä vaihtoehtoja ovat {list(VAIHTOEHDOT)}."
            )
        LOGGER.error(errmsg)
        raise ValueError(errmsg)

    @property
    def latausfunktion_nimi(self):
        '''Latausfunktion nimi (tiedetään muuallakin missä mennään).'''
        return self._latausfunktion_nimi

    def __bool__(self):
        '''Kerro ollaanko edes teoriassa latauskunnossa.
        Emittoi
        -------
        signaali_virhe : str
            Jos ei olla latauskunnossa, millä tapaa ei.
        '''
        validi = True
        if not self.polku_lahde:
            errmsg = "Latauksen lähdepolkua ei ole määritelty."
            LOGGER.error(errmsg)
            self.signaali_virhe.emit(errmsg)
            validi = False
        if not self.polku_kohde:
            errmsg = "Latauksen kohdepolkua ei ole määritelty."
            LOGGER.error(errmsg)
            self.signaali_virhe.emit(errmsg)
            validi = False
        if not os.path.exists(os.path.dirname(self.polku_kohde)):
            errmsg = "Latauksen kohdekansiota {} ei ole olemassa.".format(
                os.path.dirname(self.polku_kohde)
                )
            LOGGER.error(errmsg)
            self.signaali_virhe.emit(errmsg)
            validi = False
        return validi

    def luo_tarvittavat_kansiot(self):
        '''
        Luo tarvittavat kohdekansiot asialle, jotta se voidaan sinne ladata.
        '''
        # Menee juureen
        if not self.tarvittava_kansio:
            return
        kohdekansio = os.path.join(self.kohdejuuri, self.tarvittava_kansio)
        # Kansio on jo olemassa
        if os.path.exists(kohdekansio):
            LOGGER.debug(f"Kansio {kohdekansio} on jo olemassa, käytetään.")
            return
        # Luo
        LOGGER.debug(f"Luodaan kansio {kohdekansio}")
        os.makedirs(kohdekansio)

    def lataa_http(self):
        pass
    def lataa_ssh(self):
        pass

    def lataa(self, *args, **kwargs):
        '''Protofunktio, ylikirjoita toteutuksissa.'''
        self.signaali_virhe.emit("Pohjaluokalla ei latailla.")
        self.signaali_valmis.emit()


class NimiLatain(Latain):
    '''
    Lataa käytettävissä olevat tietokantanimet palvelimelta.
    '''
    signaali_vastaus = QtCore.pyqtSignal(list)

    def __init__(self, asetukset):
        super().__init__(asetukset=asetukset)
        self.osoite = asetukset.osoite

    def lataa(self, *args, **kwargs):
        '''Lataa saatavilla olevien tietokantojen nimet.

        Emittoi
        -------
        signaali_virhe : str
            Jos jokin meni pieleen, virhekuvaus.
        signaali_vastaus : list str
            Saadut nimet listana stringejä.
        signaali_vastaus
        '''
        LOGGER.debug(f"Lataa tietokantanimet osoitteesta {self.osoite}")
        self.luo_tarvittavat_kansiot()
        vastaus = musapet.listaa_musatietokannat(self.osoite)
        if vastaus.virhe:
            LOGGER.debug(f"Virhe: {vastaus.virhe}")
            self.signaali_virhe.emit(vastaus.virhe)
        else:
            LOGGER.debug(f"Vastaus: {type(vastaus.vastaus)}")
            self.signaali_vastaus.emit(vastaus.vastaus)
        LOGGER.debug(f"Valmis.")
        self.signaali_valmis.emit()


class TietokantaLatain(Latain):
    '''
    Lataa valittu tietokanta palvelimelta.
    '''
    signaali_vastaus = QtCore.pyqtSignal(Tiedostopuu)

    def __init__(self, asetukset, nimi=""):
        '''Tietokanta ladataan nimen perusteella, eli tarvitsee nimen.'''
        super().__init__(asetukset=asetukset)
        self._nimi = ""
        self.nimi = nimi
    @property
    def nimi(self):
        '''Nimigetteri.'''
        return self._nimi
    @nimi.setter
    def nimi(self, uusiarvo):
        '''Nimisetteri (str)'''
        if isinstance(uusiarvo, str):
            self._nimi = uusiarvo
        else:
            errmsg = (
                "Odotettiin str nimeksi"
                +f", saatiin {type(uusiarvo)} {uusiarvo}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)

    def lataa(self):
        '''Lataa tietokanta nimen perusteella.

        Emittoi
        -------
        signaali_virhe : str
            Jos jokin meni pieleen, virhekuvaus.
        signaali_vastaus : Tiedostopuu
            Ladattu puu.
        signaali_valmis
            Kun toimenpide valmis (oli tulos mikä hyvänsä)
        '''
        LOGGER.debug(f"Lataa tietokanta {self.nimi} osoitteesta {self.osoite}")
        vastaus = musapet.lataa_tietokanta(self.nimi, self.osoite)
        if vastaus.virhe:
            LOGGER.debug(f"Virhe: {vastaus.virhe}")
            self.signaali_virhe.emit(vastaus.virhe)
        else:
            LOGGER.debug(f"Vastaus: {type(vastaus.vastaus)}")
            tietokanta = Tiedostopuu.diktista(vastaus.vastaus)
            self.signaali_vastaus.emit(tietokanta)
        LOGGER.debug(f"Valmis.")
        self.signaali_valmis.emit()

    def lue_tietokanta(self):
        '''Lue tietokanta.
        Jos tietokantaa ei löydy tiedostona määritellystä sijainnista,
        hae se palvelimelta.
        '''
        tiedostosijainti = os.path.join(
            self.asetukset.tietokantojen_sijainti,
            f"{self.nimi}.json")
        LOGGER.debug(
            f"Onko tiedosto {tiedostosijainti} olemassa:"
            +f" {os.path.exists(tiedostosijainti)}")
        if os.path.exists(tiedostosijainti):
            LOGGER.debug(
                f"Luetaan tietokanta {self.nimi}"
                +f" sijainnista {tiedostosijainti}.")
            with open(tiedostosijainti, "r", encoding="utf-8") as filu:
                dikti = json.load(filu)
                tiedostopuu = Tiedostopuu.diktista(dikti)
                LOGGER.debug("Luettiin.")
                self.signaali_vastaus.emit(tiedostopuu)
                LOGGER.debug(f"Valmis.")
                self.signaali_valmis.emit()
        else:
            LOGGER.debug(
                f"Ladataan tietokanta {self.nimi}"
                +f" palvelimelta {self.osoite}.")
            self.luo_tarvittavat_kansiot()
            vastaus = musapet.lataa_tietokanta(self.nimi, self.osoite)
            if vastaus.virhe:
                LOGGER.debug(f"Virhe: {vastaus.virhe}")
                self.signaali_virhe.emit(vastaus.virhe)
            else:
                LOGGER.debug(f"Vastaus: {type(vastaus.vastaus)}")
                tietokanta = Tiedostopuu.diktista(vastaus.vastaus)
                LOGGER.debug(
                    f"Kirjoitetaan ladattu tietokanta tiedostoon {tiedostosijainti}"
                    )
                with open(tiedostosijainti, "w+", encoding="utf-8") as filu:
                    json.dump(vastaus.vastaus, filu)
                    self.signaali_vastaus.emit(tietokanta)
            LOGGER.debug(f"Valmis.")
            self.signaali_valmis.emit()



class BiisiLatain(Latain):
    '''Lataa yksittäinen biisi polun perusteella.'''
    signaali_vastaus = QtCore.pyqtSignal(bool)

    def __init__(self, asetukset, polku_lahde="", polku_kohde="", latausfunktio="http"):
        super().__init__(asetukset=asetukset)
        # Lähdepolku (mistä ladataan)
        self._polku_lahde = ""
        self.polku_lahde = polku_lahde

    @property
    def polku_lahde(self):
        '''Lähdepolun getteri.'''
        return self._polku_lahde
    @polku_lahde.setter
    def polku_lahde(self, uusiarvo):
        '''Lähdepolun setteri.'''
        if isinstance(uusiarvo, str):
            self._polku_lahde = uusiarvo
        else:
            errmsg = (
                "Odotettiin str poluksi"
                +f", saatiin {type(uusiarvo)} {uusiarvo}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)

    def lataa_http(self):
        '''Lataa biisi käyttäen http-kutsua.

        Emittoi
        -------
        signaali_virhe : str
            Jos jokin meni pieleen, virhekuvaus.
        signaali_vastaus : bool
            Jos lataus onnistui, True. Muutoin False.
        signaali_valmis
        '''
        vastaus = musapet.lataa_biisi_kansioon(
            latauspolku = self.polku_lahde,
            kohdepolku = self.polku_kohde,
            osoite = self.osoite
            )
        if vastaus.virhe:
            LOGGER.error(f"Virhe: {vastaus.virhe}")
            self.signaali_virhe.emit(vastaus.virhe)
        self.signaali_vastaus.emit(vastaus.vastaus)
        LOGGER.debug(f"Valmis.")
        self.signaali_valmis.emit()

    def lataa_ssh(self):
        '''Lataa käyttäen legacy-ssh:ta.

        Emittoi
        -------
        signaali_vastaus : True
            Muodollinen True.
        signaali_valmis
        '''
        kfun.lataa(
            vaintiedosto=True,
            lahdepalvelin=self.osoite,
            lahdepolku=self.polku_lahde,
            kohdepalvelin=None,
            kohdepolku=self.polku_kohde
            )
        self.signaali_vastaus.emit(True)
        self.signaali_valmis.emit()

    def lataa(self):
        '''Lataa biisi tiedostopolun perusteella.

        Emittoi
        -------
        signaali_virhe : str
            Jos jokin meni pieleen, virhekuvaus.
        signaali_vastaus : bool
            True jos lataus onnistui, False jos ei.
            Legacy-SSH:n tapauksessa aina True, koska homma ulkoistettu.
        signaali_valmis
        '''
        self.luo_tarvittavat_kansiot()
        if bool(self):
            ylikirjoita = self.asetukset.ylikirjoita
            on_jo = os.path.exists(self.polku_kohde)
            if on_jo and not ylikirjoita:
                LOGGER.debug(f"{self.polku_kohde} löytyy jo, ei ladata.")
                self.signaali_vastaus.emit(True)
                self.signaali_valmis.emit()
            else:
                LOGGER.debug(f"Lataa {self.polku_lahde} kohteeseen {self.polku_kohde}")
                self.latausfunktio()
