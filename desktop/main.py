import sys
from PySide6.QtWidgets import QApplication, QDialog
from api_client import ApiClient
from login_window import LoginWindow
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    api = ApiClient()
    login = LoginWindow(api)
    if login.exec() == QDialog.Accepted:
        window = MainWindow(api)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
