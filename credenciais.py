import configparser
from pathlib import Path
import os
import sys


def get_credentials_path():
    """Retorna o caminho no mesmo diretório do executável"""
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).parent

    ini_path = app_dir / "tsplus_credentials.ini"
    return str(ini_path)


def save_credentials(username, password):
    """Salva ou atualiza as credenciais no arquivo INI"""
    config = configparser.ConfigParser()
    path = get_credentials_path()
    config.read(path)  # Lê dados existentes, se houver

    if not config.has_section('acesso'):
        config.add_section('acesso')

    config.set('acesso', 'usuario', username)
    config.set('acesso', 'senha', password)

    try:
        with open(path, 'w') as configfile:
            config.write(configfile)
        print("Credenciais salvas com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao salvar credenciais: {e}")
        return False


def save_url(url):
    """Salva ou atualiza a URL no arquivo INI"""
    config = configparser.ConfigParser()
    path = get_credentials_path()
    config.read(path)  # Lê dados existentes, se houver

    if not config.has_section('url'):
        config.add_section('url')

    config.set('url', 'url', url)

    try:
        with open(path, 'w') as configfile:
            config.write(configfile)
        print("URL salva com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao salvar URL: {e}")
        return False


def load_credentials():
    """Carrega as credenciais do arquivo INI"""
    path = get_credentials_path()
    if not os.path.exists(path):
        print("Arquivo de credenciais não encontrado")
        return None

    config = configparser.ConfigParser()
    try:
        config.read(path)

        usuario = config.get('acesso', 'usuario', fallback='')
        senha = config.get('acesso', 'senha', fallback='')
        url = config.get('url', 'url', fallback='')

        if not usuario or not senha:
            return None

        return {'usuario': usuario, 'senha': senha, 'url': url}
    except Exception as e:
        print(f"Erro ao ler arquivo INI: {e}")
        return None


def load_url():
    """Carrega apenas a URL"""
    path = get_credentials_path()
    if not os.path.exists(path):
        print("Arquivo de credenciais não encontrado")
        return None

    config = configparser.ConfigParser()
    try:
        config.read(path)
        return config.get('url', 'url', fallback=None)
    except Exception as e:
        print(f"Erro ao ler arquivo INI: {e}")
        return None
