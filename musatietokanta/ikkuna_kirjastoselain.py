'''
Pääikkunan määritelmät, sisältää tietyn kattauksen muualla
määriteltyjä käyttöliittymäelementtejä fiksusti aseteltuna.
'''

import sys
import time
import subprocess
import logging

# QApplication, QWidget, QLabel, QGridLayout, QPushButton, QMainWindow
from PyQt5 import QtWidgets, QtGui
# pyqtSlot, QObject, QThread, pyqtSignal
from PyQt5 import Qt, QtCore

from tiedostohallinta.class_tiedostopuu import Tiedostopuu
from tiedostohallinta.class_biisiselaus import  Artistipuu, Hakukriteerit

from musatietokanta.class_tyolaiset import NimiLatain, TietokantaLatain, BiisiLatain
from musatietokanta import PALVELIMET, UI_KOOT, VARITEEMA, Palvelintiedot, lue_palvelinasetukset_tiedostosta
from musatietokanta import class_tyolaiset as tyovaki
from musatietokanta.class_ikkunaluokat import (
    SelausPuu, LatausLista, VirheIkkuna, Valintatiedot, Hakukentta, Pudotusvalikko
    )

LOGGER = logging.getLogger(__name__)

class Selausikkuna(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(5)
        self.setStyleSheet(VARITEEMA)

        #-----------------------------------------------------------------------
        # Datat jotka roikkuu messissä ja joita käsitellään

        # Puut (raakadata)
        self.tietokanta = Tiedostopuu()
        self.artistipuu = Artistipuu()
        self.hakutulos_tiedostopuu = Tiedostopuu()
        self.hakutulos_artistipuu = Artistipuu()
        # Varastoi myöhempää käyttöä varten (ei tarvii joka kerta ladata)
        self.aktiivipalvelin = Palvelintiedot()

        # Puut (visualisoitu data)
        self.selauspuu_tiedosto = SelausPuu()
        self.selauspuu_artisti = SelausPuu()
        self.selauspuu_hakutulos_tiedosto = SelausPuu()
        self.selauspuu_hakutulos_artisti = SelausPuu()
        #  Näytä vain yksi selaustyyppi kerrallaan
        self.nakyvat = {
            "selauspuu_tiedosto": True,
            "selauspuu_artisti": False,
            "selauspuu_hakutulos_tiedosto": False,
            "selauspuu_hakutulos_artisti": False,
            }

        # Hakumääritelmä
        self.hakukriteerit = Hakukriteerit()

        #-----------------------------------------------------------------------
        # Suorituslogiikka, säikeiden signalointi

        # Säikeet joissa asioita suoritetaan
        self.thread_tietokantanimet = QtCore.QThread()
        self.thread_tietokantalataus = QtCore.QThread()
        self.thread_biisilataus = QtCore.QThread()

        # Minkä nimisiä tietokantoja palvelimelta löytyy
        self.nimilatain = NimiLatain(self.aktiivipalvelin)
        self.nimilatain.moveToThread(self.thread_tietokantanimet)
        self.nimilatain.signaali_vastaus.connect(self.aseta_tietokantanimet)
        self.nimilatain.signaali_virhe.connect(self.sylje_virhe)

        # Lataa kulloinenkin tietokanta
        self.tietokantalatain = TietokantaLatain(self.aktiivipalvelin)
        self.tietokantalatain.moveToThread(self.thread_tietokantalataus)
        self.tietokantalatain.signaali_vastaus.connect(self.aseta_tietokanta)
        self.tietokantalatain.signaali_virhe.connect(self.sylje_virhe)

        # Biisien lataajaelementti
        self.biisilatain = BiisiLatain(self.aktiivipalvelin)
        self.biisilatain.kohdejuuri = "./"
        self.biisilatain.moveToThread(self.thread_biisilataus)
        self.biisilatain.signaali_valmis.connect(self.siirry_seuraavaan)
        self.biisilatain.signaali_vastaus.connect(self.lisaa_soittolistaan)
        self.biisilatain.signaali_virhe.connect(self.sylje_virhe)

        # Threadialoitukset
        self.thread_tietokantanimet.started.connect(self.populoi_tietokantanimet)
        self.thread_tietokantalataus.started.connect(self.tietokantalatain.lue_tietokanta)
        self.thread_biisilataus.started.connect(self.biisilatain.lataa)

        #-----------------------------------------------------------------------
        # UI-kälkyttimet

        # Näytä ladattavissa olevat tietokannat pudotusvalikkona
        self.tietokantavaihtoehdot = Pudotusvalikko()
        self.tietokantavaihtoehdot.currentIndexChanged.connect(self.vaihda_tietokantaa)
        self.tietokantavaihtoehdot.signaali_vastaus.connect(self.paivita_tietokanta)

        # Näytä käytettävissä olevat palvelimet pudotusvalikkona
        self.palvelinvaihtoehdot = Pudotusvalikko()
        self.palvelinvaihtoehdot.currentIndexChanged.connect(self.vaihda_palvelinta)
        self.palvelinvaihtoehdot.signaali_vastaus.connect(self.paivita_palvelimet)
        self.palvelinvaihtoehdot.addItems(["<palvelimet>"] + list(PALVELIMET))

        # Mikä puunäkymä on tällä hetkellä aktiivisena
        self.aktiivipuu = self.selauspuu_tiedosto

        # Vaihtele tiedostopuun ja artistipuun välillä
        self.nappi_tiedostopuu = QtWidgets.QPushButton()
        self.nappi_artistipuu = QtWidgets.QPushButton()
        self.nappi_tiedostopuu.setStyleSheet(VARITEEMA+"font-weight: bold")
        self.nappi_artistipuu.setStyleSheet(VARITEEMA+"font-weight: bold")
        self.nappi_tiedostopuu.setText("Kansio/Alikansio")
        self.nappi_artistipuu.setText("Artisti/Albumi")
        self.nappi_tiedostopuu.clicked.connect(self.vaihda_tiedostopuuhun)
        self.nappi_artistipuu.clicked.connect(self.vaihda_artistipuuhun)

        # Valinnan tiedot
        self.valintatiedot = Valintatiedot()
        self.selauspuu_tiedosto.selectionModel().selectionChanged.connect(self.paivita_tekstiboksi)
        self.selauspuu_artisti.selectionModel().selectionChanged.connect(self.paivita_tekstiboksi)
        self.selauspuu_hakutulos_tiedosto.selectionModel().selectionChanged.connect(self.paivita_tekstiboksi)
        self.selauspuu_hakutulos_artisti.selectionModel().selectionChanged.connect(self.paivita_tekstiboksi)

        # Latausjono
        self.latauslista = LatausLista(kohdejuuri="./")

        # Latausnappi
        self.latausnappi = QtWidgets.QPushButton()
        self.latausnappi.setStyleSheet(VARITEEMA+"font-weight: bold")
        self.latausnappi.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.latausnappi.setFocusPolicy(QtCore.Qt.NoFocus)
        self.latausnappi.setText("Lataa")
        self.latausnappi.clicked.connect(self.lisaa_valittu_latausjonoon)

        # Hakukenttä
        self.hakukentta = Hakukentta()
        self.hakukentta.returnPressed.connect(self.populoi_hakutuloksilla)

        # Värit kohdilleen
        self.selauspuu_tiedosto.setStyleSheet(VARITEEMA)
        self.selauspuu_artisti.setStyleSheet(VARITEEMA)
        self.selauspuu_hakutulos_tiedosto.setStyleSheet(VARITEEMA)
        self.selauspuu_hakutulos_artisti.setStyleSheet(VARITEEMA)

        #-----------------------------------------------------------------------
        # Asioiden sijainnit

        # Puuselaimet kaikki samaan kohtaan
        self.grid.addWidget(self.selauspuu_tiedosto, *UI_KOOT["selauspuu"])
        self.grid.addWidget(self.selauspuu_artisti, *UI_KOOT["selauspuu"])
        self.grid.addWidget(self.selauspuu_hakutulos_tiedosto, *UI_KOOT["selauspuu"])
        self.grid.addWidget(self.selauspuu_hakutulos_artisti, *UI_KOOT["selauspuu"])

        # Näkymän vaihtonamiskat
        self.grid.addWidget(self.nappi_tiedostopuu, *UI_KOOT["nappi_tiedostopuu"])
        self.grid.addWidget(self.nappi_artistipuu, *UI_KOOT["nappi_artistipuu"])

        # Yläpalkki
        # Etsimiskenttä
        self.grid.addWidget(self.hakukentta, *UI_KOOT["hakukentta"])
        # Tietokantojen nimet pudotusvalikkona
        self.grid.addWidget(self.tietokantavaihtoehdot, *UI_KOOT["tietokantavaihtoehdot"])
        # Palvelinten nimet pudotusvalikkona
        self.grid.addWidget(self.palvelinvaihtoehdot, *UI_KOOT["palvelinvaihtoehdot"])

        # Valinnan tiedot
        self.grid.addWidget(self.valintatiedot, *UI_KOOT["valintatiedot"])

        # Latauslista oikealle alas
        self.grid.addWidget(self.latauslista, *UI_KOOT["latauslista"])

        # Latausnappi
        self.grid.addWidget(self.latausnappi, *UI_KOOT["latausnappi"])

        self.setLayout(self.grid)
        self.setWindowTitle("Uusi musatietokantaselain")
        self.setGeometry(50,50,200,400)

        # Sulkemistoiminto ctrl+q
        self.quitSc = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Q'), self)
        self.quitSc.activated.connect(QtWidgets.QApplication.instance().quit)

        self.alusta()

    #---------------------------------------------------------------------------

    def alusta(self):
        '''Aja alustustoimenpiteet.'''
        self.show()
        #self.thread_tietokantanimet.start()
        self.aseta_puunakyma()

    def aseta_tietokantanimet(self, nimet):
        self.tietokantanimet = nimet
        LOGGER.debug(f"Ladattiin tietokantanimet: {self.tietokantanimet}")
        self.tietokantavaihtoehdot.clear()
        self.tietokantavaihtoehdot.addItems(["<tietokantanimet>"]+nimet)
        self.thread_tietokantanimet.quit()

    def populoi_tietokantanimet(self):
        '''Lataa tietokantojen nimet palvelimelta'''
        self.nimilatain.lataa()

    def vaihda_palvelinta(self):
        '''Vaihda lähdepalvelimesta toiseen.'''
        LOGGER.debug("Vaihda palvelinta.")
        # ei palvelimia tai infoteksti
        if self.palvelinvaihtoehdot.currentIndex() in (0,-1):
            LOGGER.debug("Skip")
            return
        palvelin = self.palvelinvaihtoehdot.currentText()
        LOGGER.debug(f"Vaihda palvelimeen {palvelin}")
        self.aktiivipalvelin = PALVELIMET.get(palvelin)
        # Aseta latainten asetukset ajan tasalle
        self.nimilatain.asetukset = self.aktiivipalvelin
        self.tietokantalatain.asetukset = self.aktiivipalvelin
        self.biisilatain.asetukset = self.aktiivipalvelin
        self.nimilatain.tyyppi = self.aktiivipalvelin.tyyppi
        self.tietokantalatain.tyyppi = self.aktiivipalvelin.tyyppi
        self.biisilatain.tyyppi = self.aktiivipalvelin.tyyppi
        # Kansiot oikein
        self.biisilatain.kohdejuuri = self.aktiivipalvelin.latauskansio
        self.latauslista.kohdejuuri = self.aktiivipalvelin.latauskansio
        # Aseta nimet ja puu ajan tasalle
        self.thread_tietokantanimet.start()
        self.aseta_puunakyma()

    def paivita_palvelimet(self, booli):
        '''Päivitä palvelinlista.'''
        LOGGER.debug("Päivitä palvelinlista.")
        lue_palvelinasetukset_tiedostosta()
        self.palvelinvaihtoehdot.clear()
        self.palvelinvaihtoehdot.addItems(["<palvelimet>"] + list(PALVELIMET))

    def lisaa_valittu_latausjonoon(self, asia=None):
        '''
        Lisää valittu asia latausjonon perälle.
        '''
        if not isinstance(asia, Qt.QStandardItem):
            asia = self.aktiivipuu.anna_valittu()
        self.latauslista.lisaa(asia)
        if not self.thread_biisilataus.isRunning():
            self.aloita_latausrumba()

    def aseta_puunakyma(self):
        '''
        Valitse mikä näkymä näytetään puunäkymäruudussa.
        '''
        avaa = False
        for attr,arvo in self.nakyvat.items():
            selausnakyma = getattr(self, attr)
            selausnakyma.setVisible(arvo)
            # Pidetään kirjaa mikä puista on näkyvillä
            # (osataan valia asiat oikeasta puusta)
            if arvo:
                self.aktiivipuu = selausnakyma
                if attr in ("selauspuu_tiedosto", "selauspuu_hakutulos_tiedosto"):
                    avaa = True
        if avaa:
            self.aktiivipuu.avaa_juuri()

    def vaihda_tiedostopuuhun(self):
        '''Vaihda selauspuun näkymätyyppiä artistipuu -> tiedostopuu.'''
        self.nappi_artistipuu.setEnabled(False)
        # Koko puu -> koko puu
        if self.nakyvat["selauspuu_artisti"]:
            self.nakyvat["selauspuu_artisti"] = False
            self.nakyvat["selauspuu_tiedosto"] = True
        # Hakutulokset -> Hakutulokset
        elif self.nakyvat["selauspuu_hakutulos_artisti"]:
            self.nakyvat["selauspuu_hakutulos_artisti"] = False
            self.nakyvat["selauspuu_hakutulos_tiedosto"] = True
        self.aseta_puunakyma()
        self.nappi_artistipuu.setEnabled(True)

    def vaihda_artistipuuhun(self):
        '''Vaihda selauspuun näkymätyyppiä tiedostopuu -> artistipuu.'''
        self.nappi_tiedostopuu.setEnabled(False)
        # Koko puu -> koko puu
        if self.nakyvat["selauspuu_tiedosto"]:
            self.nakyvat["selauspuu_tiedosto"] = False
            self.nakyvat["selauspuu_artisti"] = True
            # Kansoita tarvittaessa (tiedostopuut aina kansoitettu)
            if not self.selauspuu_artisti:
                self.selauspuu_artisti.kansoita_artistirakenne(self.artistipuu)
        # Hakutulokset -> Hakutulokset
        elif self.nakyvat["selauspuu_hakutulos_tiedosto"]:
            self.nakyvat["selauspuu_hakutulos_tiedosto"] = False
            self.nakyvat["selauspuu_hakutulos_artisti"] = True
            # Kansoita tarvittaessa (tiedostopuut aina kansoitettu)
            if not self.selauspuu_hakutulos_artisti:
                self.selauspuu_hakutulos_artisti.kansoita_artistirakenne(self.hakutulos_artistipuu)
        self.aseta_puunakyma()
        self.nappi_tiedostopuu.setEnabled(True)

    def lataa_tietokanta(self):
        self.thread_tietokantalataus.start()
        self.tietokantavaihtoehdot.setEnabled(False)

    def aseta_tietokanta(self, kanta):
        self.tietokanta = kanta
        self.artistipuu = Artistipuu(kanta)
        self.aktiivipalvelin.tietokannat[self.tietokantalatain.nimi] = self.tietokanta
        self.aktiivipalvelin.artistipuut[self.tietokantalatain.nimi] = self.artistipuu
        self.selauspuu_tiedosto.kansoita_tiedostorakenne(self.tietokanta)
        self.selauspuu_artisti.kansoita_artistirakenne(self.artistipuu)
        self.thread_tietokantalataus.quit()
        self.tietokantavaihtoehdot.setEnabled(True)
        self.aseta_puunakyma()

    def vaihda_tietokantaa(self):
        # Lataa vain jos oikeasti joku tietokanta valittuna
        if self.tietokantavaihtoehdot.currentIndex() in (0,-1):
            return
        haettava = self.tietokantavaihtoehdot.currentText()
        kanta = self.aktiivipalvelin.tietokannat.get(haettava)
        artistipuu = self.aktiivipalvelin.tietokannat.get(haettava)
        if kanta is None:
            self.tietokantalatain.nimi = haettava
            self.lataa_tietokanta()
        else:
            self.tietokanta = kanta
            self.artistipuu = artistipuu
            self.selauspuu_tiedosto.kansoita_tiedostorakenne(kanta)
            self.selauspuu_artisti.kansoita_artistirakenne(artistipuu)
        self.aseta_puunakyma()

    def paivita_tietokanta(self, booli):
        '''Lataa tietokanta uusiksi palvelimelta.'''
        if self.tietokantavaihtoehdot.currentIndex() in (0,-1):
            return
        self.tietokantalatain.lataa()
        while self.thread_tietokantalataus.isRunning():
            time.sleep(1E-6)
        self.aktiivipalvelin.tallenna(self.tietokantalatain.nimi)

    def paivita_tekstiboksi(self):
        '''
        Päivitä valintatietoboksi.
        '''
        asia = self.aktiivipuu.anna_valittu()
        st = str(asia)*(asia is not None)
        self.valintatiedot.setText(st)

    #---------------------------------------------------------------------------
    # Hakutoiminnot
    def populoi_hakutuloksilla(self):
        hakutulokset = self.hakukentta.hae()
        if not hakutulokset:
            LOGGER.debug("Hakutermit ei kunnolliset.")
            oli_tuloksia = False
            tulokset = {}
        else:
            haku = Hakukriteerit(hakutulokset)
            oli_tuloksia, tulokset = haku.etsi_tietokannasta(self.tietokanta)
        if oli_tuloksia:
            # Näytä tiedostopuuna
            if (self.nakyvat.get("selauspuu_tiedosto")
                or self.nakyvat.get("selauspuu_hakutulos_tiedosto")
                ):
                self.nakyvat = {
                    avain: (False if avain != "selauspuu_hakutulos_tiedosto"
                            else True)
                    for avain in self.nakyvat
                    }
            # Näytä artistipuuna
            else:
                self.nakyvat = {
                    avain: (False if avain != "selauspuu_hakutulos_artisti"
                            else True)
                    for avain in self.nakyvat
                    }
            self.hakutulos_tiedostopuu = tulokset
            self.hakutulos_artistipuu = Artistipuu(tulokset)
            self.selauspuu_hakutulos_tiedosto.kansoita_tiedostorakenne(self.hakutulos_tiedostopuu)
            self.selauspuu_hakutulos_artisti.kansoita_artistirakenne(self.hakutulos_artistipuu)
            self.aseta_puunakyma()
            self.aktiivipuu.expandAll()
        # Jos ei tuloksia, näytä alkuperäinen puu
        else:
            # Näytä tiedostopuuna
            if (self.nakyvat.get("selauspuu_tiedosto")
                or self.nakyvat.get("selauspuu_hakutulos_tiedosto")
                ):
                self.nakyvat = {
                    avain: (False if avain != "selauspuu_tiedosto"
                            else True)
                    for avain in self.nakyvat
                    }
            # Näytä artistipuuna
            else:
                self.nakyvat = {
                    avain: (False if avain != "selauspuu_artisti"
                            else True)
                    for avain in self.nakyvat
                    }
            self.hakutulos_tiedostopuu = Tiedostopuu()
            self.hakutulos_artistipuu = Artistipuu()
            self.aseta_puunakyma()

    #---------------------------------------------------------------------------
    # Lataustoiminnot

    def lisaa_soittolistaan(self, status):
        '''Jos biisi saatiin ladattua, lisää se soittolistaan.

        Jos latausmenetelmänä on http, tulee pitää huoli siitä että
        kappaletta ei vain ladata vaan että se myös lisätään soitinohjelman
        soittolistalle (legacy ssh hoitaa nämä molemmat samaan syssyyn.)

        Sisään
        ------
        status : bool
            Jos lataus onnistui, True (lisää listaan jos HTTP-kutsu).
            Muutoin älä tee mitään.
        '''
        if not status:
            return
        sijainti = self.biisilatain.polku_kohde
        komento = self.aktiivipalvelin.komento_lisaa_kappale
        subprocess.run([*komento, sijainti])

    def sylje_virhe(self, virhe):
        '''Anna virheilmoitus pop-uppina.'''
        VirheIkkuna(virhe)

    def aloita_latausrumba(self):
        '''Aloita latauslistan läpikäynti.'''
        self.siirry_seuraavaan(sailyta=True)

    def siirry_seuraavaan(self, sailyta=False):
        '''
        Laita seuraava asia latautumaan ja poista edellinen listasta.
        '''
        # Tapa edellisen latauksen threadi ja odota kunnes se on veks
        if self.thread_biisilataus.isRunning():
            self.thread_biisilataus.quit()
            while self.thread_biisilataus.isRunning():
                time.sleep(1E-6)
        # Poista edellinen asia listasta, jollei rosessi ole alussa
        if not sailyta:
            edellinen_asia = self.latauslista.takeItem(0)
        # Ota listasta seuraava juttu ladattavaksi
        seuraava_asia = self.latauslista.item(0)
        if seuraava_asia is not None:
            seuraava_data = seuraava_asia.data(QtCore.Qt.UserRole)
            self.biisilatain.polku_lahde = seuraava_data.polku_lahde
            self.biisilatain.polku_kohde = seuraava_data.polku_kohde
            self.biisilatain.tarvittava_kansio = seuraava_data.tarvittava_kansio
            seuraava_asia.setBackground(QtGui.QColor(*LatausLista.TAUSTA_LATAUS))
            seuraava_asia.setForeground(QtGui.QColor(*LatausLista.TEKSTI_LATAUS))
            self.thread_biisilataus.start()
