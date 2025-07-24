from PySide6.QtWidgets import (QDialog, QLineEdit, QPushButton,
                               QVBoxLayout, QLabel, QMessageBox)
from credenciais import save_credentials, load_credentials, save_url


class CredentialsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciar Credenciais TSPlus")
        self.setFixedSize(300, 300)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Título
        self.label = QLabel("Cadastre suas credenciais de acesso:")
        layout.addWidget(self.label)

        # Campo de usuário
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Digite seu usuário")
        layout.addWidget(QLabel("Usuário:"))
        layout.addWidget(self.username_input)

        # Campo de senha
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.password_input)

        # Campo de senha
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Digite URL")
        layout.addWidget(QLabel("Url:"))
        layout.addWidget(self.url_input)

        # Botão de salvar
        self.save_button = QPushButton("Salvar Credenciais")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.save_button.clicked.connect(self.salvar_credenciais)
        layout.addWidget(self.save_button)

        # Carrega credenciais existentes
        self.carregar_credenciais_existentes()

        self.setLayout(layout)

    def carregar_credenciais_existentes(self):
        """Carrega credenciais salvas previamente"""
        credenciais = load_credentials()
        if credenciais:
            self.username_input.setText(credenciais['usuario'])
            self.password_input.setText(credenciais['senha'])
            self.url_input.setText(credenciais["url"])

    def salvar_credenciais(self):
        """Valida e salva as credenciais no arquivo INI"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        url = self.url_input.text().strip()

        if not username or not password:
            QMessageBox.warning(
                self, "Aviso", "Por favor, preencha ambos os campos!")
            return

        if save_credentials(username, password) and save_url(url=url):
            QMessageBox.information(self, "Sucesso",
                                    "Credenciais salvas com sucesso!\n")
            self.close()
        else:
            QMessageBox.critical(self, "Erro",
                                 "Não foi possível salvar as credenciais!\n"
                                 "Verifique as permissões do sistema.")
