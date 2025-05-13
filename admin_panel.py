from tkinter import Tk, Button, Entry, Label, Listbox, Toplevel, END, messagebox
from sqlalchemy.orm import sessionmaker
from models import User

class Admin:
    def __init__(self, engine, system):
        self.engine = engine
        self.system = system
        self.Session = sessionmaker(bind=self.engine)
        self.root = Toplevel()
        self.root.title("Админ Панель")
        self.root.geometry("400x400")
        self.build()

    def build(self):
        Button(self.root, text="Создать бухгалтера", command=self.create_accountant_popup).pack(pady=5)
        Button(self.root, text="Выход", command=self.logout).pack(pady=5)

        Label(self.root, text="Список бухгалтеров:").pack(pady=5)
        self.listbox = Listbox(self.root)
        self.listbox.pack(fill='both', expand=True, padx=10)
        self.listbox.bind('<Double-1>', self.edit_selected_accountant)

        self.refresh_accountants()
        self.root.protocol("WM_DELETE_WINDOW", self.logout)
        self.root.mainloop()

    def refresh_accountants(self):
        self.listbox.delete(0, END)
        session = self.Session()
        accountants = session.query(User).filter_by(role="accountant").all()
        for acc in accountants:
            self.listbox.insert(END, f"{acc.id} - {acc.name}")
        session.close()

    def create_accountant_popup(self):
        popup = Toplevel(self.root)
        popup.title("Новый бухгалтер")

        Label(popup, text="Имя:").pack()
        name_entry = Entry(popup)
        name_entry.pack()

        Label(popup, text="Пароль:").pack()
        password_entry = Entry(popup, show="*")
        password_entry.pack()

        def submit():
            name, password = name_entry.get(), password_entry.get()
            if not (name and password):
                messagebox.showerror("Ошибка", "Все поля обязательны")
                return
            session = self.Session()
            session.add(User(name=name, password=password, role="accountant"))
            session.commit()
            session.close()
            popup.destroy()
            self.refresh_accountants()

        Button(popup, text="Создать", command=submit).pack(pady=5)

    def edit_selected_accountant(self, event):
        selected = self.listbox.get(self.listbox.curselection())
        acc_id = int(selected.split(" - ")[0])
        session = self.Session()
        acc = session.query(User).get(acc_id)
        session.close()
        if acc:
            self.edit_accountant_popup(acc)

    def edit_accountant_popup(self, acc):
        popup = Toplevel(self.root)
        popup.title(f"Изменить: {acc.name}")

        Label(popup, text="Имя:").pack()
        name_entry = Entry(popup)
        name_entry.insert(0, acc.name)
        name_entry.pack()

        Label(popup, text="Пароль:").pack()
        password_entry = Entry(popup, show="*")
        password_entry.insert(0, acc.password)
        password_entry.pack()

        def save_changes():
            session = self.Session()
            updated = session.query(User).get(acc.id)
            updated.name = name_entry.get()
            updated.password = password_entry.get()
            session.commit()
            session.close()
            popup.destroy()
            self.refresh_accountants()

        def delete_accountant():
            if messagebox.askyesno("Подтверждение", "Удалить этого бухгалтера?"):
                session = self.Session()
                session.query(User).filter_by(id=acc.id).delete()
                session.commit()
                session.close()
                popup.destroy()
                self.refresh_accountants()

        Button(popup, text="Сохранить", command=save_changes).pack(pady=5)
        Button(popup, text="Удалить", command=delete_accountant).pack(pady=5)

    def logout(self):
        self.root.destroy()
        self.system.show_login()