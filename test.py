import tkinter as tk
import serial
from tkinter import Text
from tkinter import *
from tkinter import messagebox

# Set up serial communication
ser = serial.Serial('COM4', 9600)


def login():
    username = entry1.get()
    password = entry2.get()
    if (username == "" and password == ""):
        messagebox.showinfo("Error", "Please enter both username and password")

    elif (username == "admin" and password == "password"):
        launchDashboard()

    else:
        messagebox.showinfo("Error", "Incorrect username or password")


def launchDashboard():
    def update_textbox():
        if ser.in_waiting:
            value = ser.readline()
            valueInString = value.decode('UTF-8').strip()
            text_widget.insert(tk.END, valueInString + '\n')
            text_widget.see(tk.END)  # Scroll to the end
        dashboard.after(100, update_textbox)  # Schedule the function to be called again after 100 ms

    dashboard = tk.Tk()
    dashboard.title("Dashboard")
    dashboard.geometry('800x800')

    # Create a Text widget to display messages
    text_widget = Text(dashboard, wrap='word', width=80, height=40)
    text_widget.pack(padx=20, pady=20)

    # Start the periodic check for new messages
    dashboard.after(100, update_textbox)

    dashboard.mainloop()


root = Tk()
root.title("LoRa Based Messagin System - Login")
root.geometry('400x250')
root.resizable(False, False)

global entry1
global entry2

Label(root, text="Username").place(x=20, y=20)
Label(root, text="Password").place(x=20, y=100)

entry1 = Entry(root, bd=5)
entry1.place(x=140, y=20)

entry2 = Entry(root, bd=5)
entry2.place(x=140, y=100)

Button(root, text="Login", command=login, height=2, width=13, bd=6).place(x=150, y=160)

root.mainloop()
