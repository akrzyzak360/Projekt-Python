import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QListWidget, QStackedWidget)
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

class Rura:
    def __init__(self, punkty, grubosc=12, kolor=Qt.gray):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255)
        self.czy_plynie = False

    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie

    def draw(self, painter):
        if len(self.punkty) < 2:
            return

        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        painter.setPen(QPen(self.kolor_rury, self.grubosc,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        if self.czy_plynie:
            painter.setPen(QPen(self.kolor_cieczy, self.grubosc - 4,
                                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(path)

class Zbiornik:
    def __init__(self, x, y, width=100, height=140, nazwa=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0

    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.poziom = self.aktualna_ilosc / self.pojemnosc
        return dodano

    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.poziom = self.aktualna_ilosc / self.pojemnosc
        return usunieto

    def czy_pusty(self):
        return self.aktualna_ilosc <= 0.1

    def czy_pelny(self):
        return self.aktualna_ilosc >= self.pojemnosc - 0.1

    def punkt_gora_srodek(self):
        return (self.x + self.width / 2, self.y)

    def punkt_dol_srodek(self):
        return (self.x + self.width / 2, self.y + self.height)

    def draw(self, painter):
        if self.poziom > 0:
            h = self.height * self.poziom
            painter.setBrush(QColor(0, 120, 255, 200))
            painter.setPen(Qt.NoPen)
            painter.drawRect(
                int(self.x + 3),
                int(self.y + self.height - h),
                int(self.width - 6),
                int(h)
            )

        painter.setPen(QPen(Qt.white, 4))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height)
        )
        painter.setPen(Qt.white)
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)

class EkranInstalacji(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color:black;")

        self.z1 = Zbiornik(60, 50, nazwa="Z1")
        self.z1.aktualna_ilosc = 100
        self.z1.poziom = 1.0

        self.z2 = Zbiornik(320, 200, nazwa="Z2")
        self.z3 = Zbiornik(580, 350, nazwa="Z3")
        self.z4 = Zbiornik(320, 540, nazwa="Z4")

        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]

        self._init_rury()

        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_przeplywu)

        self.running = False
        self.flow_speed = 0.8

    def _init_rury(self):
        def rura(a, b):
            mid = (a[1] + b[1]) / 2
            return Rura([a, (a[0], mid), (b[0], mid), b])

        self.rura1 = rura(self.z1.punkt_dol_srodek(), self.z2.punkt_gora_srodek())
        self.rura2 = rura(self.z2.punkt_dol_srodek(), self.z3.punkt_gora_srodek())
        self.rura3 = rura(self.z3.punkt_dol_srodek(), self.z4.punkt_gora_srodek())

        self.rury = [self.rura1, self.rura2, self.rura3]

    def start_stop(self):
        if self.running:
            self.timer.stop()
        else:
            self.timer.start(20)
        self.running = not self.running

    def napelnij(self, zb):
        zb.aktualna_ilosc = zb.pojemnosc
        zb.poziom = 1.0
        self.update()

    def oproznij(self, zb):
        zb.aktualna_ilosc = 0.0
        zb.poziom = 0.0
        self.update()

    def logika_przeplywu(self):
        for r in self.rury:
            r.ustaw_przeplyw(False)

        if not self.z1.czy_pusty() and not self.z2.czy_pelny():
            ilosc = self.z1.usun_ciecz(self.flow_speed)
            self.z2.dodaj_ciecz(ilosc)
            self.rura1.ustaw_przeplyw(True)

        if self.z2.poziom >= 0.3 and not self.z3.czy_pelny():
            ilosc = self.z2.usun_ciecz(self.flow_speed)
            self.z3.dodaj_ciecz(ilosc)
            self.rura2.ustaw_przeplyw(True)

        if self.z3.poziom >= 0.3 and not self.z4.czy_pelny():
            ilosc = self.z3.usun_ciecz(self.flow_speed)
            self.z4.dodaj_ciecz(ilosc)
            self.rura3.ustaw_przeplyw(True)

        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        for r in self.rury:
            r.draw(p)
        for z in self.zbiorniki:
            z.draw(p)

class EkranRaportow(QWidget):
    def __init__(self, ekran):
        super().__init__()
        self.ekran = ekran
        self.setStyleSheet("background-color:black; color:white;")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("RAPORT – POZIOMY ZBIORNIKÓW"))

        self.lista = QListWidget()
        self.lista.setStyleSheet("background-color:#111; color:white;")
        layout.addWidget(self.lista)

        self.timer = QTimer()
        self.timer.timeout.connect(self.aktualizuj)
        self.timer.start(500)

    def aktualizuj(self):
        self.lista.clear()
        for z in self.ekran.zbiorniki:
            self.lista.addItem(
                f"{z.nazwa}: {z.aktualna_ilosc:.1f} / {z.pojemnosc} "
                f"({z.poziom*100:.0f}%)"
            )

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projekt Python - Adam Krzyżanowski s199222")
        self.setFixedSize(1000, 820)
        self.setStyleSheet("background-color:black;")

        self.stack = QStackedWidget(self)
        self.stack.setGeometry(0, 0, 1000, 700)

        self.ekran_inst = EkranInstalacji()
        self.ekran_rap = EkranRaportow(self.ekran_inst)

        self.stack.addWidget(self.ekran_inst)
        self.stack.addWidget(self.ekran_rap)

        def styl(btn):
            btn.setStyleSheet(
                "QPushButton { background:#444; color:white; "
                "border:1px solid #777; font-weight:bold; }"
                "QPushButton:pressed { background:#666; }"
            )

        btn = QPushButton("Start / Stop", self)
        btn.setGeometry(50, 710, 120, 30)
        btn.clicked.connect(self.ekran_inst.start_stop)
        styl(btn)

        y = 710
        for i, z in enumerate(self.ekran_inst.zbiorniki):
            b1 = QPushButton(f"{z.nazwa} [+]", self)
            b1.setGeometry(220 + i*150, y, 60, 30)
            b1.clicked.connect(lambda _, zb=z: self.ekran_inst.napelnij(zb))
            styl(b1)

            b2 = QPushButton(f"{z.nazwa} [-]", self)
            b2.setGeometry(285 + i*150, y, 60, 30)
            b2.clicked.connect(lambda _, zb=z: self.ekran_inst.oproznij(zb))
            styl(b2)

        b_inst = QPushButton("Zbiorniki", self)
        b_inst.setGeometry(50, 760, 120, 30)
        b_inst.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        styl(b_inst)

        b_rap = QPushButton("Raporty", self)
        b_rap.setGeometry(220, 760, 120, 30)
        b_rap.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        styl(b_rap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
