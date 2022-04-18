'''
Ikkunaelementtien luokkamääritelmät.
Sitovat työväenluokan Qt-elementteihin.
'''
import os
import logging
from PyQt5 import Qt, QtWidgets, QtGui, QtCore

from tiedostohallinta.class_tiedostopuu import Tiedostopuu
from tiedostohallinta.class_biisiselaus import  Artistipuu

from musatietokanta import class_tyolaiset as tyovaki
from musatietokanta.class_uielementit import (
    Kansioelementti, Tiedostoelementti, Artistielementti,
    Albumielementti, Raitaelementti,
    )

LOGGER = logging.getLogger(__name__)


#-------------------------------------------------------------------------------


class VirheIkkuna(QtWidgets.QMessageBox):
    '''Näytä virheilmoitus popuppina.'''
    def __init__(self, virheteksti=""):
        super().__init__()
        self.width  = 500
        self.height = 500
        self.setWindowTitle("Virhe")
        self.setText(virheteksti)
        self.setStandardButtons(QtWidgets.QMessageBox.Yes)
        self.ok = self.button(QtWidgets.QMessageBox.Yes)
        self.ok.setText('Daym')
        self.exec_()


#-------------------------------------------------------------------------------

class LatausAsia:
    '''Ladattava asia simppelissä muodossa.'''
    def __init__(self, polku_lahde, polku_kohde, tarvittava_kansio=None):
        self.polku_lahde=polku_lahde
        self.polku_kohde=polku_kohde
        self.tarvittava_kansio=tarvittava_kansio

#-------------------------------------------------------------------------------


class LatausLista(QtWidgets.QListWidget):
    '''
    Latausjonolista.
    '''
    TAUSTA_LATAUS = (0,155,0)
    TEKSTI_LATAUS = (200,200,200)

    def __init__(self, kohdejuuri):
        super().__init__()
        # Juurikansio kaikille ladattaville asioille
        if isinstance(kohdejuuri, str) and os.path.exists(kohdejuuri):
            self.kohdejuuri = kohdejuuri
        else:
            errmsg = f"Kohdejuuri {kohdejuuri} ei ole käypä kansio."
            raise ValueError(errmsg)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        '''
        Poista asiat klikkaamall oikealla.
        '''
        if event.type() == QtCore.QEvent.ContextMenu and source is self:
            itemi = source.itemAt(event.pos())
            rivi = self.row(itemi)
            # Ekaa ei voi poistaa koska se on jo latauksessa.
            if rivi != 0 and itemi is not None:
                LOGGER.debug(f"poista {itemi.text()} @ {rivi}")
                poistettu = self.takeItem(rivi)
            return True
        return False

    def lisaa(self, asia):
        '''
        Lisää asia. Perusmuotona yksittäinen biisi.
        Jos albumi, artistituotanto tmv, pilkotaan biisilistaksi ja lisätään
        yksi biisi kerrallaan.
        '''
        ladattavat = []
        lataustekstit = []
        # Yksittäiset biisit juurikansioon
        if isinstance(asia, (Tiedostoelementti, Raitaelementti)):
            tiedostonimi = os.path.split(asia.tiedostopolku())[-1]
            latausasia = LatausAsia(
                polku_lahde=asia.tiedostopolku(),
                polku_kohde=os.path.join(self.kohdejuuri, tiedostonimi)
                )
            ladattavat = [latausasia]
            lataustekstit = [asia.latauslistateksti()]

        # Kokonaisissa kansioissa täytyy katsoa että kaikki tarpeelliset
        # alikansiot tulee luotua ennen latauksen aloittamista
        elif isinstance(asia, Kansioelementti):
            def hae_kansion_biisit(kansio, edellisetkansiot=None):
                # Juuritaso (miksi kukaan tosin)
                if kansio.edellinentaso is None:
                    tarvittava_kansio = None
                # Kansioista ensimmäinen (kansio/biisi.mp3)
                elif edellisetkansiot is None:
                    tarvittava_kansio = kansio.kansio
                # Jokin myöhemmistä rekursion vaiheista (kansio/CD1/biisi.mp3)
                else:
                    tarvittava_kansio = os.path.join(edellisetkansiot, kansio.kansio)
                # Biisi kerrallaan latauskelpoiseksi asiaksi
                for biisi in asia.puu.tiedostot:
                    latausasia = LatausAsia(
                        polku_lahde=os.path.join(
                            kansio.hae_nykyinen_polku(), biisi.tiedostonimi),
                        polku_kohde=os.path.join(
                            self.kohdejuuri, tarvittava_kansio, biisi.tiedostonimi),
                        tarvittava_kansio=tarvittava_kansio
                        )
                    ladattavat.append(latausasia)
                    lataustekstit.append(f"{biisi.esittaja} - {biisi.biisinimi}")
                # Rekursiivisesti alikansioihin
                for alikansio in kansio.alikansiot:
                    hae_kansion_biisit(alikansio, tarvittava_kansio)
            hae_kansion_biisit(asia.puu)

        # Artistielementti: Kansio artistinimellä ja sen alla albuminimet
        # <juuri>/Artisti/Albumi/biisi.mp3
        elif isinstance(asia, Artistielementti):
            artisti = asia.artisti
            for albuminimi, raitalista in asia.dikti.items():
                for biisin_puu, biisi in raitalista:
                    latausasia = LatausAsia(
                        polku_lahde=os.path.join(
                            biisin_puu.hae_nykyinen_polku(), biisi.tiedostonimi),
                        polku_kohde=os.path.join(
                            self.kohdejuuri, artisti, albuminimi, biisi.tiedostonimi),
                        tarvittava_kansio=os.path.join(
                            artisti, albuminimi)
                        )
                    ladattavat.append(latausasia)
                    lataustekstit.append(f"{biisi.esittaja} - {biisi.biisinimi}")
        # Albumielementti saman tapainen kuin Artistielementti (läsnä @em.)
        # <juuri>/Albumi/biisi.mp3
        elif isinstance(asia, Albumielementti):
            albumi = asia.albumi
            raitalista = asia.biisit
            for biisin_puu, biisi in raitalista:
                latausasia = LatausAsia(
                    polku_lahde=os.path.join(
                        biisin_puu.hae_nykyinen_polku(), biisi.tiedostonimi),
                    polku_kohde=os.path.join(
                        self.kohdejuuri, albumi, biisi.tiedostonimi),
                    tarvittava_kansio=os.path.join(
                        albumi),
                    )
                ladattavat.append(latausasia)
                lataustekstit.append(f"{biisi.esittaja} - {biisi.biisinimi}")

        # Käy lisäätävien asioiden lista lävitte ja lisää ne
        for latausindeksi,latausasia in enumerate(ladattavat):
            listaelementti = QtWidgets.QListWidgetItem()
            teksti = lataustekstit[latausindeksi]
            listaelementti.setText(teksti) # tekstimuoto
            listaelementti.setData(QtCore.Qt.UserRole, latausasia) # itse asia
            self.addItem(listaelementti)


#-------------------------------------------------------------------------------


class SelausPuu(QtWidgets.QTreeView):
    '''
    Selaa hierarkista tiedostorakennetta tahi artisti-albumi-jaottelua.
    '''
    signaali_tuplaklikattu = QtCore.pyqtSignal(Qt.QStandardItem)
    def __init__(self, parent=None, tiedostopuu=None, artistipuu=None):
        '''
        Inittifunktio, määritä lähinnä minimiasiat.

        Sisään
        ------
        parent : None, valinnainen
            Jos puulla on jokin vanhempi (läh. ikkuna josta kutsutaan).
        tiedostopuu : Tiedostopuu tai dict, valinnainen
            Jos annettu, täyttää tiedot saman tien inee muodossa
            kansio/alikansio/.../alikansio/biisi
        artistipuu : Artistipuu, Tiedostopuu tai dict, valinnainen
            Jos annettu, täyttää saman tien artisti/albumi/biisi-jaottelulla.
        '''
        super().__init__(parent=parent)
        self.setHeaderHidden(True)
        self.puumalli = Qt.QStandardItemModel()
        self.juurisolmu = self.puumalli.invisibleRootItem()
        self.setModel(self.puumalli)
        self.expand(self.puumalli.index(0,0))
        self.kansoitettu = False

        # Jos sekä tiedostopuu että artistipuu annettu, eka dominoi
        if tiedostopuu is not None:
            self.kansoita_tiedostorakenne(tiedostopuu)
        elif artistipuu is not None:
            self.kansoita_artistirakenne(artistipuu)


    def __bool__(self):
        '''Jos puu kansoitettu, True. Muutoin False.'''
        if self.kansoitettu:
            return True
        return False


    def kansoita_tiedostorakenne(self, puu):
        '''
        Täytä puun tiedot kansio/alikansio/biisi -rakenteella.
        Juuren alla kasa kansioita (Kansioelementti),
        joiden alla kasa tiedostoja (Tiedostoelementti)

        Sisään
        ------
        puu : Tiedostopuu tai dict
            Puu jonka tiedoilla hierarkia täytetään.
            Saa olla joko valmiina Tiedostopuuna tai dictinä
            jonka voi sellaiseksi lukea.
        '''
        # Tyhjää edelliset
        self.puumalli.clear()
        self.juurisolmu = self.puumalli.invisibleRootItem()
        # Täytä uudet
        def kansoita_puulla(puu, juuri, edellinen):
            fkoko = 10
            # Ylempänä juuressa isompi fonttikoko ("pääkansiot")
            if juuri < 2:
                fkoko = 12

            # Elementin väri vuorotteleva & hiipuva
            r = min(255,max(255+(-1+2*(juuri%2))*juuri*25, 0))
            g = min(255,max(255+(1-2*(juuri%2))*juuri*25, 0))
            b = min(255,max(255-juuri*25, 0))
            elementti = Kansioelementti(puu, fonttikoko=fkoko, vari=(r, g, b))
            # Täytä kansion alle kaikki mitä sen alle kuuluu
            for alikansio in puu.alikansiot:
                kansoita_puulla(alikansio, juuri+1, elementti)
            for biisi in puu.tiedostot:
                biisielementti = Tiedostoelementti(biisi)
                elementti.appendRow(biisielementti)
            edellinen.appendRow(elementti)
        if isinstance(puu, dict):
            tiedostopuu = Tiedostopuu.diktista(puu)
        elif isinstance(puu, Tiedostopuu):
            tiedostopuu = puu
        else:
            errmsg = (
                "Odotettiin tiedostopuuksi Tiedostopuu tai dict"
                +f", saatiin {type(puu)}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)
        kansoita_puulla(puu, juuri=0, edellinen=self.juurisolmu)
        self.kansoitettu = True

    def kansoita_artistirakenne(self, puu):
        '''
        Täytä puun tiedot artisti/albumi/biisi -jaottelulla.
        Juuren alla kasa artisteja (Artistielementti)
        joiden alla kasa albumeita (Albumielementti)
        joiden alla kasa biisejä (Raitaelementti).

        Sisään
        ------
        puu : Tiedostopuu, Artistipuu tai dict
            Puu jonka tiedot rykäistään hierarkiseksi puuksi.
            Jos Tiedostopuu tai dict, sen pohjalta tuotetaan Artistipuu.
            Siinä menee yleensä hetki.
        '''
        if isinstance(puu, Artistipuu):
            artistipuu = puu
        elif isinstance(puu, dict):
            tiedostopuu = Tiedostopuu.diktista(puu)
            artistipuu = Artistipuu(tiedostopuu)
        elif isinstance(puu, Tiedostopuu):
            artistipuu = Artistipuu(puu)
        else:
            errmsg = (
                "Odotettiin artistipuuksi Tiedostopuu, Artistipuu tai dict"
                +f", saatiin {type(puu)}"
                )
            LOGGER.error(errmsg)
            raise ValueError(errmsg)
        # Tyhjää edelliset
        self.puumalli.clear()
        self.juurisolmu = self.puumalli.invisibleRootItem()
        # Täytä uudet
        for artisti in artistipuu.artistit:
            artistielementti = Artistielementti(artistipuu, artisti)
            self.juurisolmu.appendRow(artistielementti)
        self.kansoitettu = True

    def anna_valittu(self):
        '''
        Palauta valittu asia.
        '''
        asia = self.puumalli.itemFromIndex(self.currentIndex())
        return asia

    def avaa_juuri(self):
        '''Avaa juurisolmu niin että näkee jotain.'''
        self.expand(self.puumalli.index(0,0))


class Valintatiedot(QtWidgets.QTextEdit):
    '''
    Valintatietoruutu.
    Käytännössä läjä tekstiä.
    '''
    TAUSTAVARI = "#31363b"
    TEKSTIVARI = "#ffffff"

    def __init__(self, taustavari=TAUSTAVARI, tekstivari=TEKSTIVARI):
        '''Inittifunktio'''
        super().__init__()
        self.setText("")
        self.setReadOnly(True)
        self.setAlignment(QtCore.Qt.AlignTop)
        self.setWordWrapMode(0)
        self.setStyleSheet(
            f"background-color: {taustavari};"
            +f"color: {tekstivari};"
            )

    def aseta_teksti(self, asia):
        '''
        Aseta asian teksti tekstiksi.
        '''
        if isinstance(asia, PuuElementti):
            self.setText(str(asia))
        else:
            self.setText("")


class Hakukentta(QtWidgets.QLineEdit):
    '''
    Hakukenttä, joka parsii tekstin järkevästi.
    '''
    def __init__(self):
        super().__init__()
        self.setClearButtonEnabled(True)
        self.setText("Vapaahaku")
        self.selectAll()
        self.setCompleter(None)
        self.setToolTip("Täsmähaku lainausmerkeillä")
        self.setMinimumSize(200,50)

    def parsi_hakutermit(self, teksti):
        '''
        Parsii hakukentän tekstin hakuargumenteiksi.
        Tätä kutsutaan ei-tyhjillä stringeillä.

        Teksti splitataan niin että hakutermit on erotettu
        välilyönneillä, poislukien "lainausmerkeillä ympäröidyt pätkät",
        jotka muodostavat yksittäisen hakutermin.
        '''
        if len(teksti) == 1:
            return([teksti])
        # Rullataan merkki kerrallaan läpi
        hakutermit = []
        hipsut_auki = teksti[0] == "\"" # alkaako hipsuilla?
        termi = ""
        if not hipsut_auki:
            termi = teksti[0]
        i = 1
        while i < len(teksti):
            # Rullataan eteenpäin kunnes vastaan tulee välilyönti
            # jollei olla aloitettu hipsumerkeillä ympäröityä pätkää
            j = 0
            while i+j < len(teksti):
                LOGGER.debug(f"Hakutermi: {termi}")
                # Vastassa välilyönti eikä hipsut ole auki: katkaistaan
                if teksti[i+j] == " " and not hipsut_auki:
                    j += 1
                    break
                # Hipsut on auki ja vastassa hipsu: katkaistaan ja vaihdetaan hipsutilaa
                if teksti[i+j] == "\"":
                    hipsut_auki = not hipsut_auki
                    j += 1
                    break
                termi += teksti[i+j]
                j += 1
            # Lisätään listaan ja resetoidaan termikasaus
            if len(termi):
                LOGGER.debug(f"Lisätään \"{termi}\" hakutermeihin")
                hakutermit.append(termi)
            termi = ""
            i += j
        return hakutermit

    def hae(self):
        '''
        Suorita haku.
        '''
        hakudikti = {}
        oli_tuloksia = False
        # Sarjan nimi
        hakutermit = None
        if self.text() and self.text() != "Vapaahaku":
            teksti = self.text()
            # Asiat splitattu välilyönneillä, lainausmerkkien
            # välissä olevat asiat omia entiteettejään.
            # Vähän sekamelska niin parsitaan erillisen funktion puolella.
            hakutermit = self.parsi_hakutermit(teksti)
        LOGGER.debug(f"Vapaahaku termeillä: {hakutermit}")
        hakudikti = {
                    "vapaahaku":     hakutermit
                    # "ehtona_ja":     False,
                    # "artistissa":    artistinnimessa,
                    # "biisissa":      artistinnimessa,
                    # "albumissa":     artistinnimessa,
                    # "tiedostossa":   artistinnimessa
                    # "raitanumero":   (1,3)
                    }
        if not hakutermit:
            hakudikti = {}
        return hakudikti
