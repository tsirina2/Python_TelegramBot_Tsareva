class Calendar:
    def __init__(self):
        self.events = {}

    def create_event(self, event_name, event_date, event_time, event_details):
        event_id = len(self.events) + 1
        event = {
            "id": event_id,
            "name": event_name,
            "date": event_date,
            "time": event_time,
            "details": event_details
        }
        self.events[event_id] = event
        return event_id
