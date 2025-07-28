from sys import argv, exit, platform
from os import environ
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSizePolicy,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QMouseEvent, QIcon
from form_credencial import *
from credenciais import load_url

# ========================================================
# CONFIGURAÇÕES GLOBAIS ANTES DE CRIAR QApplication
# ========================================================
# URL centralizada
URL_TSPLUS = load_url()

# Configurações específicas por SO
is_windows = platform.startswith('win')
is_linux = platform.startswith('linux')

# Configurações críticas ANTES da criação do QApplication
if is_linux:
    environ["QT_XCB_FORCE_SOFTWARE_OPENGL"] = "1"  # Força software
    environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-seccomp-filter-sandbox --disable-gpu"
    QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
elif is_windows:
    # Otimizações para Windows
    environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--enable-gpu-rasterization "
        "--ignore-gpu-blocklist "
        "--enable-zero-copy"
    )
    environ["QT_OPENGL"] = "angle"

# Configurações comuns para ambos os SOs
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
environ["QTWEBENGINE_DISABLE_GPU_SHADER_DISK_CACHE"] = "1"


# ========================================================
# CLASSES DA APLICAÇÃO
# ========================================================
class MeuWebEngineView(QWebEngineView):
    """Subclasse customizada para manipular abertura de novas janelas"""

    def createWindow(self, _type):
        return self  # Mantém todas as abas na mesma janela

    def contextMenuEvent(self, event):
        """Desabilita menu de contexto para melhor experiência"""
        event.ignore()


class BarraSuperior(QWidget):
    """Barra de título personalizada com controles de janela"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setFixedHeight(28 if is_windows else 32)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("background-color: #222; ")

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)

        self.titulo = QLabel("TSplus Belenzier")
        self.titulo.setStyleSheet(
            "font-weight: bold; font-size: 11px; padding: 0;")
        layout.addWidget(self.titulo)

        layout.addStretch(1)

        # Botões de controle
        self.btn_credenciais = QPushButton("🔑 Credenciais")
        self.btn_tela_cheia = QPushButton("□")
        self.btn_minimizar = QPushButton("—")
        self.btn_fechar = QPushButton("✕")

        # Estilo dos botões
        btn_style = """
            QPushButton {
                background-color: #444;
                border: none;
                color: white;
                font-weight: bold;
                min-width: 24px;
                min-height: 24px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #666; }
            QPushButton:pressed { background-color: #888; }
        """
        self.btn_credenciais.setStyleSheet(
            btn_style + "font-size: 10px; padding: 0 8px;")
        self.btn_tela_cheia.setStyleSheet(btn_style)
        self.btn_minimizar.setStyleSheet(btn_style)
        self.btn_fechar.setStyleSheet(btn_style + "background-color: #e81123;")

        layout.addWidget(self.btn_credenciais)
        layout.addWidget(self.btn_tela_cheia)
        layout.addWidget(self.btn_minimizar)
        layout.addWidget(self.btn_fechar)

        self.setLayout(layout)

        # Conexões
        self.btn_fechar.clicked.connect(self.main_window.close)
        self.btn_minimizar.clicked.connect(self.main_window.showMinimized)
        self.btn_tela_cheia.clicked.connect(self.toggle_tela_cheia)
        self.btn_credenciais.clicked.connect(
            self.main_window.show_credentials_dialog)

        # Timer para detecção de duplo clique
        self.double_click_timer = QTimer()
        # 300ms para considerar duplo clique
        self.double_click_timer.setInterval(300)
        self.double_click_timer.setSingleShot(True)
        self.double_click_timer.timeout.connect(self.reset_click_count)
        self.click_count = 0

    def mousePressEvent(self, event):
        """Detecta duplo clique na barra superior"""
        if event.button() == Qt.LeftButton:
            self.click_count += 1

            if self.click_count == 1:
                self.double_click_timer.start()
            elif self.click_count == 2:
                self.toggle_maximized()
                self.click_count = 0
                self.double_click_timer.stop()
        super().mousePressEvent(event)

    def reset_click_count(self):
        """Reseta o contador de cliques"""
        self.click_count = 0

    def toggle_maximized(self):
        """Alterna entre tela maximizada e normal"""
        if self.main_window.isMaximized():  #
            self.main_window.showNormal()
        else:
            self.main_window.showMaximized()

    def toggle_tela_cheia(self):
        """Alterna entre modo tela cheia e normal"""
        if self.main_window.isFullScreen():
            self.main_window.showNormal()
            self.btn_tela_cheia.setText("□")
        else:
            self.main_window.showFullScreen()
            self.btn_tela_cheia.setText("🗗")

    def fullscreen(self):
        if self.parent.isFullScreen():
            return True
        return False


class NavegadorTSPlus(QMainWindow):
    """Janela principal do navegador TSplus"""

    def __init__(self):
        super().__init__()
        # Flags modificadas para melhor comportamento
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # Remove bordas
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint  # Permite minimização
        )

        # Configuração adicional para comportamento correto na barra de tarefas
        self.setWindowIcon(
            QIcon('C:\\Users\\Ti Belenzier\\Desktop\\workspace\\NavegadorTS\\conexao.ico'))
        self.setWindowTitle("TSplus Belenzier")  # Título visível na barra

        # Criação do navegador
        self.browser = MeuWebEngineView()
        self.browser.loadFinished.connect(self.on_page_loaded)
        self.browser.setUrl(QUrl(URL_TSPLUS))

        # Configurações de desempenho
        self.configurar_desempenho_navegador()

        # Barra superior personalizada
        self.barra = BarraSuperior(self)

        # Layout principal
        container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.barra)
        main_layout.addWidget(self.browser, 1)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Variáveis para controle de estado
        self.was_maximized = False
        self.current_screen = None

    def on_page_loaded(self, ok):
        """Executa após o carregamento da página"""
        if ok:
            # Tentativa de preenchimento com retry progressivo
            self.tentar_preenchimento_automatico(
                tentativas=1, delay_inicial=250)

    def tentar_preenchimento_automatico(self, tentativas, delay_inicial):
        """Tenta preencher credenciais com múltiplas tentativas"""
        if tentativas > 0:
            QTimer.singleShot(
                delay_inicial, lambda: self.executar_autofill(tentativas))
        else:
            print("Autopreenchimento falhou após todas as tentativas")

    def executar_autofill(self, tentativas_restantes):
        """Executa o código JavaScript para preenchimento"""
        credenciais = load_credentials()
        if not credenciais:
            return

        js_code = f"""

        let preencherCredenciais = () => {{
            let userField = document.getElementById('Editbox1');
            let passField = document.getElementById('Editbox2');
            
            if (userField && passField) {{
                // Preencher usuário
                userField.value = '{credenciais['usuario']}';
                ['input', 'change', 'blur'].forEach(ev => {{
                    userField.dispatchEvent(new Event(ev, {{bubbles: true}}));
                }});
                
                // Preencher senha após pequeno delay
                setTimeout(() => {{
                    passField.value = '{credenciais['senha']}';
                    ['input', 'change', 'blur'].forEach(ev => {{
                        passField.dispatchEvent(new Event(ev, {{bubbles: true}}));
                    }});
                }}, 250);
                return true;
            }}
            return false;
        }};
        preencherCredenciais();

    
        """
        url_atual = self.browser.url().toString()
        if url_atual == "http://10.0.10.27/":
            self.browser.page().runJavaScript(js_code, lambda sucesso:
                                              self.tratar_resultado_autofill(
                                                  sucesso, tentativas_restantes)
                                              )

    def tratar_resultado_autofill(self, sucesso, tentativas_restantes):
        """Trata o resultado da tentativa de autopreenchimento"""
        if not sucesso and tentativas_restantes > 1:
            # Aumenta delay progressivamente
            novo_delay = 500 * (1 - tentativas_restantes)
            self.tentar_preenchimento_automatico(
                tentativas_restantes - 1, novo_delay)

    def show_credentials_dialog(self):
        """Mostra o diálogo de gerenciamento de credenciais"""
        dialog = CredentialsDialog(self)
        if credenciais := load_credentials():
            dialog.username_input.setText(credenciais['usuario'])
            dialog.password_input.setText(credenciais['senha'])
        dialog.exec()

    def configurar_desempenho_navegador(self):
        """Configurações otimizadas para TS Plus com RDP"""
        settings = self.browser.settings()
        profile = QWebEngineProfile.defaultProfile()

        # Configurações ESSENCIAIS para RDP
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(
            QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(
            QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(
            QWebEngineSettings.PlaybackRequiresUserGesture, False)
        settings.setAttribute(
            QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)

        # Otimizações avançadas
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
        settings.setAttribute(
            QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, False)

        # Configurações de cache
        profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.NoPersistentCookies)
        profile.setCachePath(environ.get("XDG_CACHE_HOME", "/tmp"))

        # Configura o user agent para compatibilidade
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )

        # Configurações específicas para Linux
        if is_linux:
            settings.setAttribute(
                QWebEngineSettings.Accelerated2dCanvasEnabled, False)

    def showEvent(self, event):
        """Mostra a janela maximizada após a inicialização"""
        super().showEvent(event)
        if not hasattr(self, '_maximized_initialized'):
            self.maximize_on_current_screen()
            self._maximized_initialized = True

    def maximize_on_current_screen(self):
        """Maximiza a janela no monitor atual"""
        self.current_screen = self.screen()
        self.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        """Captura posição inicial do arrasto e trata restauração"""
        if event.button() == Qt.LeftButton:
            # Verifica se o clique foi na barra superior
            if self.barra.geometry().contains(event.position().toPoint()):
                # Se estava maximizado, restaura ao tamanho normal
                if self.isMaximized():
                    self.was_maximized = True
                    self.showNormal()

                    # Posiciona a janela sob o cursor
                    cursor_pos = event.globalPosition().toPoint()
                    title_bar_height = self.barra.height()

                    # Calcula a posição correta relativa ao cursor
                    x = cursor_pos.x() - (self.width() / 2)
                    y = cursor_pos.y() - (title_bar_height / 2)

                    # Limita às bordas da tela
                    screen_geo = self.screen().availableGeometry()
                    x = max(screen_geo.left(), min(
                        x, screen_geo.right() - self.width()))
                    y = max(screen_geo.top(), min(
                        y, screen_geo.bottom() - self.height()))

                    self.move(int(x), int(y))

                # Atualiza posição de arrasto
                self.drag_start_position = event.globalPosition().toPoint()
                self.drag_window_position = self.pos()
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Move a janela e verifica mudança de monitor"""
        if hasattr(self, 'drag_start_position'):
            # Verifica se mudou de monitor durante o arrasto
            cursor_screen = QApplication.screenAt(
                event.globalPosition().toPoint())

            if cursor_screen and cursor_screen != self.current_screen:
                self.current_screen = cursor_screen
                if self.was_maximized:
                    self.was_maximized = False

            # Move a janela normalmente
            if not self.isMaximized() and not self.isFullScreen():
                delta = event.globalPosition().toPoint() - self.drag_start_position
                self.move(self.drag_window_position + delta)

            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Finaliza o arrasto e maximiza se necessário"""
        if hasattr(self, 'drag_start_position'):
            # Verifica se deve restaurar estado maximizado
            if self.was_maximized:
                self.was_maximized = False
                self.showMaximized()

            del self.drag_start_position
        event.accept()


# ========================================================
# PONTO DE ENTRADA PRINCIPAL
# ========================================================
if __name__ == "__main__":
    app = QApplication(argv)
    app.setStyle("Fusion")  # Estilo visual consistente

    # Configuração de fallback para Linux
    if is_linux:
        environ["QT_QPA_PLATFORM"] = "xcb"
        app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)

    janela = NavegadorTSPlus()
    janela.show()
    exit(app.exec())
