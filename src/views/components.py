"""
Smart Medical AI - Custom UI Components
Composants Senior pour une interface Premium
"""

import os
from ..utils.qt_compat import QtWidgets, QtCore, QtGui


class AvatarLabel(QtWidgets.QLabel):
    """Widget pour afficher une photo de profil circulaire"""
    def __init__(self, size=40, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.size = size
        self.setObjectName("avatar_label")

    def set_photo(self, image_path=None):
        if image_path and os.path.exists(image_path):
            pixmap = QtGui.QPixmap(image_path)
        else:
            pixmap = QtGui.QPixmap(self.size, self.size)
            pixmap.fill(QtGui.QColor("#1890ff"))

        target = QtGui.QPixmap(self.size, self.size)
        target.fill(QtCore.Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(target)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        path = QtGui.QPainterPath()
        path.addEllipse(0, 0, self.size, self.size)
        painter.setClipPath(path)

        painter.drawPixmap(
            0, 0,
            pixmap.scaled(
                self.size, self.size,
                QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
        )
        # White border ring for premium look
        self.setStyleSheet(f"border: 2.5px solid white; border-radius: {self.size//2}px; background-color: #1890ff;")
        
        painter.end()
        self.setPixmap(target)


class KPICard(QtWidgets.QFrame):
    """
    Carte KPI réutilisable affichant un indicateur chiffré.

    Paramètres:
        title   — Label en haut (ex: "Patients du jour")
        value   — Valeur principale (ex: "12")
        sub     — Sous-titre (ex: "Aujourd'hui")
        color   — Couleur accent HEX (ex: "#1890ff")
        icon    — Emoji ou caractère optionnel (ex: "📊")
    """

    def __init__(self, title: str, value: str, sub: str = "",
                 color: str = "#1890ff", icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("KPICard")
        self.setFixedHeight(110)
        self.setMinimumWidth(160)
        self.setStyleSheet(f"""
            QFrame#KPICard {{
                background-color: white;
                border-radius: 22px;
                border: 1px solid {color}25;
            }}
            QFrame#KPICard:hover {{
                border: 2px solid {color};
                background-color: {color}08;
            }}
        """)

        # Modern Shadow Effect
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QtGui.QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        # Ligne titre + icône
        header = QtWidgets.QHBoxLayout()
        lbl_title = QtWidgets.QLabel(title)
        lbl_title.setObjectName("kpi_title")
        header.addWidget(lbl_title)
        header.addStretch()
        if icon:
            lbl_icon = QtWidgets.QLabel(icon)
            lbl_icon.setObjectName("kpi_icon")
            header.addWidget(lbl_icon)
        layout.addLayout(header)

        # Valeur principale
        lbl_value = QtWidgets.QLabel(value)
        lbl_value.setObjectName("kpi_value")
        layout.addWidget(lbl_value)

        # Sous-titre
        if sub:
            lbl_sub = QtWidgets.QLabel(sub)
            lbl_sub.setObjectName("kpi_sub")
            layout.addWidget(lbl_sub)

        layout.addStretch()

class PulseLabel(QtWidgets.QLabel):
    """Label avec animation de pulsation (opacité) pour les alertes IA"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(1500)
        self.anim.setStartValue(0.4)
        self.anim.setEndValue(1.0)
        self.anim.setLoopCount(-1) # Infinite
        self.anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)
        self.anim.start()

    def set_alert(self, is_alert: bool):
        if is_alert:
            self.setProperty("class", "danger_text")
            self.style().unpolish(self)
            self.style().polish(self)
            if self.anim.state() == QtCore.QPropertyAnimation.State.Stopped:
                self.anim.start()
        else:
            self.setProperty("class", "primary_text") # I should add this class to ThemeManager
            self.style().unpolish(self)
            self.style().polish(self)
            self.anim.stop()
            self.setWindowOpacity(1.0)
