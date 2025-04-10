import os
import json
import time
import sqlite3
import platform
import getpass
import keyring
import browser_cookie3
import webbrowser
import requests
import re
from pathlib import Path
from colorama import Fore, Style
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DigitalDetox:
    """DigitalDetox - A tool that helps you go truly offline by deleting your social media presence"""

    # ASCII Banner to display when the program starts
    BANNER = r"""
    ██████╗ ██╗ ██████╗ ██╗████████╗ █████╗ ██╗      ██████╗ ███████╗████████╗ ██████╗ ██╗  ██╗
    ██╔══██╗██║██╔════╝ ██║╚══██╔══╝██╔══██╗██║     ██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗╚██╗██╔╝
    ██║  ██║██║██║  ███╗██║   ██║   ███████║██║     ██║  ██║█████╗     ██║   ██║   ██║ ╚███╔╝ 
    ██║  ██║██║██║   ██║██║   ██║   ██╔══██║██║     ██║  ██║██╔══╝     ██║   ██║   ██║ ██╔██╗ 
    ██████╔╝██║╚██████╔╝██║   ██║   ██║  ██║███████╗██████╔╝███████╗   ██║   ╚██████╔╝██╔╝ ██╗
    ╚═════╝ ╚═╝ ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
                                                             Made by Nebulous
    """

    colored_banner = BANNER.replace(
    "Made by Nebulous",
    f"{Fore.CYAN + Style.BRIGHT}Made by Nebulous{Style.RESET_ALL}"
)
    # Credits and version
    VERSION = "1.0.0"
    CREDITS = "Created by Nebulous"
    colored_version = f"{Fore.YELLOW + Style.BRIGHT}{VERSION}{Style.RESET_ALL}"
    colored_credits = f"{Fore.CYAN + Style.BRIGHT}{CREDITS}{Style.RESET_ALL}"

    PLATFORMS = {
        "facebook": {
            "domains": ["facebook.com", "m.facebook.com"],
            "delete_url": "https://www.facebook.com/help/delete_account",
            "download_url": "https://www.facebook.com/dyi",
            "login_url": "https://www.facebook.com/login",
            "login_check": "https://www.facebook.com/me",
            "username_field": "email",
            "password_field": "pass",
            "submit_button": "//button[@name='login']",
            "profile_indicator": "//div[@role='navigation']//span[contains(text(), '')]",
        },
        "twitter": {
            "domains": ["twitter.com", "mobile.twitter.com", "x.com"],
            "delete_url": "https://twitter.com/settings/account/deactivate",
            "download_url": "https://twitter.com/settings/download_your_data",
            "login_url": "https://twitter.com/i/flow/login",
            "login_check": "https://twitter.com/home",
            "username_field": "//input[@autocomplete='username']",
            "password_field": "//input[@name='password']",
            "submit_button": "//div[@role='button'][.//span[text()='Log in']]",
            "profile_indicator": "//a[@aria-label='Profile']",
        },
        "instagram": {
            "domains": ["instagram.com", "www.instagram.com"],
            "delete_url": "https://www.instagram.com/accounts/remove/request/permanent/",
            "download_url": "https://www.instagram.com/download/request/",
            "login_url": "https://www.instagram.com/accounts/login/",
            "login_check": "https://www.instagram.com/",
            "username_field": "username",
            "password_field": "password",
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//a[contains(@href, '/') and .//img[contains(@alt, 'profile picture')]]",
        },
        "linkedin": {
            "domains": ["linkedin.com", "www.linkedin.com"],
            "delete_url": "https://www.linkedin.com/psettings/account-management/close-account",
            "download_url": "https://www.linkedin.com/psettings/member-data",
            "login_url": "https://www.linkedin.com/login",
            "login_check": "https://www.linkedin.com/feed/",
            "username_field": "username",
            "password_field": "password",
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//a[contains(@href, '/in/')]",
        },
        "reddit": {
            "domains": ["reddit.com", "www.reddit.com", "old.reddit.com"],
            "delete_url": "https://www.reddit.com/settings/account",
            "download_url": "https://www.reddit.com/settings/data-request",
            "login_url": "https://www.reddit.com/login/",
            "login_check": "https://www.reddit.com/",
            "username_field": "username",
            "password_field": "password",
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//span[contains(@class, 'Header') and contains(text(), 'u/')]",
        },
        "tiktok": {
            "domains": ["tiktok.com", "www.tiktok.com"],
            "delete_url": "https://www.tiktok.com/setting/delete-account",
            "download_url": "https://www.tiktok.com/setting/download-data",
            "login_url": "https://www.tiktok.com/login",
            "login_check": "https://www.tiktok.com/foryou",
            "username_field": "//input[@name='username']",
            "password_field": "//input[@type='password']",
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//div[contains(@class, 'UserIcon')]",
        },
        "pinterest": {
            "domains": ["pinterest.com", "www.pinterest.com"],
            "delete_url": "https://www.pinterest.com/settings/privacy",
            "download_url": "https://www.pinterest.com/settings/privacy",
            "login_url": "https://www.pinterest.com/login/",
            "login_check": "https://www.pinterest.com/",
            "username_field": "email",
            "password_field": "password",
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//div[contains(@data-test-id, 'user-avatar')]",
        },
        "snapchat": {
            "domains": ["snapchat.com", "accounts.snapchat.com"],
            "delete_url": "https://accounts.snapchat.com/accounts/delete_account",
            "download_url": "https://accounts.snapchat.com/accounts/downloadmydata",
            "login_url": "https://accounts.snapchat.com/accounts/login",
            "login_check": "https://web.snapchat.com/",
            "username_field": "username",
            "password_field": "password",
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//img[contains(@alt, 'Bitmoji')]",
        },
        "discord": {
            "domains": ["discord.com", "discordapp.com"],
            "delete_url": "https://discord.com/settings/account",
            "download_url": "https://discord.com/settings/privacy",
            "login_url": "https://discord.com/login",
            "login_check": "https://discord.com/channels/@me",
            "username_field": "//input[@name='email']",
            "password_field": "//input[@name='password']",
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//div[contains(@class, 'avatar')]",
        },
        "tumblr": {
            "domains": ["tumblr.com", "www.tumblr.com"],
            "delete_url": "https://www.tumblr.com/settings/account",
            "download_url": "https://www.tumblr.com/settings/account",
            "login_url": "https://www.tumblr.com/login",
            "login_check": "https://www.tumblr.com/dashboard",
            "username_field": "email",
            "password_field": "password",
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//a[contains(@class, 'avatar')]",
        },
        "twitch": {
            "domains": ["twitch.tv", "www.twitch.tv"],
            "delete_url": "https://www.twitch.tv/user/delete-account",
            "download_url": "https://www.twitch.tv/settings/data",
            "login_url": "https://www.twitch.tv/login",
            "login_check": "https://www.twitch.tv/",
            "username_field": "login",
            "password_field": "password",
            "submit_button": "//button[@data-a-target='passport-login-button']",
            "profile_indicator": "//div[contains(@class, 'user-menu-dropdown')]",
        },
        "youtube": {
            "domains": ["youtube.com", "www.youtube.com"],
            "delete_url": "https://myaccount.google.com/deleteservices",
            "download_url": "https://takeout.google.com/",
            "login_url": "https://accounts.google.com/signin",
            "login_check": "https://www.youtube.com/",
            "username_field": "identifier",
            "password_field": "password",
            "submit_button": "//button[contains(., 'Next')]",
            "profile_indicator": "//yt-icon-button[@id='avatar-btn']",
        },
        "telegram": {
            "domains": ["telegram.org", "web.telegram.org"],
            "delete_url": "https://my.telegram.org/auth?to=delete",
            "download_url": "https://my.telegram.org/auth?to=export",
            "login_url": "https://my.telegram.org/auth",
            "login_check": "https://web.telegram.org/",
            "username_field": "phone",
            "password_field": "password",  # For verification code in some steps
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//div[contains(@class, 'profile-info')]",
        },
        "whatsapp": {
            "domains": ["whatsapp.com", "web.whatsapp.com"],
            "delete_url": "https://faq.whatsapp.com/general/account-and-profile/how-to-delete-your-account/",
            "download_url": "https://faq.whatsapp.com/general/account-and-profile/how-to-request-your-account-information/",
            "login_url": "https://web.whatsapp.com/",
            "login_check": "https://web.whatsapp.com/",
            "username_field": None,  # WhatsApp Web uses QR code login
            "password_field": None,
            "submit_button": None,
            "profile_indicator": "//span[@data-icon='menu']",
        },
        "wechat": {
            "domains": ["wechat.com", "wx.qq.com"],
            "delete_url": "https://help.wechat.com/cgi-bin/micromsg-bin/oshelpcenter?opcode=2",
            "download_url": "https://help.wechat.com/cgi-bin/micromsg-bin/oshelpcenter?opcode=2",
            "login_url": "https://wx.qq.com/",
            "login_check": "https://wx.qq.com/",
            "username_field": None,  # WeChat Web uses QR code login
            "password_field": None,
            "submit_button": None,
            "profile_indicator": "//img[contains(@class, 'avatar')]",
        },
        "clubhouse": {
            "domains": ["clubhouse.com", "www.clubhouse.com"],
            "delete_url": "https://www.clubhouse.com/settings",
            "download_url": "https://www.clubhouse.com/settings",
            "login_url": "https://www.clubhouse.com/signin",
            "login_check": "https://www.clubhouse.com/",
            "username_field": "phoneNumber",
            "password_field": "verificationCode",
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//div[contains(@class, 'profileInfo')]",
        },
        "threads": {
            "domains": ["threads.net", "www.threads.net"],
            "delete_url": "https://www.threads.net/accounts/remove/request/permanent/",
            "download_url": "https://www.threads.net/download/request/",
            "login_url": "https://www.threads.net/accounts/login/",
            "login_check": "https://www.threads.net/",
            "username_field": "username",
            "password_field": "password",
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//a[contains(@href, '/profile/')]",
        },
        "mastodon": {
            "domains": ["mastodon.social", "mastodon.online"],
            "delete_url": "https://mastodon.social/settings/delete",
            "download_url": "https://mastodon.social/settings/export",
            "login_url": "https://mastodon.social/auth/sign_in",
            "login_check": "https://mastodon.social/home",
            "username_field": "user[email]",
            "password_field": "user[password]",
            "submit_button": "//button[@type='submit']",
            "profile_indicator": "//div[contains(@class, 'account__header')]",
        },
        "bereal": {
            "domains": ["bereal.com", "app.bereal.com"],
            "delete_url": "https://app.bereal.com/settings/account",
            "download_url": "https://app.bereal.com/settings/account",
            "login_url": "https://app.bereal.com/",
            "login_check": "https://app.bereal.com/feed",
            "username_field": "phone",
            "password_field": "verificationCode",  # BeReal uses phone verification
            "submit_button": "//button[contains(text(), 'Continue')]",
            "profile_indicator": "//div[contains(@class, 'profilePicture')]",
        },
    }

    def __init__(self):
        self.detected_accounts = {}
        self.driver = None
        self.credential_store = {}
        self.debug = False  # Default debug mode is off
        self.current_credentials = (
            {}
        )  # To store credentials for the current login attempt

    def log_debug(self, message):
        if self.debug:
            print(f"[DEBUG] {message}")

    def _check_permissions(self):
        """Check if the tool has sufficient permissions [1]"""
        try:
            if platform.system() == "Windows":
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            elif platform.system() in ["Darwin", "Linux"]:
                return os.geteuid() == 0
        except Exception as e:
            self.log_debug(f"Permission check error: {e}")
        return False

    def _extract_browser_passwords(self, browser_name, login_db_path, key_path):
        """Generic function to extract passwords from Chromium-based browsers [2, 3]"""
        passwords = {}
        try:
            if not os.path.exists(login_db_path):
                self.log_debug(
                    f"{browser_name} login database not found at {login_db_path}"
                )
                return passwords

            if not os.path.exists(key_path):
                self.log_debug(f"{browser_name} encryption key not found at {key_path}")
                return passwords

            temp_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), f"temp_{browser_name}_login"
            )

            os.system(
                f'copy "{login_db_path}" "{temp_path}" 2>nul'
                if platform.system() == "Windows"
                else f'cp "{login_db_path}" "{temp_path}" 2>/dev/null'
            )

            with open(key_path, "r", encoding="utf-8") as f:
                local_state = json.loads(f.read())
                key = local_state["os_crypt"]["encrypted_key"]
                key = key[5:]
                # Decrypt key - This part requires additional implementation using cryptography library
                # For now, we'll just extract the encrypted password

            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT origin_url, username_value, password_value FROM logins"
            )
            for url, username, password in cursor.fetchall():
                for platform_name, platform_data in self.PLATFORMS.items():
                    for domain in platform_data["domains"]:
                        if domain in url:
                            passwords.setdefault(
                                platform_name, {"username": username, "url": url}
                            )
            conn.close()
            os.remove(temp_path)

        except Exception as e:
            print(f"[-] Error extracting {browser_name} passwords: {e}")
            self.log_debug(
                f"Detailed {browser_name} password extraction error: {str(e)}"
            )
        return passwords

    def _get_chromium_paths(self, browser_name):
        """Get OS-specific paths for Chromium-based browsers [4-11]"""
        paths = {}
        if browser_name == "Chrome":
            if platform.system() == "Windows":
                paths["login_db"] = os.path.join(
                    os.getenv("LOCALAPPDATA"),
                    r"Google\Chrome\User Data\Default\Login Data",
                )
                paths["key_path"] = os.path.join(
                    os.getenv("LOCALAPPDATA"), r"Google\Chrome\User Data\Local State"
                )
            elif platform.system() == "Darwin":
                paths["login_db"] = os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/Google/Chrome/Default/Login Data",
                )
                paths["key_path"] = os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/Google/Chrome/Local State",
                )
            elif platform.system() == "Linux":
                paths["login_db"] = os.path.join(
                    os.path.expanduser("~"), r".config/google-chrome/Default/Login Data"
                )
                paths["key_path"] = os.path.join(
                    os.path.expanduser("~"), r".config/google-chrome/Local State"
                )
        elif browser_name == "Edge":
            if platform.system() == "Windows":
                paths["login_db"] = os.path.join(
                    os.getenv("LOCALAPPDATA"),
                    r"Microsoft\Edge\User Data\Default\Login Data",
                )
                paths["key_path"] = os.path.join(
                    os.getenv("LOCALAPPDATA"), r"Microsoft\Edge\User Data\Local State"
                )
            elif platform.system() == "Darwin":
                paths["login_db"] = os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/Microsoft Edge/Default/Login Data",
                )
                paths["key_path"] = os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/Microsoft Edge/Local State",
                )
            elif platform.system() == "Linux":
                paths["login_db"] = os.path.join(
                    os.path.expanduser("~"),
                    r".config/microsoft-edge/Default/Login Data",
                )
                paths["key_path"] = os.path.join(
                    os.path.expanduser("~"), r".config/microsoft-edge/Local State"
                )
        elif browser_name == "Brave":
            if platform.system() == "Windows":
                paths["login_db"] = os.path.join(
                    os.getenv("LOCALAPPDATA"),
                    r"BraveSoftware\Brave-Browser\User Data\Default\Login Data",
                )
                paths["key_path"] = os.path.join(
                    os.getenv("LOCALAPPDATA"),
                    r"BraveSoftware\Brave-Browser\User Data\Local State",
                )
            elif platform.system() == "Darwin":
                paths["login_db"] = os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/BraveSoftware/Brave-Browser/Default/Login Data",
                )
                paths["key_path"] = os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/BraveSoftware/Brave-Browser/Local State",
                )
            elif platform.system() == "Linux":
                paths["login_db"] = os.path.join(
                    os.path.expanduser("~"),
                    r".config/BraveSoftware/Brave-Browser/Default/Login Data",
                )
                paths["key_path"] = os.path.join(
                    os.path.expanduser("~"),
                    r".config/BraveSoftware/Brave-Browser/Local State",
                )
        elif browser_name == "Opera":
            if platform.system() == "Windows":
                paths["login_db"] = os.path.join(
                    os.getenv("APPDATA"), r"Opera Software\Opera Stable\Login Data"
                )
                paths["key_path"] = os.path.join(
                    os.getenv("APPDATA"), r"Opera Software\Opera Stable\Local State"
                )
            elif platform.system() == "Darwin":
                paths["login_db"] = os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/com.operasoftware.Opera/Login Data",
                )
                paths["key_path"] = os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/com.operasoftware.Opera/Local State",
                )
            elif platform.system() == "Linux":
                paths["login_db"] = os.path.join(
                    os.path.expanduser("~"), r".config/opera/Login Data"
                )
                paths["key_path"] = os.path.join(
                    os.path.expanduser("~"), r".config/opera/Local State"
                )
        elif browser_name == "Vivaldi":
            if platform.system() == "Windows":
                paths["login_db"] = os.path.join(
                    os.getenv("LOCALAPPDATA"), r"Vivaldi\User Data\Default\Login Data"
                )
                paths["key_path"] = os.path.join(
                    os.getenv("LOCALAPPDATA"), r"Vivaldi\User Data\Local State"
                )
            elif platform.system() == "Darwin":
                paths["login_db"] = os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/Vivaldi/Default/Login Data",
                )
                paths["key_path"] = os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/Vivaldi/Local State",
                )
            elif platform.system() == "Linux":
                paths["login_db"] = os.path.join(
                    os.path.expanduser("~"), r".config/vivaldi/Default/Login Data"
                )
                paths["key_path"] = os.path.join(
                    os.path.expanduser("~"), r".config/vivaldi/Local State"
                )
        return paths

    def _extract_firefox_passwords(self):
        """Extract saved passwords from Firefox [12-15]"""
        passwords = {}
        try:
            if platform.system() == "Windows":
                profiles_path = os.path.join(
                    os.getenv("APPDATA"), r"Mozilla\Firefox\Profiles"
                )
            elif platform.system() == "Darwin":
                profiles_path = os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/Firefox/Profiles",
                )
            elif platform.system() == "Linux":
                profiles_path = os.path.join(
                    os.path.expanduser("~"), r".mozilla/firefox"
                )
            else:
                return passwords

            if not os.path.exists(profiles_path):
                self.log_debug(f"Firefox profiles path not found: {profiles_path}")
                return passwords

            profiles = [
                os.path.join(profiles_path, d)
                for d in os.listdir(profiles_path)
                if os.path.isdir(os.path.join(profiles_path, d))
            ]

            for profile in profiles:
                logins_path = os.path.join(profile, "logins.json")
                if os.path.exists(logins_path):
                    try:
                        with open(logins_path, "r") as f:
                            logins_data = json.load(f)
                            for login in logins_data.get("logins", []):
                                hostname = login.get("hostname", "")
                                username = login.get("username", "")
                                for (
                                    platform_name,
                                    platform_data,
                                ) in self.PLATFORMS.items():
                                    for domain in platform_data["domains"]:
                                        if domain in hostname:
                                            passwords.setdefault(
                                                platform_name,
                                                {"username": username, "url": hostname},
                                            )
                    except json.JSONDecodeError as e:
                        self.log_debug(
                            f"Error decoding Firefox logins.json in {profile}: {e}"
                        )
                    except Exception as e:
                        self.log_debug(
                            f"Error processing Firefox logins.json in {profile}: {e}"
                        )
            return passwords

        except Exception as e:
            print(f"[-] Error extracting Firefox passwords: {e}")
            self.log_debug(f"Detailed Firefox password extraction error: {str(e)}")
            return passwords

    def _check_browser_database(self):
        """Check browser databases for saved login information [15-17]"""
        password_data = {}
        try:
            chrome_paths = self._get_chromium_paths("Chrome")
            password_data.update(
                self._extract_browser_passwords(
                    "Chrome", chrome_paths.get("login_db"), chrome_paths.get("key_path")
                )
            )

            edge_paths = self._get_chromium_paths("Edge")
            password_data.update(
                self._extract_browser_passwords(
                    "Edge", edge_paths.get("login_db"), edge_paths.get("key_path")
                )
            )

            brave_paths = self._get_chromium_paths("Brave")
            password_data.update(
                self._extract_browser_passwords(
                    "Brave", brave_paths.get("login_db"), brave_paths.get("key_path")
                )
            )

            opera_paths = self._get_chromium_paths("Opera")
            password_data.update(
                self._extract_browser_passwords(
                    "Opera", opera_paths.get("login_db"), opera_paths.get("key_path")
                )
            )

            vivaldi_paths = self._get_chromium_paths("Vivaldi")
            password_data.update(
                self._extract_browser_passwords(
                    "Vivaldi",
                    vivaldi_paths.get("login_db"),
                    vivaldi_paths.get("key_path"),
                )
            )

            password_data.update(self._extract_firefox_passwords())

        except Exception as e:
            print(f"[-] Error checking browser databases: {e}")
            self.log_debug(f"Detailed browser database check error: {str(e)}")

        return password_data

    def _get_browser_cookies(self):
        """Get cookies with better fallback mechanisms [17-20]"""
        all_cookies = []
        browsers = [
            {"name": "Chrome", "function": browser_cookie3.chrome},
            {"name": "Firefox", "function": browser_cookie3.firefox},
            {"name": "Edge", "function": browser_cookie3.edge},
            {"name": "Opera", "function": browser_cookie3.opera},
        ]

        if platform.system() == "Darwin":
            browsers.append({"name": "Safari", "function": browser_cookie3.safari})

        for browser in browsers:
            try:
                cookies = browser["function"]()
                all_cookies.extend(cookies)
                self.log_debug(f"Successfully read {browser['name']} cookies")
                print(f"[+] Successfully read {browser['name']} cookies")
            except Exception as e:
                print(f"[-] Could not read {browser['name']} cookies: {e}")
                self.log_debug(
                    f"Could not read {browser['name']} cookies ({browser['name']}): {e}"
                )

        # Attempt Brave specifically as browser_cookie3 might not directly support it
        if platform.system() == "Windows":
            brave_path = os.path.join(
                os.getenv("LOCALAPPDATA"), r"BraveSoftware\Brave-Browser\User Data"
            )
        elif platform.system() == "Darwin":
            brave_path = os.path.join(
                os.path.expanduser("~"),
                r"Library/Application Support/BraveSoftware/Brave-Browser",
            )
        elif platform.system() == "Linux":
            brave_path = os.path.join(
                os.path.expanduser("~"), r".config/BraveSoftware/Brave-Browser"
            )
        else:
            brave_path = None

        if brave_path and os.path.exists(
            os.path.join(brave_path, "Default", "Cookies")
        ):
            try:
                brave_cookies = browser_cookie3.chrome(
                    cookie_file=os.path.join(brave_path, "Default", "Cookies")
                )
                all_cookies.extend(brave_cookies)
                print("[+] Successfully read Brave cookies")
                self.log_debug("Successfully read Brave cookies")
            except Exception as e:
                print(f"[-] Could not read Brave cookies: {e}")
                self.log_debug(f"Could not read Brave cookies: {e}")

        return all_cookies

    def _parse_browser_history(self):
        """Parse browser history for social media platform visits [20-27]"""
        history_data = {}
        browsers = {
            "Chrome": {
                "windows": os.path.join(
                    os.getenv("LOCALAPPDATA"),
                    r"Google\Chrome\User Data\Default\History",
                ),
                "darwin": os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/Google/Chrome/Default/History",
                ),
                "linux": os.path.join(
                    os.path.expanduser("~"), r".config/google-chrome/Default/History"
                ),
            },
            "Edge": {
                "windows": os.path.join(
                    os.getenv("LOCALAPPDATA"),
                    r"Microsoft\Edge\User Data\Default\History",
                ),
                "darwin": os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/Microsoft Edge/Default/History",
                ),
                "linux": os.path.join(
                    os.path.expanduser("~"), r".config/microsoft-edge/Default/History"
                ),
            },
            "Brave": {
                "windows": os.path.join(
                    os.getenv("LOCALAPPDATA"),
                    r"BraveSoftware\Brave-Browser\User Data\Default\History",
                ),
                "darwin": os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/BraveSoftware/Brave-Browser/Default/History",
                ),
                "linux": os.path.join(
                    os.path.expanduser("~"),
                    r".config/BraveSoftware/Brave-Browser/Default/History",
                ),
            },
            "Opera": {
                "windows": os.path.join(
                    os.getenv("APPDATA"), r"Opera Software\Opera Stable\History"
                ),
                "darwin": os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/com.operasoftware.Opera/History",
                ),
                "linux": os.path.join(
                    os.path.expanduser("~"), r".config/opera/History"
                ),
            },
            "Vivaldi": {
                "windows": os.path.join(
                    os.getenv("LOCALAPPDATA"), r"Vivaldi\User Data\Default\History"
                ),
                "darwin": os.path.join(
                    os.path.expanduser("~"),
                    r"Library/Application Support/Vivaldi/Default/History",
                ),
                "linux": os.path.join(
                    os.path.expanduser("~"), r".config/vivaldi/Default/History"
                ),
            },
        }

        current_platform = platform.system().lower()
        for browser_name, paths in browsers.items():
            if current_platform in paths:
                history_path = paths[current_platform]
                if os.path.exists(history_path):
                    try:
                        temp_path = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)),
                            f"temp_{browser_name.lower()}_history",
                        )
                        os.system(
                            f'copy "{history_path}" "{temp_path}" 2>nul'
                            if platform.system() == "Windows"
                            else f'cp "{history_path}" "{temp_path}" 2>/dev/null'
                        )

                        conn = sqlite3.connect(temp_path)
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT url FROM urls ORDER BY last_visit_time DESC LIMIT 1000"
                        )
                        for (url,) in cursor.fetchall():
                            for platform_name, platform_data in self.PLATFORMS.items():
                                for domain in platform_data["domains"]:
                                    if domain in url:
                                        profile_pattern = re.compile(
                                            rf"https?://(www\.)?{domain.replace('.', r'\\.')}/(.*?)(/|$)"
                                        )
                                        match = profile_pattern.search(url)
                                        if (
                                            match
                                            and match.group(2)
                                            and match.group(2)
                                            not in [
                                                "login",
                                                "signup",
                                                "explore",
                                                "home",
                                                "settings",
                                                "notifications",
                                                "messages",
                                                "search",
                                            ]
                                        ):
                                            history_data.setdefault(
                                                platform_name,
                                                {
                                                    "potential_username": match.group(
                                                        2
                                                    ),
                                                    "url": url,
                                                    "browser": browser_name,
                                                },
                                            )
                                            break
                                break
                        conn.close()
                        os.remove(temp_path)
                        print(f"[+] Successfully analyzed {browser_name} history")
                        self.log_debug(f"Successfully analyzed {browser_name} history")

                    except sqlite3.Error as e:
                        print(f"[-] SQLite error parsing {browser_name} history: {e}")
                        self.log_debug(
                            f"SQLite error parsing {browser_name} history: {e}"
                        )
                    except Exception as e:
                        print(f"[-] Error parsing {browser_name} history: {e}")
                        self.log_debug(
                            f"Detailed error parsing {browser_name} history: {str(e)}"
                        )
        return history_data

    def _scan_local_app_data(self):
        """Scan for local app data that might indicate social media usage [27-29]"""
        detected_platforms = set()
        app_indicators = {
            "facebook": [
                os.path.join(os.path.expanduser("~"), "AppData", "Local", "Facebook"),
                os.path.join(
                    os.path.expanduser("~"),
                    "Library",
                    "Application Support",
                    "Facebook",
                ),
            ],
            "instagram": [
                os.path.join(os.path.expanduser("~"), "AppData", "Local", "Instagram"),
                os.path.join(
                    os.path.expanduser("~"),
                    "Library",
                    "Application Support",
                    "Instagram",
                ),
            ],
            "discord": [
                os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Discord"),
                os.path.join(
                    os.path.expanduser("~"), "Library", "Application Support", "Discord"
                ),
            ],
            "slack": [
                os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Slack"),
                os.path.join(
                    os.path.expanduser("~"), "Library", "Application Support", "Slack"
                ),
            ],
            "twitter": [
                os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Twitter"),
                os.path.join(
                    os.path.expanduser("~"), "Library", "Application Support", "Twitter"
                ),
            ],
        }

        for platform_name, paths in app_indicators.items():
            for path in paths:
                if os.path.exists(path):
                    detected_platforms.add(platform_name)
                    break
        return detected_platforms

    def detect_accounts(self):
        """Enhanced detection of social media accounts using a scoring system [30-40]"""
        print("\n[+] Scanning for social media accounts in browser data...")
        detection_scores = {platform: 0 for platform in self.PLATFORMS.keys()}
        detection_methods = {platform: [] for platform in self.PLATFORMS.keys()}
        self.credential_store = {}  # Initialize credential store

        # Check cookies (most reliable)
        try:
            all_cookies = self._get_browser_cookies()
            for cookie in all_cookies:
                for platform_name, platform_data in self.PLATFORMS.items():
                    for domain in platform_data["domains"]:
                        if domain in cookie.domain:
                            detection_scores[platform_name] += 3
                            if "cookies" not in detection_methods[platform_name]:
                                detection_methods[platform_name].append("cookies")
                            break
        except Exception as e:
            self.log_debug(f"Cookie detection error: {e}")

        # Check browser saved passwords (medium-high confidence)
        try:
            password_data = self._check_browser_database()
            for platform, data in password_data.items():
                if platform in detection_scores:
                    detection_scores[platform] += 2
                    if "saved_password" not in detection_methods[platform]:
                        detection_methods[platform].append("saved_password")
                    # Store potential username from saved passwords
                    if "username" in data:
                        self.credential_store.setdefault(platform, {})["username"] = (
                            data["username"]
                        )
                        if "username" not in self.detected_accounts.get(platform, {}):
                            self.detected_accounts.setdefault(platform, {}).update(data)
        except Exception as e:
            self.log_debug(f"Password detection error: {e}")

        # Parse browser history (lower confidence)
        try:
            history_data = self._parse_browser_history()
            for platform, data in history_data.items():
                if platform in detection_scores:
                    detection_scores[platform] += 1
                    if "history" not in detection_methods[platform]:
                        detection_methods[platform].append("history")
                    # Store potential username from history if not already found
                    potential_username = data.get("potential_username")
                    if potential_username and (
                        platform not in self.credential_store
                        or "username" not in self.credential_store[platform]
                    ):
                        self.credential_store.setdefault(platform, {})[
                            "username"
                        ] = potential_username
                    if "potential_username" not in self.detected_accounts.get(
                        platform, {}
                    ) and "username" not in self.credential_store.get(platform, {}):
                        self.detected_accounts.setdefault(platform, {}).update(data)
        except Exception as e:
            self.log_debug(f"History detection error: {e}")

        # Check local app data (medium-high confidence)
        try:
            app_data = self._scan_local_app_data()
            for platform in app_data:
                if platform in detection_scores:
                    detection_scores[platform] += 2
                    if "local_app_data" not in detection_methods[platform]:
                        detection_methods[platform].append("local_app_data")
        except Exception as e:
            self.log_debug(f"App data detection error: {e}")

        # Build final results (platforms with score > 0)
        self.detected_accounts = {}  # Reset to store with details
        for platform, score in detection_scores.items():
            if score > 0:
                self.detected_accounts[platform] = {
                    "detection_score": score,
                    "detection_methods": detection_methods[platform],
                }
                print(
                    f"[+] Detected {platform} account via {', '.join(detection_methods[platform])}"
                )
                if platform in self.credential_store and self.credential_store[
                    platform
                ].get("username"):
                    print(
                        f" └─ Found potential username: {self.credential_store[platform]['username']}"
                    )

        if not self.detected_accounts:
            print("[-] No social media accounts detected in browser data")

    def display_results(self):
        """Display detection results in a more user-friendly way [41, 42]"""
        if not self.detected_accounts:
            print("\n[-] No social media accounts detected")
            return

        print("\n[+] Detected Social Media Accounts:")
        print("=" * 50)
        print(f"{'Platform':<15} {'Confidence':<15} {'Detection Methods':<20}")
        print("-" * 50)
        for platform, data in self.detected_accounts.items():
            score = data.get("detection_score", 0)
            if score >= 5:
                confidence = "High"
            elif score >= 3:
                confidence = "Medium"
            else:
                confidence = "Low"
            methods = ", ".join(data.get("detection_methods", []))
            print(f"{platform:<15} {confidence:<15} {methods:<20}")
        print("=" * 50)

    def manual_verification(self):
        """Allow users to manually confirm detected accounts [43]"""
        if not self.detected_accounts:
            return

        print("\n[+] Please verify these detected accounts:")
        verified_accounts = {}
        for platform in list(self.detected_accounts.keys()):
            response = input(
                f"[?] Do you want to delete your {Fore.RED + Style.BRIGHT}{platform}{Style.RESET_ALL} account? (yes/no): "
            ).lower()
            if response == "yes":
                verified_accounts[platform] = self.detected_accounts[platform]
        self.detected_accounts = verified_accounts
        if self.detected_accounts:
            print("\n[+] Verified accounts:", ", ".join(self.detected_accounts.keys()))

    def _prompt_for_credentials(self):
        """Prompt user for credentials for verified platforms [44, 45]"""
        print("\n[+] Please enter credentials for the platforms you wish to process:")
        print(
            f"{Fore.YELLOW + Style.BRIGHT}[!] Security Warning:{Style.RESET_ALL} Please be cautious when entering your credentials. This information will be used only for the immediate login attempt and will be cleared afterwards."
        )
        print(
            f"{Fore.CYAN}   For enhanced security and convenience for frequent use, consider using a secure credential manager like 'keyring'. You would need to configure it separately and modify the tool to use it.{Style.RESET_ALL}"
        )
        self.current_credentials = {}
        for platform in self.detected_accounts.keys():
            username_suggestion = self.credential_store.get(platform, {}).get(
                "username", ""
            )
            print(f"\n[+] {platform}")
            if username_suggestion:
                username = input(
                    f"[?] Username/Email (suggested: {username_suggestion}): "
                )
                if not username:
                    username = username_suggestion
            else:
                username = input("[?] Username/Email: ")

            password = getpass.getpass("[?] Password: ")
            if username and password:
                self.current_credentials[platform] = {
                    "username": username,
                    "password": password,
                }
            else:
                print(f"[!] Skipping {platform} as credentials were not provided.")

    def setup_browser(self):
        """Initialize the webdriver [46, 47]"""
        print("\n[+] Setting up browser...")
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                },
            )
            return True
        except Exception as e:
            print(f"[-] Error setting up browser: {e}")
            print(
                "[-] Please ensure you have Chrome and ChromeDriver installed and in your PATH."
            )
            self.log_debug(f"Browser setup error: {e}")
            return False

    def process_platform(self, platform_name, download_first=True):
        """Process a single platform for data download and deletion [47-52]"""
        if platform_name not in self.PLATFORMS:
            print(f"[-] Platform {platform_name} not supported")
            return

        platform_data = self.PLATFORMS[platform_name]
        credentials = self.current_credentials.get(platform_name)

        if credentials:
            print(f"\n[+] Logging in to {platform_name}...")
            try:
                self.driver.get(platform_data["login_url"])
                time.sleep(3)
                username_elem = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, platform_data["username_field"])
                        if "//" in platform_data["username_field"]
                        else (By.NAME, platform_data["username_field"])
                    )
                )
                username_elem.clear()
                username_elem.send_keys(credentials["username"])

                if platform_name == "twitter":
                    next_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                    )
                    next_button.click()
                    time.sleep(3)
                    password_elem = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, platform_data["password_field"])
                            if "//" in platform_data["password_field"]
                            else (By.NAME, platform_data["password_field"])
                        )
                    )
                    password_elem.clear()
                    password_elem.send_keys(credentials["password"])
                else:
                    password_elem = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, platform_data["password_field"])
                            if "//" in platform_data["password_field"]
                            else (By.NAME, platform_data["password_field"])
                        )
                    )
                    password_elem.clear()
                    password_elem.send_keys(credentials["password"])

                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, platform_data["submit_button"])
                    )
                )
                login_button.click()
                time.sleep(5)
                print(f"[+] Login attempt completed for {platform_name}")

                if download_first:
                    print(
                        f"\n[+] Navigating to data download page for {platform_name}..."
                    )
                    self.driver.get(platform_data["download_url"])
                    print(
                        f"[+] Follow the instructions in the browser to request your data from {platform_name}"
                    )
                    input(
                        "[+] Press Enter once you've completed the data download request..."
                    )

                print(
                    f"\n[+] Navigating to account deletion page for {platform_name}..."
                )
                self.driver.get(platform_data["delete_url"])
                print(
                    f"[+] Follow the instructions in the browser to delete your {platform_name} account"
                )
                input("[+] Press Enter once you've completed the deletion process...")

            except Exception as e:
                print(f"[-] Login or processing failed for {platform_name}: {e}")
                print(
                    f"[+] You may need to login and proceed manually in the browser window."
                )
                input(
                    f"[+] Press Enter once you've manually completed the process for {platform_name}..."
                )

        else:
            print(
                f"\n[+] No credentials provided for {platform_name}. Skipping automated process."
            )
            print(
                f"[+] You can manually visit the following URLs to download and delete your account:"
            )
            print(f"  - Download Data: {platform_data.get('download_url')}")
            print(f"  - Delete Account: {platform_data.get('delete_url')}")
            input("[+] Press Enter to continue with other platforms.")

        # Minimize in-memory storage: Clear credentials after processing
        if platform_name in self.current_credentials:
            del self.current_credentials[platform_name]

    def run(self, dry_run=False):
        """Main execution flow with dry run option [34-40, 44, 45, 52-60]"""
        print(self.colored_banner)
        print(f"Version: {self.colored_version}")
        print(f"Credits: {self.colored_credits}")
        print("\nWelcome to DigitalDetox - A tool to help you go truly offline.")

        self.debug = True  # Enable debug mode during run

        if dry_run:
            print("\n[!] Running in DRY RUN mode - no accounts will be modified")

        # Step 1: Check Permissions
        if not self._check_permissions():
            print("[!] Warning: Running without admin/root privileges")
            print("[!] Some browser data extraction features may not work")
            print("[!] Consider running this tool with elevated privileges")

        # Step 2: Detect accounts
        self.detect_accounts()
        self.display_results()

        # Step 3: Manual Verification
        self.manual_verification()

        if not self.detected_accounts and not dry_run:
            print("\n[-] No accounts selected or verified. Exiting.")
            return

        if self.detected_accounts and not dry_run:
            # Step 4: Prompt for credentials
            self._prompt_for_credentials()

            # Confirm deletion
            print(
                "\n[+] The following accounts will be processed (if credentials were provided):"
            )
            for i, platform in enumerate(self.detected_accounts, 1):
                print(f"{i}. {platform}")

            confirm = input(
                f"\n{Fore.YELLOW + Style.BRIGHT}[!] WARNING:{Style.RESET_ALL} Account deletion is permanent. Proceed with the platforms where credentials were provided? (yes/no): "
            ).lower()

            if confirm != "yes":
                print("[-] Operation cancelled.")
                return

            # Download data option
            download = input(
                f"{Fore.GREEN}[?] Download{Style.RESET_ALL} your data before deletion for platforms being processed? (yes/no): "
            ).lower()
            download_first = download == "yes"

            # Setup browser
            if not self.setup_browser():
                return

            # Process each platform
            for platform in list(self.detected_accounts.keys()):
                self.process_platform(platform, download_first)

            # Cleanup
            if self.driver:
                self.driver.quit()
            print("\n[+] Process complete!")
            print("[+] Some platforms may have a delay before permanent deletion.")
            print("[+] Check your email for confirmation messages from each platform.")

        elif dry_run and self.detected_accounts:
            print("\n[!] Dry run complete. The following accounts were detected:")
            self.display_results()

        elif dry_run and not self.detected_accounts:
            print("\n[!] Dry run complete. No accounts were detected.")


if __name__ == "__main__":
    tool = DigitalDetox()
    tool.run()
