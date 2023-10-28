import gooeypie as gp
from classes import Task, Subject
import pystray
from PIL import Image
import pickle
import threading
from datetime import datetime, date

version = 0.1

subjects = ['PRG', 'DBS', 'OSM', 'CIS', 'NWK', 'OSL']
task_types = ['Lab', 'Assignment', 'Quiz', 'Project']
table_headings = ['Subject', 'Task', 'Due Date', 'Completed']

data = None


def load_data_file():
    global data
    try:
        with open('data', 'rb') as f:
            data = pickle.load(f)
    except FileNotFoundError as e:
        data = [Subject(x) for x in subjects]
    
    add_task_to_table()
    add_task_to_menu()

def save_data_file():
    with open('data', 'wb') as f:
        pickle.dump(data, f)
    
def show_task_add_layout(event):
    add_task_window.show_on_top()

def add_task_to_data(event):
    global data
    if not all((task_type_dd.selected, task_name_inp.text, due_date.date)):
        app.alert("Error", "Please select/populate all values", 'error')
        return
    delta = due_date.date - datetime.now().date()
    delta = delta.days
    if delta < 0:
        app.alert("Error", "Selected due date in the past, please correct!", "error")
        return
    for subject in data:
        if subject.name == subject_dd.selected:
            subject.add_tasks(Task(task_type_dd.selected, task_name_inp.text, datetime.combine(due_date.date, datetime.max.time())))


    add_task_to_menu()
    add_task_to_table()
    save_data_file()
    clear_fields()

def add_task_to_table():
    table_data = []
    for subject in data:
        if subject.tasks:
            for task in subject.tasks:
                table_data.append([subject.name, task.name, task.deadline.strftime('%d-%b-%y'), 'Yes' if task.completed else 'No'])
    tracker_table.data = table_data
    
def add_task_to_menu():
    final = []
    for subject in data:
        temp = []
        if subject.tasks:
            for task in subject.tasks:
                notifications = pystray.MenuItem('Notifications', action=lambda tray, item, task=task: on_click(item=item, task=task), checked=lambda _, task=task: task.notifications)
                completed = pystray.MenuItem('Completed', action=lambda tray, item, task=task: on_click(item=item, task=task), checked=lambda _, task=task: task.completed)
                task_menu = pystray.MenuItem(task.name, pystray.Menu(completed, notifications))
                temp.append(task_menu)
            subject_menu = pystray.MenuItem(subject.name, pystray.Menu(*temp))
            final.append(subject_menu)
            final_menu = menu_items[0:1] + final + menu_items[1:]
            tray.menu = pystray.Menu(*final_menu)
            tray.update_menu()

def clear_fields():
    subject_dd.deselect()
    task_type_dd.deselect()
    task_name_inp.clear()
    due_date.clear()

def check_due_date():
    for subject in data:
        for task in subject.tasks:
            task.alert(subject.name)


def on_click(**kwargs):
    match str(kwargs['item']):
        case 'Open':
            app._root.deiconify()
        case 'Exit':
            print('Exit')
            app.exit()
        case 'Completed':
            kwargs['task'].toggle_completed()
            add_task_to_table()
            save_data_file()
            tray.update_menu()
            app.update()
        case 'Notifications':
            kwargs['task'].toggle_notifications()
            add_task_to_table()
            save_data_file()
            tray.update_menu()
            app.update()


def minimize():
    reply = app.confirm_yesnocancel('Sure?', 'Do you want to close the app?\n"Yes" to close.\n"No" to minimize.\n"Cancel" to stay on the app.', 'info')
    match reply:
        case True:
            app.exit()
        case False:
            app._root.withdraw()
        case _:
            return


app = gp.GooeyPieApp(f'Task Tracker v{version}')
app.width = 300
app.height = 300
app.set_icon('./tray_icon.png')

menu_items = [
    pystray.MenuItem('Open', lambda tray, item: on_click(item=item)),
    pystray.MenuItem('Exit', lambda tray, item: on_click(item=item))
]
menu = pystray.Menu(*menu_items)

icon = Image.open('./tray_icon.png')
tray = pystray.Icon(name='Assignment tracker', icon=icon, title='Assignment tracker', menu=menu)


tracker_table = gp.Table(app, table_headings)
tracker_table.set_column_alignments(*['center'] * len(table_headings))

add_new_task_btn = gp.Button(app, 'Add Task', show_task_add_layout)

add_task_window = gp.Window(app, 'Add Tasks')

subject_lbl = gp.Label(add_task_window, 'Subject')
subject_dd = gp.Dropdown(add_task_window, subjects)

task_type_lbl = gp.Label(add_task_window, 'Task Type')
task_type_dd = gp.Dropdown(add_task_window, task_types)

task_name_lbl = gp.Label(add_task_window, 'Task Name')
task_name_inp = gp.Input(add_task_window)

due_date_lbl = gp.Label(add_task_window, 'Due Date')
due_date = gp.Date(add_task_window)
due_date.year_range = [2023, 2027]
due_date.set_selector_order('DMY')

add_task_btn = gp.Button(add_task_window, 'Save', add_task_to_data)

app.set_grid(11, 5)
app.add(tracker_table, 1, 1, row_span=10, column_span=5)
app.add(add_new_task_btn, 11, 1, column_span=5, align='center')

add_task_window.set_grid(5, 2)
add_task_window.add(subject_lbl, 1, 1)
add_task_window.add(subject_dd, 2, 1)
add_task_window.add(task_type_lbl, 1, 2)
add_task_window.add(task_type_dd, 2, 2)
add_task_window.add(task_name_lbl, 3, 1)
add_task_window.add(task_name_inp, 4, 1)
add_task_window.add(due_date_lbl, 3, 2)
add_task_window.add(due_date, 4, 2)
add_task_window.add(add_task_btn, 5, 1, column_span=2, align='center')

app.set_interval(1000*10, lambda: threading.Thread(target=check_due_date).start())

app.on_open(load_data_file)
app.on_close(minimize)
threading.Thread(target=lambda: tray.run(), daemon=True).start()
app.run()