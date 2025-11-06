from PyQt5 import QtWidgets, QtCore

class UserDashboard(QtWidgets.QMainWindow):
    def __init__(self, username="user"):
        super().__init__()
        self.setWindowTitle("Crypto Insight — User Dashboard")
        self.resize(760, 480)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        layout = QtWidgets.QVBoxLayout(central)

        title = QtWidgets.QLabel(f"Hai, {username}! 🚀")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: 700; margin: 12px 0;")
        layout.addWidget(title)

        info = QtWidgets.QLabel("Ini adalah halaman User Dashboard.\nContoh fitur: lihat harga crypto, berita terbaru, dan portofolio.")
        info.setAlignment(QtCore.Qt.AlignCenter)
        info.setStyleSheet("font-size: 14px;")
        layout.addWidget(info)

        self.logout_btn = QtWidgets.QPushButton("Logout")
        self.logout_btn.setFixedHeight(42)
        layout.addWidget(self.logout_btn, alignment=QtCore.Qt.AlignCenter)
