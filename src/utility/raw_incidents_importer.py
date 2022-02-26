import requests

from model.incident_type import IncidentType


class RawIncidentsImporter:
    ''' Decouples how the raw incident and identity data is imported '''
    _RESULT_KEY = 'results'

    def __init__(self, base_url, username, password):
        self._base_url = str(base_url)
        self._username = str(username)
        self._password = str(password)

    def _get_session(self):
        # Consider caching for some amount of time
        session = requests.Session()
        session.auth = (self._username, self._password)
        return session

    def _get_json_data(self, url):
        return self._get_session().get(url).json()

    def get_incidents_data(self):
        return {incident_type: self._get_incident_data(incident_type)[RawIncidentsImporter._RESULT_KEY] for incident_type in IncidentType.get_all()}

    def _get_incident_data(self, type):
        return self._get_json_data(f'{self._base_url}/incidents/{type}')

    def get_identities_data(self):
        return self._get_json_data(f'{self._base_url}/identities')
