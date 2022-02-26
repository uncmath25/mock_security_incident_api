class IncidentType:
    DENIAL = 'denial'
    INTRUSION = 'intrusion'
    EXECUTABLE = 'executable'
    MISUSE = 'misuse'
    UNAUTHORIZED = 'unauthorized'
    PROBING = 'probing'
    OTHER = 'other'

    @staticmethod
    def get_all():
        return (
            IncidentType.DENIAL,
            IncidentType.INTRUSION,
            IncidentType.EXECUTABLE,
            IncidentType.MISUSE,
            IncidentType.UNAUTHORIZED,
            IncidentType.PROBING,
            IncidentType.OTHER
        )
