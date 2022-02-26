from model.incident_type import IncidentType
from model.priority import Priority


class DataAggregator:
    ''' Implements the aggregation business logic '''
    _INCIDENT_TYPE_KEY = 'type'
    _INCIDENTS_KEY = 'incidents'
    _PRIORITY_KEY = 'priority'
    _TIMESTAMP_KEY = 'timestamp'

    COUNT_KEY = 'count'

    @staticmethod
    def aggregate(employee_priority_data_map, raw_incidents_data, raw_identities_data):
        ''' Builds a new employee id - priority data map for each incident type and then merges into the existing total data map '''
        ip_employee_map = raw_identities_data
        for incident_type in raw_incidents_data:
            raw_incidents = raw_incidents_data[incident_type]
            new_employee_priority_data_map = DataAggregator._aggregate_incident_type(employee_priority_data_map, raw_incidents, ip_employee_map, incident_type)
            DataAggregator._merge_employee_priority_data_map(employee_priority_data_map, new_employee_priority_data_map)

    @staticmethod
    def _aggregate_incident_type(employee_priority_data_map, raw_incidents, ip_employee_map, incident_type):
        ''' Builds the appropriate incident records for the new employee id - priority data map '''
        new_employee_priority_data_map = {}
        for raw_incident in raw_incidents:
            employee_id = str(DataAggregator._resolve_incident_employee_id(raw_incident, ip_employee_map, incident_type))
            # None indicates that an employee id could not be resolved for an incident
            if employee_id is None:
                continue
            if employee_id not in new_employee_priority_data_map:
                new_employee_priority_data_map[employee_id] = DataAggregator._create_empty_priority_map()
            priority = raw_incident[DataAggregator._PRIORITY_KEY]
            if priority not in Priority.get_all():
                raise Exception(f'Unsupported priority: {priority}')
            new_employee_priority_data_map[employee_id][priority][DataAggregator.COUNT_KEY] += 1
            incident = dict(raw_incident)
            incident[DataAggregator._INCIDENT_TYPE_KEY] = incident_type
            new_employee_priority_data_map[employee_id][priority][DataAggregator._INCIDENTS_KEY].append(incident)
        return new_employee_priority_data_map

    @staticmethod
    def _create_empty_priority_map():
        ''' Initializes the data map for a new employee id '''
        return {priority: {
                DataAggregator.COUNT_KEY: 0,
                DataAggregator._INCIDENTS_KEY: []
                } for priority in Priority.get_all()}

    @staticmethod
    def _resolve_incident_employee_id(raw_incident, ip_employee_map, incident_type):
        if incident_type == IncidentType.DENIAL:
            return raw_incident['reported_by']
        elif incident_type == IncidentType.INTRUSION:
            return ip_employee_map[raw_incident['internal_ip']] if raw_incident['internal_ip'] in ip_employee_map else None
        elif incident_type == IncidentType.EXECUTABLE:
            return ip_employee_map[raw_incident['machine_ip']] if raw_incident['machine_ip'] in ip_employee_map else None
        elif incident_type == IncidentType.MISUSE:
            return raw_incident['employee_id']
        elif incident_type == IncidentType.UNAUTHORIZED:
            return raw_incident['employee_id']
        elif incident_type == IncidentType.PROBING:
            return ip_employee_map[raw_incident['ip']] if raw_incident['ip'] in ip_employee_map else None
        elif incident_type == IncidentType.OTHER:
            return ip_employee_map[raw_incident['identifier']] if raw_incident['identifier'] in ip_employee_map else None
        else:
            raise Exception(f'Unsupported incident type: {incident_type}')

    @staticmethod
    def _merge_employee_priority_data_map(map, update_map):
        ''' Merges the existing employee id - priority data map with the new data map '''
        employee_ids = set(list(map) + list(update_map))
        for employee_id in employee_ids:
            if employee_id not in map:
                map[employee_id] = update_map[employee_id]
                continue
            if employee_id not in update_map:
                continue
            for priority in Priority.get_all():
                map[employee_id][priority][DataAggregator.COUNT_KEY] += update_map[employee_id][priority][DataAggregator.COUNT_KEY]
                incidents = list(map[employee_id][priority][DataAggregator._INCIDENTS_KEY])
                update_incidents = list(update_map[employee_id][priority][DataAggregator._INCIDENTS_KEY])
                map[employee_id][priority][DataAggregator._INCIDENTS_KEY] = DataAggregator._merge_incidents(incidents, update_incidents)

    @staticmethod
    def _merge_incidents(incidents, update_incidents):
        ''' Merges the incident lists based on the timestamps, leveraging the fact that each list is already sorted by timestamp '''
        merged_incidents = []
        while len(incidents) > 0 and len(update_incidents) > 0:
            if incidents[0][DataAggregator._TIMESTAMP_KEY] < update_incidents[0][DataAggregator._TIMESTAMP_KEY]:
                merged_incidents.append(incidents.pop(0))
            else:
                merged_incidents.append(update_incidents.pop(0))
        if len(incidents) == 0:
            merged_incidents.extend(update_incidents)
        else:
            merged_incidents.extend(incidents)
        return merged_incidents
