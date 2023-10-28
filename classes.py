from datetime import datetime
from dataclasses import dataclass, field
from winotify import Notification, audio

@dataclass
class Task():
    type: str
    name: str
    deadline: datetime
    completed: bool = False
    toast: Notification = Notification(app_id="Task Tracker", title="Task Reminder", msg='', icon=r'D:\Python Projects\Assignment Tracker (Krutika)\notification_icon.png')
    notifications: bool = True

    def toggle_completed(self):
        self.completed = not self.completed
        
    def toggle_notifications(self):
        self.notifications = not self.notifications
    
    def alert(self, subject):
        if not self.completed and self.notifications:
            time_delta = self.deadline - datetime.now()
            total_seconds = int(time_delta.total_seconds())
            days, remaining_seconds = divmod(total_seconds, 86400)
            hours, _ = divmod(remaining_seconds, 3600)
            minutes, seconds = divmod(_, 60)
            
            if 5 > days:
                self.toast.msg = f"{subject}: {self.name} due in {days} {'days' if days != 1 else 'day'}, {hours} {'hours' if hours != 1 else 'hour'} and {minutes} {'minutes' if minutes != 1 else 'minute'}."
                self.toast.show()
    
    def __repr__(self) -> str:
        return f'{self.name} - {self.completed} - {self.notifications}'


@dataclass
class Subject:
    name: str
    tasks: list[Task] = field(default_factory=list)

    def add_tasks(self, task: Task):
        self.tasks.append(task)



