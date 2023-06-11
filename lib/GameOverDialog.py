#!/usr/bin/env python3

from PyQt5.QtWidgets import QLabel,QDialog,QDialogButtonBox,QVBoxLayout
from PyQt5.QtCore import Qt
from lib.Utils import initialize_logger

class GameOverDialog(QDialog):
    def __init__(self,text,parent=None):
        super().__init__(parent)
        self.logger = initialize_logger()

        self.setWindowTitle("Game Over")
        self.setStyleSheet("font: 12pt;")

        QBtn = QDialogButtonBox.Yes | QDialogButtonBox.No

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        btns = self.buttonBox.buttons()
        btns[0].setDefault(True)
        btns[1].setDefault(False)

        self.layout = QVBoxLayout()
        message = QLabel(text)
        message.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
