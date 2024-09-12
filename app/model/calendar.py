from datetime import datetime, date, time
from app.services.util import generate_unique_id, reminder_not_found_error, slot_not_available_error, event_not_found_error, date_lower_than_today_error

class Reminder:
    EMAIL = "email"
    SYSTEM = "system"

    def __init__(self, date_time: datetime, type_: str = EMAIL):
        self.date_time = date_time
        self.type = type_

    def __str__(self):
        return f"Reminder on {self.date_time} of type {self.type}"


class Event:
    def __init__(self, title: str, description: str, date_: date, start_at: time, end_at: time, id: str = None):
        self.title = title
        self.description = description
        self.date_ = date_
        self.start_at = start_at
        self.end_at = end_at
        self.id = id if id else generate_unique_id()
        self.reminders = []

    def add_reminder(self, date_time, type_="email"):
        self.reminders.append(Reminder(date_time, type_))

    def delete_reminder(self, reminder_index: int):
        if 0 <= reminder_index < len(self.reminders):
            self.reminders.pop(reminder_index)
        else:
            reminder_not_found_error()

    def __str__(self):
        return f"ID: {self.id}\nEvent title: {self.title}\nDescription: {self.description}\nTime: {self.start_at} - {self.end_at}"


class Day:
    def __init__(self, date_: date):
        self.date_ = date_
        self.slots = {}
        self._init_slots()

    def _init_slots(self):
        for hour in range(24):
            for minute in range(0, 60, 15):
                self.slots[time(hour, minute)] = None

    def add_event(self, event_id: str, start_at: time, end_at: time):
        for slot in self.slots:
            if start_at <= slot < end_at:
                if self.slots[slot] is None:
                    self.slots[slot] = event_id
                else:
                    slot_not_available_error()

    def delete_event(self, event_id: str):
        deleted = False
        for slot, saved_id in self.slots.items():
            if saved_id == event_id:
                self.slots[slot] = None
                deleted = True
        if not deleted:
            event_not_found_error()

    def update_event(self, event_id: str, start_at: time, end_at: time):
        self.delete_event(event_id)
        self.add_event(event_id, start_at, end_at)


class Calendar:
    def __init__(self):
        self.days = {}
        self.events = {}

    def add_event(self, title: str, description: str, date_: date, start_at: time, end_at: time):
        if date_ < datetime.now().date():
            date_lower_than_today_error()

        if date_ not in self.days:
            self.days[date_] = Day(date_)

        event = Event(title, description, date_, start_at, end_at)
        self.days[date_].add_event(event.id, start_at, end_at)
        self.events[event.id] = event
        return event.id

    def add_reminder(self, event_id: str, date_time: datetime, type_: str):
        if event_id not in self.events:
            event_not_found_error()
        self.events[event_id].add_reminder(date_time, type_)

    def find_available_slots(self, date_: date):
        if date_ not in self.days:
            return []
        return [slot for slot, event_id in self.days[date_].slots.items() if event_id is None]

    def delete_event(self, event_id: str):
        if event_id not in self.events:
            event_not_found_error()

        event = self.events.pop(event_id)
        self.days[event.date_].delete_event(event_id)

    def update_event(self, event_id: str, title: str, description: str, date_: date, start_at: time, end_at: time):
        self.delete_event(event_id)
        return self.add_event(title, description, date_, start_at, end_at)

    def delete_reminder(self, event_id: str, reminder_index: int):
        if event_id not in self.events:
            event_not_found_error()
        self.events[event_id].delete_reminder(reminder_index)

    def list_reminders(self, event_id: str):
        if event_id not in self.events:
            event_not_found_error()
        return self.events[event_id].reminders

