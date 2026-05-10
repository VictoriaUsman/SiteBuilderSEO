import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

# WordPress.com REST API base — uses Bearer token auth
_WPCOM_BASE = "https://public-api.wordpress.com/wp/v2/sites/{site}"

# Self-hosted WP REST API base — uses Application Password (Basic Auth)
_SELFHOSTED_BASE = "{url}/wp-json/wp/v2"


class WordPressClient:
    def __init__(
        self,
        url: str = None,
        username: str = None,
        app_password: str = None,
        access_token: str = None,
        site: str = None,
    ):
        token = access_token or os.getenv("WP_ACCESS_TOKEN", "")
        wp_url = (url or os.getenv("WP_URL", "")).rstrip("/")
        wp_site = site or os.getenv("WP_SITE", "") or _extract_domain(wp_url)

        self.session = requests.Session()

        if token:
            # WordPress.com mode — OAuth Bearer token
            self._base = _WPCOM_BASE.format(site=wp_site)
            self.session.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            })
            self._mode = "wpcom"
        else:
            # Self-hosted mode — Application Password
            self._base = _SELFHOSTED_BASE.format(url=wp_url)
            self.session.auth = HTTPBasicAuth(
                username or os.getenv("WP_USERNAME", ""),
                app_password or os.getenv("WP_APP_PASSWORD", ""),
            )
            self.session.headers.update({"Content-Type": "application/json"})
            self._mode = "selfhosted"

    def _api(self, path: str) -> str:
        return f"{self._base}/{path.lstrip('/')}"

    def get(self, path: str, **kwargs) -> dict | list:
        resp = self.session.get(self._api(path), timeout=30, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, data: dict, **kwargs) -> dict:
        resp = self.session.post(self._api(path), json=data, timeout=30, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def test_connection(self) -> bool:
        try:
            self.get("users/me")
            return True
        except Exception:
            return False

    @property
    def is_wpcom(self) -> bool:
        return self._mode == "wpcom"


def _extract_domain(url: str) -> str:
    return url.replace("https://", "").replace("http://", "").rstrip("/")
