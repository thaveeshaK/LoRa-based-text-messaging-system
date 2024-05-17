from tkinter import *
from tkinter import messagebox

def login():
    username=entry1.get()
    password=entry2.get()
    if (username == "" and password == ""):
        messagebox.showinfo("Error", "Please enter both username and password")

    elif(username=="" and password == ""):
        messagebox.showinfo("", "Login Success!")

    else:
        messagebox.showinfo("Error", "Incorrect username or password")
root = Tk()
root.title("LoRa Based Messagin System - Login")
root.geometry('500x500')

global entry1
global entry2

Label(root,text="Username").place(x=20,y=20)
Label(root,text="Password").place(x=20,y=100)

entry1=Entry(root,bd=5)
entry1.place(x=140,y=20)

entry2=Entry(root,bd=5)
entry2.place(x=140,y=100)

Button(root,text="Login", command=login(),height=2, width=13, bd=6).place(x=150,y=160)

root.mainloop()

