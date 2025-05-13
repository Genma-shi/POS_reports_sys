import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tkinter import Tk, Label, Entry, Button, messagebox
from models import Base, User
from admin_panel import Admin
from accountant_panel import Accountant

class System:
    def __init__(self):
        self.engine = self.init_system()
        self.Session = sessionmaker(bind=self.engine)
        self.root = Tk()
        self.root.title("ППО Система")
        self.root.geometry("400x300")
        self.build_login()
    
    def init_system(self):
        if not os.path.exists("data/db"):
            os.makedirs("data/db")
        engine = create_engine('sqlite:///data/db/ppo_system.db')
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()
        admin = session.query(User).filter_by(role="admin").first()
        if not admin:
            admin = User(name="admin", password="admin", role="admin")
            session.add(admin)
            session.commit()
        session.close()
        return engine

    def build_login(self):
        Label(self.root, text="Логин").pack(pady=5)
        login_entry = Entry(self.root)
        login_entry.pack(pady=5)

        Label(self.root, text="Пароль").pack(pady=5)
        password_entry = Entry(self.root, show="*")
        password_entry.pack(pady=5)

        Button(self.root, text="Войти", command=lambda: self.login(login_entry.get(), password_entry.get())).pack(pady=10)

    def login(self, login, password):
        session = self.Session()
        user = session.query(User).filter_by(name=login, password=password).first()
        session.close()

        if not user:
            messagebox.showerror("Ошибка", "Неправильный логин или пароль")
            return

        self.root.withdraw()
        if user.role == "admin":
            admin_win = Admin(self.engine, self)
        else:
            acc_win = Accountant(self.engine, user, self)

    def show_login(self):
        self.root.deiconify()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = System()
    app.run()