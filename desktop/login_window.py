from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout

class LoginWindow(QDialog):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.setWindowTitle("Login")
        self.setFixedSize(300, 180)
        
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        layout.addWidget(self.error_label)
        
        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.do_login)
        btn_layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.do_register)
        btn_layout.addWidget(self.register_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def do_login(self):
        user = self.username_input.text()
        pwd = self.password_input.text()
        try:
            self.api_client.login(user, pwd)
            self.accept()
        except Exception:
            self.error_label.setStyleSheet("color: red;")
            self.error_label.setText("Login failed: invalid credentials")

    def do_register(self):
        user = self.username_input.text()
        pwd = self.password_input.text()
        try:
            self.api_client.register(user, pwd)
            self.error_label.setStyleSheet("color: green;")
            self.error_label.setText("Registered! Please login")
        except Exception:
            self.error_label.setStyleSheet("color: red;")
            self.error_label.setText("Registration failed")
