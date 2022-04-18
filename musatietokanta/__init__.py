__version__ = "2022.04.18"
__author__  = "Pilperi"

import os
import logging
import configparser

LOGGER = logging.getLogger(__name__)
if not LOGGER.hasHandlers():
    LOGGER.addHandler(logging.NullHandler())

#-------------------------------------------------------------------------------
# Koneen määritykset
OSOITE = "http://62.78.212.11:5000/"

# Tunnista käytettävä kone kotikansion perusteella.
KOTIKANSIO = os.path.expanduser("~")
LOKAALI_KONE = os.path.basename(KOTIKANSIO)
TYOKANSIO = os.path.join(KOTIKANSIO, ".Musatietokanta")
SIJAINTI_LATAALISAA = os.path.join(os.path.dirname(__file__), "lataa_ja_lisaa.sh")

if not os.path.exists(TYOKANSIO):
    try:
        os.mkdir(TYOKANSIO)
    except PermissionError as err:
        LOGGER.error(
            f"Ei ole oikeuksia tehdä kotikansioon {KOTIKANSIO}"
            +"työskentelykansiota \".Musatietokanta\" :<"
            +f" {err}"
            )

CONFIGTIEDOSTO = os.path.join(TYOKANSIO, "asetukset.ini")

LOGGER.debug(f"LOKAALI_KONE: {LOKAALI_KONE}")
LOGGER.debug(f"KOTIKANSIO: {KOTIKANSIO}")
LOGGER.debug(f"TYOKANSIO: {TYOKANSIO}")
LOGGER.debug(f"CONFIGTIEDOSTO: {CONFIGTIEDOSTO}")
LOGGER.debug(f"SIJAINTI_LATAALISAA: {SIJAINTI_LATAALISAA}")


# Luetaan asetukset INI-tiedostosta, jos sellainen löytyy.
ASETUKSET = configparser.ConfigParser(default_section="Pettankone")
if os.path.exists(CONFIGTIEDOSTO):
    LOGGER.debug(f"Luetaan asetukset .ini-tiedostosta {CONFIGTIEDOSTO}")
    ASETUKSET.read(CONFIGTIEDOSTO)


# Asetuskokoonpanot
class Palvelintiedot:
    '''
    Määritä palvelimen asetukset siivosti yhdessä paikkaa.
    '''
    def __init__(self):
        self._nimi = ""
        self.osoite = ""
        self._tyyppi = "http"
        self.komento_lisaa_kappale = ""
        self._latauskansio = TYOKANSIO
        self._ylikirjoita = True
        self.raja_latausvaroitus = 50

        self.tietokannat = {}
        self._tietokantojen_sijainti = ""

    @property
    def nimi(self):
        '''Nimigetteri.'''
        return self._nimi
    @nimi.setter
    def nimi(self, uusiarvo):
        '''Nimisetteri. Päivitä tietokantojen sijainti samalla.'''
        if not isinstance(uusiarvo, str):
            errmsg = (
                "Palvelinasetusten nimi tulee olla str"
                +f", saatiin {type(uusiarvo)} {uusiarvo}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)
        self._nimi = uusiarvo
        if not self.tietokantojen_sijainti:
            self.tietokantojen_sijainti = os.path.join(self.latauskansio, self.nimi)

    @property
    def latauskansio(self):
        '''Latauskansion getteri.'''
        return self._latauskansio
    @latauskansio.setter
    def latauskansio(self, uusiarvo):
        '''Latauskansion setteri. Päivitä tietokantojen sijainti samalla.'''
        if not isinstance(uusiarvo, str) or not uusiarvo:
            errmsg = (
                "Latauskansion tulee olla ei-tyhjä str"
                +f", saatiin {type(uusiarvo)} {uusiarvo}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)
        # Jos kansiota ei ole, luodaan
        if not os.path.exists(uusiarvo):
            LOGGER.debug(f"Latauskansiota {uusiarvo} ei ole, luodaan.")
            os.makedirs(uusiarvo)
        self._latauskansio = uusiarvo
        if not self.tietokantojen_sijainti:
            self.tietokantojen_sijainti = os.path.join(self.latauskansio, self.nimi)

    @property
    def tietokantojen_sijainti(self):
        '''Tietokantojen sijainnin getteri.'''
        return self._tietokantojen_sijainti
    @tietokantojen_sijainti.setter
    def tietokantojen_sijainti(self, uusiarvo):
        '''Tietokantasijainnin setteri. Jos kansiota ei ole, luodaan.'''
        if not isinstance(uusiarvo, str) or not uusiarvo:
            errmsg = (
                "Tietokantojen latauskansion tulee olla ei-tyhjä str"
                +f", saatiin {type(uusiarvo)} {uusiarvo}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)
        # Jos kansiota ei ole, luodaan
        if not os.path.exists(uusiarvo):
            LOGGER.debug(f"Latauskansiota {uusiarvo} ei ole, luodaan.")
            os.makedirs(uusiarvo)
        self._tietokantojen_sijainti = uusiarvo

    @property
    def tyyppi(self):
        return self._tyyppi
    @tyyppi.setter
    def tyyppi(self, uusiarvo):
        if uusiarvo.lower() not in ("ssh", "http"):
            errmsg = f"{uusiarvo} ei ole käypä osoite, pitää olla http tai ssh"
            LOGGER.error(errmsg)
            raise ValueError(errmsg)
        self._tyyppi = uusiarvo.lower()

    @property
    def ylikirjoita(self):
        return self._ylikirjoita
    @ylikirjoita.setter
    def ylikirjoita(self, uusiarvo):
        kaannetty_uusiarvo = False
        if isinstance(uusiarvo, bool):
            kaannetty_uusiarvo = uusiarvo
        elif isinstance(uusiarvo, str):
            if uusiarvo.lower() in ("true", "kyllä", "joo"):
                kaannetty_uusiarvo = True
        self._ylikirjoita = kaannetty_uusiarvo

    def sisallyta_configgiin(self, configgi):
        '''
        Kirjoita asetuskattaus configgiin jotta se voidaan myöhemmin lukea.
        (läh. initoi esimerkki jota voidaan sitten muokata)
        '''
        configgi.set(self.nimi, "osoite", self.osoite)
        configgi.set(self.nimi, "tyyppi", self.tyyppi)
        configgi.set(self.nimi, "lisayskomento", self.komento_lisaa_kappale)
        configgi.set(self.nimi, "latauskansio", self.latauskansio)
        configgi.set(self.nimi, "ylikirjoita", self.ylikirjoita)
        configgi.set(self.nimi, "raja latausvaroitus", self.raja_latausvaroitus)
        configgi.set(self.nimi, "tietokantojen sijainti", self.tietokantojen_sijainti)
        configgi.set(self.nimi, "tietokannat", json.dumps(
            [f"{t}.json" for t in self.tietokannat]))

PALVELIMET = {
    }
for asetussetti in ASETUKSET:
    try:
        asetuskokoonpano = Palvelintiedot()
        # Etäpalvelimen nimi
        asetuskokoonpano.nimi = asetussetti
        LOGGER.debug(f"Nimi: {asetuskokoonpano.nimi} {type(asetuskokoonpano.nimi)}")
        # Etäpalvelimen osoite
        asetuskokoonpano.osoite = ASETUKSET.get(asetussetti, "etapalvelin")
        LOGGER.debug(f"Osoite: {asetuskokoonpano.osoite} {type(asetuskokoonpano.osoite)}")
        # Etäpalvelimen tyyppi, onko http vai ssh
        asetuskokoonpano.tyyppi = ASETUKSET.get(asetussetti, "tyyppi")
        LOGGER.debug(f"Tyyppi: {asetuskokoonpano.tyyppi} {type(asetuskokoonpano.tyyppi)}")
        # Paikallinen komento jolla ladatut kappaleet olisi tarkoitus lisätä
        asetuskokoonpano.komento_lisaa_kappale = ASETUKSET.get(asetussetti, "lisayskomento")
        LOGGER.debug(f"Lisäyskomento: {asetuskokoonpano.komento_lisaa_kappale} {type(asetuskokoonpano.tyyppi)}")
        # Minne kappaleet olisi tarkoitus ladata
        asetuskokoonpano.latauskansio = ASETUKSET.get(asetussetti, "latauskansio")
        LOGGER.debug(f"Latauskansio: {asetuskokoonpano.latauskansio} {type(asetuskokoonpano.latauskansio)}")
        # Ylikirjoituspolitiikka
        asetuskokoonpano.ylikirjoita = ASETUKSET.get(asetussetti, "ylikirjoita")
        LOGGER.debug(f"Ylikirjoituspolitiikka: {asetuskokoonpano.ylikirjoita} {type(asetuskokoonpano.ylikirjoita)}")
        # Latausvaroituksen raja
        asetuskokoonpano.raja_latausvaroitus = ASETUKSET.get(asetussetti, "raja latausvaroitus")
        LOGGER.debug(f"Latausvaroituksen raja: {asetuskokoonpano.raja_latausvaroitus} {type(asetuskokoonpano.raja_latausvaroitus)}")
        # Latausvaroituksen raja
        asetuskokoonpano.tietokantojen_sijainti = ASETUKSET.get(asetussetti, "tietokantojen sijainti")
        LOGGER.debug(f"Tietokantojen sijainti: {asetuskokoonpano.tietokantojen_sijainti} {type(asetuskokoonpano.tietokantojen_sijainti)}")

        # Lisää diktiin
        PALVELIMET[asetussetti] = asetuskokoonpano
        LOGGER.debug("Lisätty palvelinten listaan.")
    # Jos asetukset on kökösti, skippaa
    except (configparser.NoOptionError, ValueError) as err:
        LOGGER.warning(err)


#-------------------------------------------------------------------------------
# UI-määritykset


# Ikkunaelementtien kokomääritteet
# (aloitusblokki y, aloitusblokki x, pituus y, leveys x)
# Yksiköt ruutuja ja suhteellisia
UI_KOOT = {
    # Yläpalkki
    "hakukentta": (0,0,10,20),
    "tietokantavaihtoehdot": (0,20,10,30),
    "palvelinvaihtoehdot": (0,50,10,30),
    # Vasen reuna
    "selauspuu": (10,0,80,50),
    "nappi_tiedostopuu": (90,0,10,25),
    "nappi_artistipuu": (90,25,10,25),
    # Oikea reuna
    "valintatiedot": (10,50,40,30),
    "latauslista": (50,50,40,30),
    "latausnappi": (90,50,10,30),
    }
NAPPITYYLI = "background-color: #373c41; color: white; font-weight: bold"
