import tkinter as tk
from tkinter import Text, Entry, Button, Label, messagebox
import hashlib

ser = None  # Will be initialized later based on the end (transmitter or receiver)

def login():
    global ser
    username = entry1.get()
    password = entry2.get()

    if username == "" or password == "":
        messagebox.showinfo("Error", "Please enter both username and password")
    else:
        # Read the credentials from the file
        try:
            with open("C:/credentials.txt", "r") as file:
                for line in file:
                    stored_username, stored_hashed_password = line.strip().split(":")
                    if username == stored_username:
                        # Hash the input password
                        hashed_password = hashlib.sha256(password.encode()).hexdigest()
                        # Compare the hashed passwords
                        if hashed_password == stored_hashed_password:
                            messagebox.showinfo("Success", "Login successful")
                            launchDashboard()
                            return
                        else:
                            messagebox.showinfo("Error", "Incorrect password")
                            return
                # If username not found
                messagebox.showinfo("Error", "Username not found")
        except IOError:
            messagebox.showerror("Error", "Credentials file not found")

def update_password():
    username = entry3.get()
    old_password = entry4.get()
    new_password = entry5.get()

    if username == "" or old_password == "" or new_password == "":
        messagebox.showinfo("Error", "Please enter username, old password, and new password")
    else:
        try:
            with open("C:/credentials.txt", "r") as file:
                lines = file.readlines()
            with open("C:/credentials.txt", "w") as file:
                updated = False
                for line in lines:
                    stored_username, stored_hashed_password = line.strip().split(":")
                    if username == stored_username:
                        # Hash the input old password
                        hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
                        if hashed_old_password == stored_hashed_password:
                            # Hash the input new password
                            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
                            file.write(f"{username}:{hashed_new_password}\n")
                            updated = True
                            break
                        else:
                            messagebox.showinfo("Error", "Incorrect old password")
                            return
                if not updated:
                    messagebox.showinfo("Error", "Username not found")
                else:
                    messagebox.showinfo("Success", "Password updated successfully")
        except IOError:
            messagebox.showerror("Error", "Credentials file not found")

def launchDashboard():
    def update_textbox():
        global ser
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

    def open_update_password_window():
        # Function to open the update password window
        update_password_window = tk.Toplevel(dashboard)
        update_password_window.title("Update Password")

        Label(update_password_window, text="Username").grid(row=0, column=0)
        Label(update_password_window, text="Old Password").grid(row=1, column=0)
        Label(update_password_window, text="New Password").grid(row=2, column=0)

        entry_username = Entry(update_password_window)
        entry_username.grid(row=0, column=1)
        entry_old_password = Entry(update_password_window, show='*')
        entry_old_password.grid(row=1, column=1)
        entry_new_password = Entry(update_password_window, show='*')
        entry_new_password.grid(row=2, column=1)

        Button(update_password_window, text="Update Password",
               command=lambda: update_password_from_window(entry_username.get(), entry_old_password.get(),
                                                            entry_new_password.get())).grid(row=3, column=0, columnspan=2)

    def update_password_from_window(username, old_password, new_password):
        # Function to update password from the update password window
        if username == "" or old_password == "" or new_password == "":
            messagebox.showinfo("Error", "Please enter username, old password, and new password")
        else:
            try:
                with open("C:/credentials.txt", "r") as file:
                    lines = file.readlines()
                with open("C:/credentials.txt", "w") as file:
                    updated = False
                    for line in lines:
                        stored_username, stored_hashed_password = line.strip().split(":")
                        if username == stored_username:
                            # Hash the input old password
                            hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
                            if hashed_old_password == stored_hashed_password:
                                # Hash the input new password
                                hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
                                file.write(f"{username}:{hashed_new_password}\n")
                                updated = True
                                break
                            else:
                                messagebox.showinfo("Error", "Incorrect old password")
                                return
                    if not updated:
                        messagebox.showinfo("Error", "Username not found")
                    else:
                        messagebox.showinfo("Success", "Password updated successfully")
            except IOError:
                messagebox.showerror("Error", "Credentials file not found")

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

    # Create a Button to update password
    update_password_button = Button(input_frame, text="Update Password", command=open_update_password_window)
    update_password_button.pack(side=tk.RIGHT)

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
entry1 = Entry(root, bd=5)
entry1.place(x=140, y=20)

entry2 = Entry(root, bd=5, show='*')
entry2.place(x=140, y=100)

Button(root, text="Login", command=login, height=2, width=13, bd=6).place(x=150, y=160)

Label(root, text="Username").place(x=450, y=20)
Label(root, text="Old Password").place(x=450, y=70)
Label(root, text="New Password").place(x=450, y=120)

entry3 = Entry(root, bd=5)
entry3.place(x=570, y=20)

entry4 = Entry(root, bd=5, show='*')
entry4.place(x=570, y=70)

entry5 = Entry(root, bd=5, show='*')
entry5.place(x=570, y=120)

Button(root, text="Update Password", command=update_password, height=2, width=15, bd=6).place(x=590, y=160)

root.mainloop()

