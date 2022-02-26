from flask import Flask
import os

from controller.poll_manager import PollManager
from utility.raw_incidents_importer import RawIncidentsImporter


webserver = Flask(__name__)

API_BASE_URL = os.environ.get('BASE_URL')
API_USERNAME = os.environ.get('USERNAME')
API_PASSWORD = os.environ.get('PASSWORD')
raw_incidents_importer = RawIncidentsImporter(API_BASE_URL, API_USERNAME, API_PASSWORD)
poll_manager = PollManager(raw_incidents_importer)
poll_manager.poll()


# Displays health metrics on how successful raw incident importing and aggregation has been
@webserver.route('/health', methods=['GET'])
def health():
    return poll_manager.get_health_data()


# Returns the aggregated incident data grouped by employee id and priority
@webserver.route('/incidents', methods=['GET'])
def incidents():
    return poll_manager.get_aggregated_incidents_data()


if __name__ == '__main__':
    webserver.run(host='0.0.0.0', debug=True)
