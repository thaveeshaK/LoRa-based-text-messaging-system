import tkinter as tk
from tkinter import Text, Entry, Button, Label, messagebox
import serial
import hashlib


# Function to hash a password
def hash_password(password):
    # Hash the password using SHA-256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password


# Set up serial communication
ser = None  # Will be initialized later based on the end (transmitter or receiver)

# Modify this with the hashed password stored in your system
stored_hashed_password = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"


def login():
    username = entry1.get()
    password = entry2.get()

    # Hash the entered password
    hashed_entered_password = hash_password(password)

    if username == "" or password == "":
        messagebox.showinfo("Error", "Please enter both username and password")
    elif username == "admin" and hashed_entered_password == stored_hashed_password:
        launchDashboard()
    else:
        messagebox.showinfo("Error", "Incorrect username or password")


def launchDashboard():
    def update_textbox():
        if ser and ser.in_waiting:
            value = ser.readline()
            valueInString = value.decode('UTF-8').strip()
            text_widget.insert(tk.END, valueInString + '\n')
            text_widget.see(tk.END)  # Scroll to the end
        dashboard.after(100, update_textbox)  # Schedule the function to be called again after 100 ms

    def send_message():
        message = message_entry.get()
        if message:
            # Transmit the message over serial
            if ser:
                ser.write(message.encode('UTF-8'))
            # Update the GUI with the sent message
            message_entry.delete(0, tk.END)
            text_widget.insert(tk.END, "Sent: " + message + '\n')
            text_widget.see(tk.END)

    dashboard = tk.Tk()
    dashboard.title("Dashboard")
    dashboard.geometry('800x600')

    # Create a Text widget to display messages
    text_widget = Text(dashboard, wrap='word', width=80, height=30)
    text_widget.pack(padx=20, pady=20)

    # Create a frame to hold the entry and send button
    input_frame = tk.Frame(dashboard)
    input_frame.pack(padx=20, pady=10, fill=tk.X, side=tk.TOP, anchor=tk.CENTER)

    # Create an Entry widget for composing messages
    message_entry = Entry(input_frame, width=70)
    message_entry.pack(side=tk.LEFT)

    # Create a Button to send messages
    send_button = Button(input_frame, text="Send", command=send_message)
    send_button.pack(side=tk.LEFT, padx=(10, 0))

    # Start the periodic check for new messages
    dashboard.after(100, update_textbox)

    dashboard.mainloop()


root = tk.Tk()
root.title("LoRa Based Messaging System - Login")
root.geometry('400x250')
root.resizable(False, False)

Label(root, text="Username").place(x=20, y=20)
Label(root, text="Password").place(x=20, y=100)

entry1 = Entry(root, bd=5)
entry1.place(x=140, y=20)

entry2 = Entry(root, bd=5, show='*')
entry2.place(x=140, y=100)

Button(root, text="Login", command=login, height=2, width=13, bd=6).place(x=150, y=160)

root.mainloop()
