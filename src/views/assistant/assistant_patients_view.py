from ...utils.qt_compat import QtWidgets, QtCore
from ..patient_view import PatientListView

class AssistantPatientsView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Réutilisation de la liste de patients (RBAC géré à l'intérieur)
        self.patient_list = PatientListView()
        layout.addWidget(self.patient_list)
