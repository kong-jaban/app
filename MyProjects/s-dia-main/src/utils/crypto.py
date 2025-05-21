import os
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import logging
import winreg
import platform
from pathlib import Path

class SecretStorage:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_windows = platform.system().lower() == 'windows'
        
        if self.is_windows:
            self.reg_path = r"Software\UPSDATA\S-DIA"
        else:
            self.env_path = os.path.expanduser('~/.upsdata/s-dia/.env')
            os.makedirs(os.path.dirname(self.env_path), exist_ok=True)

    def save_secrets(self, iv, salt):
        """IV와 Salt를 저장합니다."""
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        
        if self.is_windows:
            try:
                key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, self.reg_path, 0, 
                                       winreg.KEY_WRITE)
                winreg.SetValueEx(key, "iv", 0, winreg.REG_SZ, iv_b64)
                winreg.SetValueEx(key, "salt", 0, winreg.REG_SZ, salt_b64)
                winreg.CloseKey(key)
            except Exception as e:
                self.logger.error(f"레지스트리 저장 중 오류: {str(e)}")
                raise
        else:
            try:
                # 기존 .env 파일 내용 읽기
                env_dict = self._read_env_file()
                # IV와 Salt 업데이트
                env_dict['IV'] = iv_b64
                env_dict['SALT'] = salt_b64
                # 파일 저장
                self._save_env_file(env_dict)
            except Exception as e:
                self.logger.error(f".env 파일 저장 중 오류: {str(e)}")
                raise

    def load_secrets(self):
        """저장된 IV와 Salt를 로드합니다."""
        if self.is_windows:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0,
                                   winreg.KEY_READ)
                iv_b64 = winreg.QueryValueEx(key, "iv")[0]
                salt_b64 = winreg.QueryValueEx(key, "salt")[0]
                winreg.CloseKey(key)
                return (base64.b64decode(iv_b64), base64.b64decode(salt_b64))
            except FileNotFoundError:
                return None, None
            except Exception as e:
                self.logger.error(f"레지스트리 로드 중 오류: {str(e)}")
                raise
        else:
            try:
                env_dict = self._read_env_file()
                if 'IV' in env_dict and 'SALT' in env_dict:
                    return (base64.b64decode(env_dict['IV']),
                           base64.b64decode(env_dict['SALT']))
                return None, None
            except Exception as e:
                self.logger.error(f".env 파일 로드 중 오류: {str(e)}")
                raise

    def save_window_state(self, x, y, width, height, is_maximized):
        """창 상태를 저장합니다."""
        try:
            if self.is_windows:
                key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, self.reg_path, 0,
                                       winreg.KEY_WRITE)
                # 모든 값을 문자열로 저장
                winreg.SetValueEx(key, "window_x", 0, winreg.REG_SZ, str(x))
                winreg.SetValueEx(key, "window_y", 0, winreg.REG_SZ, str(y))
                winreg.SetValueEx(key, "window_width", 0, winreg.REG_SZ, str(width))
                winreg.SetValueEx(key, "window_height", 0, winreg.REG_SZ, str(height))
                winreg.SetValueEx(key, "window_maximized", 0, winreg.REG_DWORD, 1 if is_maximized else 0)
                winreg.CloseKey(key)
            else:
                env_dict = self._read_env_file()
                env_dict.update({
                    'WINDOW_X': str(x),
                    'WINDOW_Y': str(y),
                    'WINDOW_WIDTH': str(width),
                    'WINDOW_HEIGHT': str(height),
                    'WINDOW_MAXIMIZED': '1' if is_maximized else '0'
                })
                self._save_env_file(env_dict)
        except Exception as e:
            self.logger.error(f"창 상태 저장 중 오류: {str(e)}")
            raise

    def load_window_state(self):
        """저장된 창 상태를 로드합니다."""
        try:
            if self.is_windows:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0,
                                       winreg.KEY_READ)
                    # 문자열로 저장된 값을 정수로 변환
                    x = int(winreg.QueryValueEx(key, "window_x")[0])
                    y = int(winreg.QueryValueEx(key, "window_y")[0])
                    width = int(winreg.QueryValueEx(key, "window_width")[0])
                    height = int(winreg.QueryValueEx(key, "window_height")[0])
                    is_maximized = bool(winreg.QueryValueEx(key, "window_maximized")[0])
                    winreg.CloseKey(key)
                    return x, y, width, height, is_maximized
                except FileNotFoundError:
                    return None
            else:
                env_dict = self._read_env_file()
                if all(key in env_dict for key in ['WINDOW_X', 'WINDOW_Y', 'WINDOW_WIDTH', 'WINDOW_HEIGHT', 'WINDOW_MAXIMIZED']):
                    return (
                        int(env_dict['WINDOW_X']),
                        int(env_dict['WINDOW_Y']),
                        int(env_dict['WINDOW_WIDTH']),
                        int(env_dict['WINDOW_HEIGHT']),
                        env_dict['WINDOW_MAXIMIZED'] == '1'
                    )
                return None
        except Exception as e:
            self.logger.error(f"창 상태 로드 중 오류: {str(e)}")
            return None

    def _read_env_file(self):
        """환경 설정 파일을 읽습니다."""
        env_dict = {}
        if os.path.exists(self.env_path):
            with open(self.env_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_dict[key] = value
        return env_dict

    def _save_env_file(self, env_dict):
        """환경 설정 파일을 저장합니다."""
        with open(self.env_path, 'w') as f:
            for key, value in env_dict.items():
                f.write(f"{key}={value}\n")

class CryptoUtil:
    def __init__(self, password):
        self.password = password.encode('utf-8')
        self.logger = logging.getLogger(__name__)
        self.secret_storage = SecretStorage()
        
    def _derive_key(self, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256 키 길이
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(self.password)
        
    def encrypt_data(self, data):
        # 저장된 IV와 Salt 로드 시도
        iv, salt = self.secret_storage.load_secrets()
        
        # 저장된 값이 없으면 새로 생성
        if iv is None or salt is None:
            salt = os.urandom(16)
            iv = os.urandom(16)
            # 새로 생성한 IV와 Salt 저장
            self.secret_storage.save_secrets(iv, salt)
        
        key = self._derive_key(salt)
        
        # AES-256 암호화 (CBC 모드)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # PKCS7 패딩 적용
        padded_data = pad(data, AES.block_size)
        
        # 데이터 암호화
        encrypted_data = cipher.encrypt(padded_data)
        
        return {
            'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8')
        }
        
    def decrypt_data(self, encrypted_dict):
        # 저장된 IV와 Salt 로드
        iv, salt = self.secret_storage.load_secrets()
        if iv is None or salt is None:
            raise ValueError("IV와 Salt를 찾을 수 없습니다.")
            
        encrypted_data = base64.b64decode(encrypted_dict['encrypted_data'])
        
        key = self._derive_key(salt)
        
        # AES-256 복호화 (CBC 모드)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = cipher.decrypt(encrypted_data)
        
        # PKCS7 패딩 제거
        return unpad(padded_data, AES.block_size)
        
    def save_encrypted_data(self, data, filepath):
        # 데이터를 JSON 문자열로 변환
        json_data = json.dumps(data).encode('utf-8')
        
        # 데이터 암호화
        encrypted_dict = self.encrypt_data(json_data)
        
        # 파일 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 암호화된 데이터를 파일에 저장
        with open(filepath, 'w') as f:
            json.dump(encrypted_dict, f)
            
    def load_encrypted_data(self, filepath):
        try:
            # 암호화된 데이터를 파일에서 읽기
            with open(filepath, 'r') as f:
                encrypted_dict = json.load(f)
                
            # 데이터 복호화
            decrypted_data = self.decrypt_data(encrypted_dict)
            
            # JSON 문자열을 파이썬 객체로 변환
            return json.loads(decrypted_data)
        except FileNotFoundError:
            self.logger.info(f"{filepath} 파일이 없습니다. 기본 정보로 생성합니다.")
            default_data = {
                "user_id": "admin",
                "password": "admin",
                "name": "관리자",
                "email": "admin@example.com",
                "role": "admin",
                "created_at": "",
                "last_login": ""
            }
            self.save_encrypted_data(default_data, filepath)
            return default_data
        except Exception as e:
            self.logger.error(f"데이터 로드 중 오류 발생: {str(e)}")
            raise 