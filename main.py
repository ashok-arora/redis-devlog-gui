import redis
import PySimpleGUI as sg
from datetime import date, timedelta, datetime


def layout(r, today):
    l = r.lrange(today, 0, -1)

    layout = [
        [sg.Text("store devlogs for each day")],
        [   sg.Button("P"),
            sg.Input(key="-IN-", size=(20, 1), default_text=today, enable_events=True, justification='c'),
            sg.Button("N"),
            sg.CalendarButton(
                "Choose date",
                close_when_date_chosen=True,
                target="-IN-",
                no_titlebar=False,
                format="%d.%m.%Y",
            ),
        ],
        [sg.Listbox(l, key="-list-", size=(60, 10), enable_events=True)],
        [sg.Button("Add"), sg.Button("Modify"), sg.Button("Delete"), sg.Exit()],
    ]
    window = sg.Window("devlog", layout, size=(600, 400), element_justification="c")
    return window


def add_item(r, key):
    layout = [
        [sg.Text("Enter text: ")],
        [sg.InputText()],
        [sg.Button("Apply"), sg.Button("Exit")],
    ]
    window = sg.Window("Add record", layout, finalize=True, modal=True)
    while True:
        event, values = window.read()

        if event in ("Exit", sg.WIN_CLOSED):
            break

        elif event == "Apply":
            if values[0] == "":
                sg.popup(
                    "Blank input is not acceptable. Enter something and try again!",
                    title="Error",
                )
            else:
                r.rpush(key, values[0])
                sg.popup("Record added successfully")
                break
    window.close()


def modify_item(r, key, item):
    layout = [
        [sg.Text("Enter text: ")],
        [sg.InputText(default_text=item)],
        [sg.Button("Apply"), sg.Button("Exit")],
    ]
    window = sg.Window("Add record", layout, finalize=True, modal=True)
    while True:
        event, values = window.read()

        if event in ("Exit", sg.WIN_CLOSED):
            break

        elif event == "Apply":
            if values[0] == "":
                sg.popup(
                    "Blank input is not acceptable. Enter something and try again!",
                    title="Error",
                )
            else:
                l = r.lrange(key, 0, -1)
                r.lset(key, l.index(item), str.encode(values[0]))
                sg.popup("Record added successfully")
                break
    window.close()



def delete_item(r, key, item):
    r.lrem(name=key, count=1, value=str.encode(item))
    sg.popup("The selected item has been deleted.", title="Item deleted")


def main():
    sg.theme("Reddit")
    sg.set_options(font=("Montserrat", 10))

    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    window = layout(r, date.today().strftime("%d.%m.%Y"))
    while True:
        event, values = window.read()
        if event in ("Exit", sg.WIN_CLOSED):
            break

        if event in "P":
            values["-IN-"] = (datetime.strptime(values["-IN-"], "%d.%m.%Y") - timedelta(days=1)).strftime("%d.%m.%Y")
            window["-IN-"].update(values["-IN-"])
            l = r.lrange(values["-IN-"], 0, -1)
            window["-list-"].update(l)

        if event in "N":
            values["-IN-"] = (datetime.strptime(values["-IN-"], "%d.%m.%Y") + timedelta(days=1)).strftime("%d.%m.%Y")
            window["-IN-"].update(values["-IN-"])
            l = r.lrange(values["-IN-"], 0, -1)
            window["-list-"].update(l)

        if event in "-IN-":
            l = r.lrange(values["-IN-"], 0, -1)
            window["-list-"].update(l)

        if event in "Add":
            add_item(r, values["-IN-"])
            l = r.lrange(values["-IN-"], 0, -1)
            window["-list-"].update(l)

        if event in "Modify":
            if not values["-list-"]:
                sg.popup(
                    "Select an item from the list and try again!",
                    title="No item selected",
                )
            else:
                modify_item(r, values["-IN-"], values["-list-"][0])
                l = r.lrange(values["-IN-"], 0, -1)
                window["-list-"].update(l)

        if event == "Delete":
            if not values["-list-"]:
                sg.popup(
                    "Select an item from the list and try again!",
                    title="No item selected",
                )
            else:
                delete_item(r, values["-IN-"], values["-list-"][0])
                l = r.lrange(values["-IN-"], 0, -1)
                window["-list-"].update(l)
    window.close()


if __name__ == "__main__":
    main()
