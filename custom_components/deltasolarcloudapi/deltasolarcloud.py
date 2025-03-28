import logging
import requests
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://mydeltasolar.deltaww.com"
LOGIN_URL = f"{BASE_URL}/includes/process_login.php"
DATA_URL = f"{BASE_URL}/includes/process_init_plant.php?_="
WATT_URL = f"{BASE_URL}/includes/process_gtop_plot.php"

class DeltaSolarCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, email, password):
        """Initialize the coordinator."""
        self.hass = hass
        self.email = email
        self.password = password
        self.session = requests.Session()
        super().__init__(
            hass,
            _LOGGER,
            name="DeltaSolar",
            update_interval=timedelta(minutes=5),
        )

    def login(self):
        """Login to Delta Solar."""
        payload = {"email": self.email, "password": self.password}
        response = self.session.post(LOGIN_URL, data=payload)
        if response.status_code != 200:
            raise UpdateFailed("Failed to login to Delta Solar")

    def fetch_data(self):
        """Fetch data from Delta Solar."""
        response = self.session.get(DATA_URL)
        if response.status_code != 200:
            raise UpdateFailed("Failed to fetch plant data")
        return response.json()

    def fetch_watt_data(self):
        """Fetch watt data from Delta Solar."""
        response = self.session.get(WATT_URL)
        if response.status_code != 200:
            raise UpdateFailed("Failed to fetch watt data")
        return response.json()

    async def _async_update_data(self):
        """Fetch the latest data."""
        try:
            self.login()
            data = self.fetch_data()
            watt_data = self.fetch_watt_data()
            return {"data": data, "watt_data": watt_data}
        except Exception as err:
            raise UpdateFailed(f"Error updating Delta Solar data: {err}")
