from threading import Thread
from time import sleep

from controller.data_aggregator import DataAggregator


class PollManager:
    ''' Manages regular polling of the raw incidents data and subsequent aggregation '''
    # Low polling frequency is used for testing that the poll updating is working properly - would be increased for production
    _POLLING_FREQUENCY_SECONDS = 10  # Period of time in seconds between fresh data retrieval attempts
    _MAX_POLLING_ATTEMPTS = 3  # Max attempts per poll, stale data is used if all attempts fail
    _POLL_DATA_KEY_POLLS = 'polls'
    _POLL_DATA_KEY_SUCCESSFUL_UPDATES = 'successful_updates'
    _POLL_DATA_KEY_FAILED_UPDATES = 'failed_updates'
    _POLL_DATA_KEY_TOTAL_IDENTIFIED_INCIDENTS = 'total_identified_incidents'

    def __init__(self, data_importer):
        self._data_importer = data_importer
        self._health_data = {
            PollManager._POLL_DATA_KEY_POLLS: 0,
            PollManager._POLL_DATA_KEY_SUCCESSFUL_UPDATES: 0,
            PollManager._POLL_DATA_KEY_FAILED_UPDATES: 0,
            PollManager._POLL_DATA_KEY_TOTAL_IDENTIFIED_INCIDENTS: 0
        }
        self._aggregated_incidents_data = {}

    def get_health_data(self):
        ''' Captures useful health metrics to diagnose polling success and aggregation updates '''
        return self._health_data

    def get_aggregated_incidents_data(self):
        return self._aggregated_incidents_data

    def poll(self):
        ''' Starts a separate thread to manage polling, so that the main server thread is not blocked '''
        Thread(target=PollManager._run_polling, args=(self._data_importer, self._health_data, self._aggregated_incidents_data)).start()

    @staticmethod
    def _run_polling(data_importer, health_data, aggregated_incidents_data):
        ''' Attempts to import the raw incidents data according to the max attempts parameter and then delegates aggregation of this raw data'''
        while True:
            health_data[PollManager._POLL_DATA_KEY_POLLS] += 1
            update_attempts = 0
            successfully_updated = False
            while not successfully_updated and update_attempts < PollManager._MAX_POLLING_ATTEMPTS:
                update_attempts += 1
                try:
                    raw_incidents_data = data_importer.get_incidents_data()
                    raw_identities_data = data_importer.get_identities_data()
                    successfully_updated = True
                except Exception:
                    health_data[PollManager._POLL_DATA_KEY_FAILED_UPDATES] += 1
            if successfully_updated:
                DataAggregator.aggregate(aggregated_incidents_data, raw_incidents_data, raw_identities_data)
                health_data[PollManager._POLL_DATA_KEY_SUCCESSFUL_UPDATES] += 1
                health_data[PollManager._POLL_DATA_KEY_TOTAL_IDENTIFIED_INCIDENTS] = PollManager._count_incidents(aggregated_incidents_data)
            sleep(PollManager._POLLING_FREQUENCY_SECONDS)

    @staticmethod
    def _count_incidents(aggregated_incidents_data):
        total_incidents = 0
        for employee_id in aggregated_incidents_data:
            for priority in aggregated_incidents_data[employee_id]:
                total_incidents += aggregated_incidents_data[employee_id][priority][DataAggregator.COUNT_KEY]
        return total_incidents
