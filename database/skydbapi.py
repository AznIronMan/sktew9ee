import requests
from settings.settings_file import SettingsManager
from utils.sk_logger import sk_log


class SkyDBAPI:
    def __init__(self):
        settings = SettingsManager()
        self.api_url = settings.get_value("skydb_api_server")
        self.api_port = settings.get_value("skydb_api_port")
        self.api_ssl = settings.get_value("skydb_api_ssl")
        if isinstance(self.api_ssl, str):
            self.api_ssl = self.api_ssl.lower() == "true"
        protocol = "https" if self.api_ssl else "http"
        self.api_url = f"{protocol}://{self.api_url}:{self.api_port}"
        sk_log.debug(
            f"SkyDBAPI initialized with URL: {self.api_url} "
            f"(SSL: {self.api_ssl})"
        )
        if not self.api_ssl:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def create(self, query, params=None):
        sk_log.debug(f"Creating table with query: {query}")
        self._execute_non_select_query(query, params)

    def insert(self, query, params=None):
        sk_log.debug(f"Inserting data with query: {query}")
        self._execute_non_select_query(query, params)

    def update(self, query, params=None):
        sk_log.debug(f"Updating data with query: {query}")
        self._execute_non_select_query(query, params)

    def delete(self, query, params=None):
        sk_log.debug(f"Deleting data with query: {query}")
        self._execute_non_select_query(query, params)

    def select(self, query, params=None):
        sk_log.debug(f"Selecting data with query: {query}")
        return self._execute_select_query(query, params)

    def custom_query(self, query, params=None):
        sk_log.debug(f"Executing custom query: {query}")
        if query.strip().upper().startswith("SELECT"):
            return self._execute_select_query(query, params)
        else:
            self._execute_non_select_query(query, params)

    def _execute_select_query(self, query, params=None):
        """Executes a SELECT query and returns the results."""
        sk_log.debug(f"SkyDBAPI executing SELECT query: {query}")
        payload = {"query": query, "params": params or []}
        try:
            response = requests.post(
                f"{self.api_url}/query", json=payload, timeout=5, verify=False
            )
            sk_log.debug(
                f"SkyDBAPI received response with status: "
                f"{response.status_code}"
            )

            if response.status_code == 200:
                result = response.json()
                sk_log.debug(f"SkyDBAPI SELECT query result: {result}")
                return result
            else:
                error_message = response.text
                try:
                    error_message = response.json().get(
                        "error", "Unknown error"
                    )
                except Exception:
                    pass
                sk_log.error(
                    f"SkyDBAPI SELECT query failed with status "
                    f"{response.status_code}: {error_message}"
                )
                raise Exception(
                    f"Error executing SELECT query: {error_message}"
                )
        except requests.Timeout:
            sk_log.error("SkyDBAPI request timed out after 5 seconds")
            raise Exception("Database request timed out")
        except requests.RequestException as e:
            sk_log.error(f"SkyDBAPI request failed: {str(e)}")
            raise Exception(f"Database request failed: {str(e)}")

    def _execute_non_select_query(self, query, params=None):
        """Executes a non-SELECT query (e.g., CREATE, INSERT, UPDATE, DELETE)."""
        sk_log.debug(f"SkyDBAPI executing non-SELECT query: {query}")
        payload = {"query": query, "params": params or []}
        response = requests.post(
            f"{self.api_url}/query", json=payload, verify=False
        )

        if response.status_code == 200:
            sk_log.debug("SkyDBAPI query executed successfully.")
        else:
            error_message = response.json().get("error", "Unknown error")
            sk_log.error(f"SkyDBAPI non-SELECT query failed: {error_message}")
            raise Exception(f"Error executing query: {error_message}")
