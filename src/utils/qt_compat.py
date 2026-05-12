"""
Smart Medical AI - Qt Compatibility Layer (V3 - Fix White Screen)
Gère la bascule automatique entre PyQt6 et PySide6 avec support visuel complet
"""

import sys
import os

try:
    from PyQt6 import QtWidgets, QtCore, QtGui, uic
    QT_LIB = "PyQt6"
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui, QtUiTools
        QT_LIB = "PySide6"
        
        class uic:
            @staticmethod
            def loadUi(ui_path, base_instance):
                """Simulation robuste de uic.loadUi pour PySide6 avec fix visuel"""
                loader = QtUiTools.QUiLoader()
                ui_file = QtCore.QFile(ui_path)
                if not ui_file.open(QtCore.QFile.ReadOnly):
                    print(f"ERREUR: Impossible d'ouvrir {ui_path}")
                    return None
                
                # Charger l'UI. On ne passe pas base_instance au load() 
                # pour éviter les conflits de parentage
                ui_widget = loader.load(ui_file)
                ui_file.close()
                
                if ui_widget is None:
                    print(f"ERREUR: Échec du chargement de {ui_path}")
                    return None

                # 1. Créer un layout sur l'instance de base s'il n'existe pas
                if base_instance.layout() is None:
                    layout = QtWidgets.QVBoxLayout(base_instance)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.addWidget(ui_widget)
                else:
                    base_instance.layout().addWidget(ui_widget)

                # 2. Injecter tous les enfants dans base_instance
                # Cela permet d'utiliser self.nomDuBouton
                for child in ui_widget.findChildren(QtCore.QObject):
                    name = child.objectName()
                    if name:
                        setattr(base_instance, name, child)
                
                # 3. Transférer les propriétés de base (titre, taille)
                base_instance.setWindowTitle(ui_widget.windowTitle())
                if ui_widget.minimumSize():
                    base_instance.setMinimumSize(ui_widget.minimumSize())
                
                return ui_widget
    except ImportError:
        print("ERREUR: Ni PyQt6 ni PySide6 n'est installé.")
        sys.exit(1)

# Compatibility aliases for Signals and Slots
if 'QT_LIB' in globals():
    if QT_LIB == "PyQt6":
        QtCore.Signal = QtCore.pyqtSignal
        QtCore.Slot = QtCore.pyqtSlot
    elif QT_LIB == "PySide6":
        # PySide6 already uses Signal and Slot
        pass

print(f"[Qt] Moteur de rendu: {QT_LIB} | Fix visuel activé")
os.environ["PYQTGRAPH_QT_LIB"] = QT_LIB

# Configuration globale pour éviter les conflits de QPainter sur Windows/PySide6
if "QtCore" in globals():
    # Éviter les conflits de painting entre widgets parents/enfants
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
    # Support haute résolution
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
