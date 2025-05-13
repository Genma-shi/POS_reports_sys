import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from io import BytesIO
from models import Transaction, ImportedFile
from utils import *

class Accountant:
    def __init__(self, engine, user, system):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)
        self.user = user
        self.system = system
        self.window = tk.Toplevel()
        self.window.title("Панель Бухгалтера")
        self.window.geometry("500x400")
        self.build_main()
        self.window.protocol("WM_DELETE_WINDOW", self.logout)

    def build_main(self):
        tk.Label(self.window, text=f"Добро пожаловать, {self.user.name}", font=("Arial", 12)).pack(pady=10)

        # 🔄 Кнопка для импорта файла прямо из главного окна
        tk.Button(self.window, text="📤 Импортировать файл", command=self.import_file).pack(pady=10)

        tk.Button(self.window, text="Работа с файлами", command=self.open_file_manager).pack(pady=10)
        tk.Button(self.window, text="Экспорт из базы", command=self.export_from_db).pack(pady=10)
        tk.Button(self.window, text="Выход", command=self.logout).pack(pady=10)

    def logout(self):
        self.window.destroy()
        self.system.show_login()

    def open_file_manager(self):
        window = tk.Toplevel(self.window)
        window.title("Управление файлами")
        window.geometry("600x500")

        tk.Label(window, text="Загруженные файлы:", font=("Arial", 10)).pack(pady=5)
        self.file_listbox = tk.Listbox(window, height=10, width=70)
        self.file_listbox.pack()

        self.refresh_file_list()

        tk.Button(window, text="📤 Импортировать файл", command=self.import_file).pack(pady=5)
        tk.Button(window, text="🔍 Просмотр / Редактирование", command=self.view_file).pack(pady=5)
        tk.Button(window, text="📁 Экспортировать", command=self.export_file).pack(pady=5)
        tk.Button(window, text="🗑 Удалить файл", command=self.delete_file).pack(pady=5)

    def refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        session = self.Session()
        files = session.query(ImportedFile).all()
        for f in files:
            self.file_listbox.insert(tk.END, f"{f.id}: {f.filename} ({f.uploaded_at.strftime('%Y-%m-%d %H:%M')})")
        session.close()

    def import_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not path:
            return

        try:
            df = pd.read_excel(path)
            required_cols = ["ID", "DeviceCode", "OperDateTime", "Curr", "Amnt", "Card_Number"]
            if not all(col in df.columns for col in required_cols):
                messagebox.showerror("Ошибка", "Файл должен содержать колонки: ID, DeviceCode, OperDateTime, Curr, Amnt, Card_Number")
                return

            session = self.Session()
            with open(path, "rb") as f:
                file_data = f.read()
            imported = ImportedFile(filename=path.split("/")[-1], data=file_data)
            session.add(imported)
            session.flush()

            for _, row in df.iterrows():
                transaction = Transaction(
                    device_code=str(row["DeviceCode"]),
                    op_date_time=datetime.strptime(str(row["OperDateTime"]), "%Y-%m-%d %H:%M:%S"),
                    curr=str(row["Curr"]),
                    amt=float(row["Amnt"]),
                    card_number=str(row["Card_Number"]).replace(".0", ""),
                    file_id=imported.id
                )
                session.add(transaction)
            session.commit()
            session.close()
            messagebox.showinfo("Успех", "Файл импортирован")
            self.refresh_file_list()
        except Exception as e:
            session.rollback()
            session.close()
            messagebox.showerror("Ошибка", f"Не удалось импортировать файл:\n{e}")

    def view_file(self):
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите файл")
            return

        index = int(self.file_listbox.get(selected[0]).split(":")[0])
        session = self.Session()
        file = session.query(ImportedFile).get(index)
        if not file:
            session.close()
            messagebox.showerror("Ошибка", "Файл не найден")
            return

        try:
            df = pd.read_excel(BytesIO(file.data)) 
            top = tk.Toplevel(self.window)
            top.title(file.filename)
            tree = ttk.Treeview(top)
            tree.pack(expand=True, fill=tk.BOTH)

            tree["columns"] = list(df.columns)
            tree["show"] = "headings"

            for col in df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            for _, row in df.iterrows():
                tree.insert("", tk.END, values=list(row))

            session.close()
        except Exception as e:
            session.close()
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def export_file(self):
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите файл")
            return

        index = int(self.file_listbox.get(selected[0]).split(":")[0])
        session = self.Session()
        file = session.query(ImportedFile).get(index)
        if not file:
            session.close()
            messagebox.showerror("Ошибка", "Файл не найден")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if not save_path:
            session.close()
            return

        try:
            with open(save_path, "wb") as f:
                f.write(file.data)
            messagebox.showinfo("Успех", "Файл экспортирован")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
        finally:
            session.close()

    def delete_file(self):
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите файл")
            return

        index = int(self.file_listbox.get(selected[0]).split(":")[0])
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить файл?")
        if not confirm:
            return

        session = self.Session()
        file = session.query(ImportedFile).get(index)
        if file:
            session.delete(file)
            session.commit()
            messagebox.showinfo("Удалено", "Файл удалён")
            self.refresh_file_list()
        else:
            messagebox.showerror("Ошибка", "Файл не найден")
        session.close()

    def export_from_db(self):
        window = tk.Toplevel(self.window)
        window.title("Экспорт из базы данных")
        window.geometry("400x300")

        tk.Label(window, text="Дата от (ГГГГ-ММ-ДД):").pack()
        entry_date_from = tk.Entry(window)
        entry_date_from.pack()

        tk.Label(window, text="Дата до (ГГГГ-ММ-ДД):").pack()
        entry_date_to = tk.Entry(window)
        entry_date_to.pack()

        tk.Label(window, text="Код устройства:").pack()
        entry_device = tk.Entry(window)
        entry_device.pack()

        tk.Label(window, text="Номер карты:").pack()
        entry_card = tk.Entry(window)
        entry_card.pack()

        def do_export():
            session = self.Session()
            try:
                # 1. Получаем курсы валют
                rates = get_exchange_rates()

                # 2. Запрашиваем данные из БД (с фильтрацией по введённым полям)
                query = session.query(Transaction)

                date_from = entry_date_from.get()
                date_to = entry_date_to.get()
                device_code = entry_device.get()
                card_number = entry_card.get()

                if date_from:
                    query = query.filter(Transaction.op_date_time >= datetime.strptime(date_from, "%Y-%m-%d"))
                if date_to:
                    query = query.filter(Transaction.op_date_time <= datetime.strptime(date_to, "%Y-%m-%d"))
                if device_code:
                    query = query.filter(Transaction.device_code == device_code)
                if card_number:
                    query = query.filter(Transaction.card_number == card_number)

                results = query.all()

                # 3. Преобразуем в DataFrame
                df = pd.DataFrame([{
                    "ID": r.id,
                    "DeviceCode": r.device_code or "",
                    "OperDateTime": r.op_date_time.strftime("%Y-%m-%d %H:%M:%S") if r.op_date_time else "",
                    "Curr": r.curr or "KGS",
                    "Amnt": float(r.amt) if r.amt is not None else 0,
                    "Card_Number": r.card_number or ""
                } for r in results])

                # 4. Добавим столбец с пересчётом в KGS
                def convert_to_kgs(row):
                    try:
                        amount = float(row.get("Amnt", 0))  # безопасно приводим к числу
                        currency = row.get("Curr", "KGS")
                        rate = rates.get(currency, 1.0)  # если курс не найден, умножаем на 1
                        return round(amount * rate, 2)
                    except Exception as e:
                        print(f"Ошибка при конвертации строки {row}: {e}")
                        return 0

                df["Amnt_in_KGS"] = df.apply(convert_to_kgs, axis=1)

                # 5. Сохраняем в Excel
                save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
                if save_path:
                    df.to_excel(save_path, index=False)
                    messagebox.showinfo("Успешно", f"Файл экспортирован: {save_path}")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")

        tk.Button(window, text="Экспортировать", command=do_export).pack(pady=10)
