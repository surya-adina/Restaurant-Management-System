import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
from decimal import Decimal
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "appuser",
    "password": "password123",
    "database": "restaurant_db"
}

MAROON = "#7A0019"
MAROON_DARK = "#5c0013"
DARK = "#2f3542"
BG = "#f5f6fa"
WHITE = "#ffffff"
GREEN = "#0984e3"
RED = "#d63031"
ORANGE = "#f39c12"
GRAY = "#636e72"

class Database:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            messagebox.showerror("Database Error", f"Could not connect to MySQL:\n{e}\n\nCheck DB_CONFIG in app.py.")
            raise

    def query(self, sql, params=None, fetch=False):
        try:
            if not self.conn.is_connected():
                self.connect()
            cur = self.conn.cursor(dictionary=True)
            cur.execute(sql, params or ())
            if fetch:
                rows = cur.fetchall()
                cur.close()
                return rows
            self.conn.commit()
            last_id = cur.lastrowid
            cur.close()
            return last_id
        except Error as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", str(e))
            return None

class RestaurantApp:
    def __init__(self, root):
        self.bg_image = Image.open("bg.jpg")
        self.bg_image = self.bg_image.resize((1000, 650))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.root = root
        self.root.title("Restaurant Management System")
        self.root.geometry("1100x700")
        self.root.minsize(1000, 650)
        self.root.configure(bg=BG)
        self.db = Database()
        self.current_user = None
        self.setup_styles()
        self.show_login()
    def set_background(self):
            if self.bg_photo:
                bg_label = tk.Label(self.root, image=self.bg_photo)
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                bg_label.lower()
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=WHITE, foreground=DARK, rowheight=30, fieldbackground=WHITE, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#edf0f5", foreground=DARK)
        style.map("Treeview", background=[("selected", MAROON)])
        style.configure("TCombobox", padding=5)

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def button(self, parent, text, command, width=18, color=MAROON):
        return tk.Button(parent, text=text, command=command, width=width, bg=color, fg="white", activebackground=MAROON_DARK, activeforeground="white", font=("Arial", 10, "bold"), relief="flat", pady=8, cursor="hand2")

    def label(self, parent, text, size=11, bold=False, bg=WHITE, fg=DARK):
        weight = "bold" if bold else "normal"
        return tk.Label(parent, text=text, bg=bg, fg=fg, font=("Arial", size, weight))

    def show_login(self):
        self.clear()
        self.set_background()
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)
        card = tk.Frame(outer, bg=WHITE, padx=50, pady=38, highlightbackground="#dcdde1", highlightthickness=1)
        card.place(relx=0.5, rely=0.48, anchor="center")
        tk.Label(card, text="🍽", fg=MAROON, bg=WHITE, font=("Arial", 42, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 8))
        tk.Label(card, text="RESTAURANT MANAGEMENT SYSTEM", fg=MAROON, bg=WHITE, font=("Arial", 22, "bold")).grid(row=1, column=0, columnspan=2, pady=(0, 28))
        tk.Label(card, text="Username", bg=WHITE, font=("Arial", 11, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        username = tk.Entry(card, width=32, font=("Arial", 11), relief="solid", bd=1)
        username.grid(row=2, column=1, pady=8, ipady=7)
        tk.Label(card, text="Password", bg=WHITE, font=("Arial", 11, "bold")).grid(row=3, column=0, sticky="w", pady=8)
        password = tk.Entry(card, width=32, show="*", font=("Arial", 11), relief="solid", bd=1)
        password.grid(row=3, column=1, pady=8, ipady=7)

        def login():
            rows = self.db.query("SELECT * FROM users WHERE username=%s AND password=%s", (username.get().strip(), password.get().strip()), fetch=True)
            if rows:
                self.current_user = rows[0]
                self.show_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")

        self.button(card, "Login", login, 25).grid(row=4, column=0, columnspan=2, pady=25)
        tk.Label(card, text="Default: admin/admin123 or staff/staff123", bg=WHITE, fg=GRAY).grid(row=5, column=0, columnspan=2)
        tk.Label(outer, text="© 2026 Restaurant Management System", bg=BG, fg=GRAY, font=("Arial", 9)).pack(side="bottom", pady=15)
        username.focus()
        self.root.bind("<Return>", lambda event: login())

    def show_dashboard(self):
        self.clear()
        self.root.bind("<Return>", lambda event: None)
        sidebar = tk.Frame(self.root, bg=MAROON, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        main = tk.Frame(self.root, bg=BG)
        main.pack(side="right", fill="both", expand=True)
        tk.Label(sidebar, text="RMS", bg=MAROON, fg="white", font=("Arial", 26, "bold")).pack(pady=(28, 5))
        tk.Label(sidebar, text=f"{self.current_user['username']} ({self.current_user['role']})", bg=MAROON, fg="#f1f2f6", font=("Arial", 10)).pack(pady=(0, 22))

        role = self.current_user["role"].lower()
        items = [
            ("🍽  Menu Items", self.menu_window),
            ("👥  Customers", self.customers_window),
            ("🪑  Tables", self.tables_window),
            ("🧾  Orders", self.orders_window),
            ("🔥  Current Orders", self.current_orders_window),
            ("💳  Billing", self.billing_window),
        ]
        if role == "admin":
            items.append(("📊  Reports", self.reports_window))
        items.append(("🚪  Logout", self.show_login))

        for text, cmd in items:
            tk.Button(sidebar, text=text, command=cmd, bg=MAROON, fg="white", activebackground=MAROON_DARK, relief="flat", anchor="w", padx=24, pady=13, font=("Arial", 11, "bold"), cursor="hand2").pack(fill="x")

        header = tk.Frame(main, bg=BG)
        header.pack(fill="x", padx=35, pady=(25, 10))
        tk.Label(header, text="RESTAURANT MANAGEMENT SYSTEM", bg=BG, fg=MAROON, font=("Arial", 24, "bold")).pack(side="left")
        tk.Label(header, text="Welcome, " + self.current_user['username'].title(), bg=BG, fg=DARK, font=("Arial", 12, "bold")).pack(side="right")

        stats = self.get_dashboard_stats()
        stat_frame = tk.Frame(main, bg=BG)
        stat_frame.pack(fill="x", padx=35, pady=10)
        self.stat_card(stat_frame, "Open Orders", stats["open_orders"], "🧾", 0)
        self.stat_card(stat_frame, "Tables Available", stats["available_tables"], "🪑", 1)
        self.stat_card(stat_frame, "Menu Items", stats["menu_items"], "🍽", 2)
        self.stat_card(stat_frame, "Sales", f"${stats['sales']:.2f}", "💵", 3)

        cards = tk.Frame(main, bg=BG)
        cards.pack(pady=25)
        dashboard_cards = items[:-1]
        for i, (text, cmd) in enumerate(dashboard_cards):
            clean = text.split("  ", 1)
            icon = clean[0]
            name = clean[1] if len(clean) > 1 else text
            card = tk.Button(cards, text=f"{icon}\n{name}", command=cmd, width=18, height=5, bg=WHITE, fg=DARK, activebackground="#edf0f5", font=("Arial", 13, "bold"), relief="solid", bd=1, cursor="hand2")
            card.grid(row=i // 3, column=i % 3, padx=20, pady=18)

        footer = tk.Frame(main, bg="#edf0f5", height=34)
        footer.pack(side="bottom", fill="x")
        tk.Label(footer, text="Role based access enabled | Staff cannot view reports", bg="#edf0f5", fg=GRAY, font=("Arial", 9)).pack(side="left", padx=20)
        self.button(main, "Refresh Dashboard", self.show_dashboard, 18, "#0984e3").pack(pady=10)

    def stat_card(self, parent, title, value, icon, col):
        card = tk.Frame(parent, bg=WHITE, padx=18, pady=14, highlightbackground="#dcdde1", highlightthickness=1)
        card.grid(row=0, column=col, padx=8, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        tk.Label(card, text=icon, bg=WHITE, font=("Arial", 22)).pack(side="left", padx=(0, 12))
        box = tk.Frame(card, bg=WHITE)
        box.pack(side="left")
        tk.Label(box, text=str(value), bg=WHITE, fg=MAROON, font=("Arial", 18, "bold")).pack(anchor="w")
        tk.Label(box, text=title, bg=WHITE, fg=GRAY, font=("Arial", 9, "bold")).pack(anchor="w")

    def get_dashboard_stats(self):
        def one(sql):
            rows = self.db.query(sql, fetch=True) or [{}]
            return list(rows[0].values())[0] or 0
        return {
            "open_orders": one("SELECT COUNT(*) FROM orders WHERE status='Open'"),
            "available_tables": one("SELECT COUNT(*) FROM restaurant_tables WHERE status='Available'"),
            "menu_items": one("SELECT COUNT(*) FROM menu_items"),
            "sales": Decimal(str(one("SELECT COALESCE(SUM(final_amount),0) FROM bills")))
        }

    def crud_window(self, title, fields, table, pk):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("980x600")
        win.configure(bg=BG)
        form = tk.Frame(win, bg=WHITE, padx=22, pady=20, highlightbackground="#dcdde1", highlightthickness=1)
        form.pack(side="left", fill="y", padx=18, pady=18)
        list_frame = tk.Frame(win, bg=BG)
        list_frame.pack(side="right", fill="both", expand=True, padx=(0, 18), pady=18)
        entries = {}
        tk.Label(form, text=title, bg=WHITE, fg=MAROON, font=("Arial", 16, "bold")).pack(pady=(0, 18))
        for label, name, kind, options in fields:
            tk.Label(form, text=label, bg=WHITE, fg=DARK, anchor="w", font=("Arial", 10, "bold")).pack(fill="x", pady=(8, 3))
            if kind == "combo":
                e = ttk.Combobox(form, values=options, state="readonly", width=24)
                e.set(options[0])
            else:
                e = tk.Entry(form, width=27, relief="solid", bd=1)
            e.pack(ipady=5)
            entries[name] = e

        toolbar = tk.Frame(list_frame, bg=BG)
        toolbar.pack(fill="x", pady=(0, 10))
        tk.Label(toolbar, text=f"{title} List", bg=BG, fg=DARK, font=("Arial", 14, "bold")).pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(toolbar, textvariable=search_var, width=30, relief="solid", bd=1)
        search_entry.pack(side="right", ipady=5)
        tk.Label(toolbar, text="Search:", bg=BG, fg=GRAY).pack(side="right", padx=6)

        cols = [pk] + [f[1] for f in fields]
        tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.replace("_", " ").title())
            tree.column(c, width=130)
        tree.pack(fill="both", expand=True)

        def load():
            for r in tree.get_children():
                tree.delete(r)
            rows = self.db.query(f"SELECT * FROM {table} ORDER BY {pk} DESC", fetch=True) or []
            term = search_var.get().lower().strip()
            for row in rows:
                values = [row.get(c) for c in cols]
                if not term or term in " ".join(str(v).lower() for v in values):
                    tree.insert("", "end", values=values)

        def clear_form():
            for f in fields:
                widget = entries[f[1]]
                if isinstance(widget, ttk.Combobox):
                    widget.set(f[3][0])
                else:
                    widget.delete(0, tk.END)

        def add():
            vals = [entries[f[1]].get() for f in fields]
            sql = f"INSERT INTO {table} ({','.join([f[1] for f in fields])}) VALUES ({','.join(['%s']*len(fields))})"
            self.db.query(sql, vals)
            clear_form(); load()

        def delete():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Row", "Select a row first.")
                return
            if not messagebox.askyesno("Confirm Delete", "Delete selected record?"):
                return
            row_id = tree.item(sel[0])["values"][0]
            self.db.query(f"DELETE FROM {table} WHERE {pk}=%s", (row_id,))
            load()

        def fill_from_selection(event=None):
            sel = tree.selection()
            if not sel: return
            vals = tree.item(sel[0])["values"]
            for idx, f in enumerate(fields, start=1):
                widget = entries[f[1]]
                if isinstance(widget, ttk.Combobox):
                    widget.set(vals[idx])
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, vals[idx])

        def update():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Row", "Select a row first.")
                return
            row_id = tree.item(sel[0])["values"][0]
            vals = [entries[f[1]].get() for f in fields] + [row_id]
            sets = ",".join([f"{f[1]}=%s" for f in fields])
            self.db.query(f"UPDATE {table} SET {sets} WHERE {pk}=%s", vals)
            load()

        tree.bind("<<TreeviewSelect>>", fill_from_selection)
        search_var.trace_add("write", lambda *args: load())
        btns = tk.Frame(form, bg=WHITE)
        btns.pack(pady=22)
        self.button(btns, "Add", add, 10).grid(row=0, column=0, padx=5)
        self.button(btns, "Update", update, 10, ORANGE).grid(row=0, column=1, padx=5)
        self.button(btns, "Delete", delete, 10, RED).grid(row=1, column=0, padx=5, pady=8)
        self.button(btns, "Clear", clear_form, 10, GRAY).grid(row=1, column=1, padx=5, pady=8)
        load()

    def menu_window(self):
        self.crud_window("Menu Management", [
            ("Item Name", "item_name", "entry", None),
            ("Category", "category", "combo", ["Starters", "Main Course", "Drinks", "Desserts"]),
            ("Price", "price", "entry", None),
            ("Availability", "availability", "combo", ["Available", "Unavailable"]),
        ], "menu_items", "item_id")

    def customers_window(self):
        self.crud_window("Customer Management", [
            ("Name", "name", "entry", None),
            ("Phone", "phone", "entry", None),
            ("Email", "email", "entry", None),
        ], "customers", "customer_id")

    def tables_window(self):
        self.crud_window("Table Management", [
            ("Table Number", "table_number", "entry", None),
            ("Capacity", "capacity", "entry", None),
            ("Status", "status", "combo", ["Available", "Occupied", "Reserved"]),
        ], "restaurant_tables", "table_id")

    def orders_window(self):
        win = tk.Toplevel(self.root)
        win.title("Create Order")
        win.geometry("1020x620")
        win.configure(bg=BG)
        left = tk.Frame(win, bg=WHITE, padx=22, pady=22, highlightbackground="#dcdde1", highlightthickness=1)
        left.pack(side="left", fill="y", padx=18, pady=18)
        right = tk.Frame(win, bg=BG, padx=10, pady=18)
        right.pack(side="right", fill="both", expand=True, padx=(0, 18))
        tk.Label(left, text="Create Order", bg=WHITE, fg=MAROON, font=("Arial", 17, "bold")).pack(pady=(0, 15))
        customers = self.db.query("SELECT customer_id, name FROM customers ORDER BY name", fetch=True) or []
        tables = self.db.query("SELECT table_id, table_number FROM restaurant_tables WHERE status IN ('Available','Reserved') ORDER BY table_number", fetch=True) or []
        items = self.db.query("SELECT item_id, item_name, price FROM menu_items WHERE availability='Available' ORDER BY item_name", fetch=True) or []
        customer_map = {f"{c['customer_id']} - {c['name']}": c['customer_id'] for c in customers}
        table_map = {f"{t['table_id']} - {t['table_number']}": t['table_id'] for t in tables}
        item_map = {f"{i['item_id']} - {i['item_name']} (${i['price']})": i for i in items}
        for txt in ["Customer", "Table", "Item"]:
            tk.Label(left, text=txt, bg=WHITE, fg=DARK, font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 3))
            cb = ttk.Combobox(left, width=32, state="readonly")
            if txt == "Customer": customer_cb = cb; cb["values"] = list(customer_map.keys())
            elif txt == "Table": table_cb = cb; cb["values"] = list(table_map.keys())
            else: item_cb = cb; cb["values"] = list(item_map.keys())
            cb.pack(ipady=4)
        tk.Label(left, text="Quantity", bg=WHITE, fg=DARK, font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 3))
        qty_entry = tk.Entry(left, width=12, relief="solid", bd=1)
        qty_entry.insert(0, "1")
        qty_entry.pack(ipady=5, anchor="w")
        cols = ["item_id", "name", "price", "qty", "total"]
        tk.Label(right, text="Order Items", bg=BG, fg=DARK, font=("Arial", 15, "bold")).pack(anchor="w", pady=(0, 10))
        tree = ttk.Treeview(right, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c.replace("_", " ").title())
            tree.column(c, width=110)
        tree.pack(fill="both", expand=True)
        total_var = tk.StringVar(value="Subtotal: $0.00")
        tk.Label(right, textvariable=total_var, bg=BG, fg=MAROON, font=("Arial", 16, "bold")).pack(anchor="e", pady=12)

        def recalc():
            total = Decimal("0.00")
            for r in tree.get_children():
                total += Decimal(str(tree.item(r)["values"][4]))
            total_var.set(f"Subtotal: ${total:.2f}")
            return total

        def add_item():
            if not item_cb.get(): return
            try:
                qty = int(qty_entry.get())
                if qty <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Quantity", "Quantity must be a positive number")
                return
            item = item_map[item_cb.get()]
            price = Decimal(str(item["price"]))
            tree.insert("", "end", values=[item["item_id"], item["item_name"], f"{price:.2f}", qty, f"{price*qty:.2f}"])
            recalc()

        def remove_item():
            for s in tree.selection(): tree.delete(s)
            recalc()

        def save_order():
            if not customer_cb.get() or not table_cb.get() or not tree.get_children():
                messagebox.showerror("Missing Data", "Select customer, table, and at least one item")
                return
            order_id = self.db.query("INSERT INTO orders(customer_id, table_id) VALUES(%s,%s)", (customer_map[customer_cb.get()], table_map[table_cb.get()]))
            for r in tree.get_children():
                v = tree.item(r)["values"]
                self.db.query("INSERT INTO order_items(order_id,item_id,quantity,unit_price) VALUES(%s,%s,%s,%s)", (order_id, v[0], v[3], v[2]))
            self.db.query("UPDATE restaurant_tables SET status='Occupied' WHERE table_id=%s", (table_map[table_cb.get()],))
            messagebox.showinfo("Success", f"Order #{order_id} created")
            win.destroy()

        self.button(left, "Add Item", add_item, 20).pack(pady=(18, 5))
        self.button(left, "Remove Selected", remove_item, 20, RED).pack(pady=5)
        self.button(left, "Save Order", save_order, 20, GREEN).pack(pady=(20, 5))

    def current_orders_window(self):
        win = tk.Toplevel(self.root)
        win.title("Current Orders")
        win.geometry("1000x600")
        win.configure(bg=BG)
        header = tk.Frame(win, bg=BG)
        header.pack(fill="x", padx=20, pady=(18, 8))
        tk.Label(header, text="Current Open Orders", bg=BG, fg=MAROON, font=("Arial", 20, "bold")).pack(side="left")
        self.button(header, "Refresh", lambda: load(), 10, GRAY).pack(side="right")
        cols = ["order_id", "order_date", "customer", "table_number", "items", "subtotal", "status"]
        tree = ttk.Treeview(win, columns=cols, show="headings")
        widths = {"order_id": 80, "order_date": 160, "customer": 150, "table_number": 100, "items": 300, "subtotal": 100, "status": 90}
        for c in cols:
            tree.heading(c, text=c.replace("_", " ").title())
            tree.column(c, width=widths.get(c, 120))
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        buttons = tk.Frame(win, bg=BG)
        buttons.pack(pady=12)

        def load():
            for r in tree.get_children():
                tree.delete(r)
            rows = self.db.query("""
                SELECT o.order_id, o.order_date, c.name AS customer, t.table_number, o.table_id, o.status,
                       GROUP_CONCAT(CONCAT(m.item_name, ' x', oi.quantity) SEPARATOR ', ') AS items,
                       SUM(oi.quantity * oi.unit_price) AS subtotal
                FROM orders o
                LEFT JOIN customers c ON o.customer_id=c.customer_id
                LEFT JOIN restaurant_tables t ON o.table_id=t.table_id
                LEFT JOIN order_items oi ON o.order_id=oi.order_id
                LEFT JOIN menu_items m ON oi.item_id=m.item_id
                WHERE o.status='Open'
                GROUP BY o.order_id, o.order_date, c.name, t.table_number, o.table_id, o.status
                ORDER BY o.order_id DESC
            """, fetch=True) or []
            for r in rows:
                tree.insert("", "end", values=[r["order_id"], r["order_date"], r["customer"], r["table_number"], r["items"], f"${Decimal(str(r['subtotal'] or 0)):.2f}", r["status"]])

        def selected_order():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Order", "Select an order first.")
                return None
            return tree.item(sel[0])["values"][0]

        def cancel_order():
            order_id = selected_order()
            if not order_id: return
            if not messagebox.askyesno("Cancel Order", f"Cancel order #{order_id}?"):
                return
            table = self.db.query("SELECT table_id FROM orders WHERE order_id=%s", (order_id,), fetch=True)
            self.db.query("UPDATE orders SET status='Cancelled' WHERE order_id=%s", (order_id,))
            if table and table[0]["table_id"]:
                self.db.query("UPDATE restaurant_tables SET status='Available' WHERE table_id=%s", (table[0]["table_id"],))
            messagebox.showinfo("Cancelled", f"Order #{order_id} cancelled.")
            load()

        def mark_served():
            order_id = selected_order()
            if not order_id: return
            self.db.query("UPDATE orders SET status='Served' WHERE order_id=%s", (order_id,))
            messagebox.showinfo("Served", f"Order #{order_id} marked as served. It can still be billed later.")
            load()

        self.button(buttons, "Mark Served", mark_served, 15, GREEN).grid(row=0, column=0, padx=8)
        self.button(buttons, "Cancel Order", cancel_order, 15, RED).grid(row=0, column=1, padx=8)
        self.button(buttons, "Open Billing", self.billing_window, 15, MAROON).grid(row=0, column=2, padx=8)
        load()

    def billing_window(self):
        win = tk.Toplevel(self.root)
        win.title("Billing")
        win.geometry("900x540")
        win.configure(bg=BG)
        top = tk.Frame(win, bg=WHITE, padx=20, pady=15, highlightbackground="#dcdde1", highlightthickness=1)
        top.pack(fill="x", padx=20, pady=20)
        orders = self.db.query("SELECT order_id FROM orders WHERE status IN ('Open','Served') ORDER BY order_id DESC", fetch=True) or []
        order_cb = ttk.Combobox(top, values=[o["order_id"] for o in orders], state="readonly", width=15)
        tk.Label(top, text="Order ID:", bg=WHITE, fg=DARK, font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))
        order_cb.pack(side="left")
        detail = tk.Text(win, height=16, width=95, relief="solid", bd=1, font=("Consolas", 10))
        detail.pack(pady=5)
        bottom = tk.Frame(win, bg=BG)
        bottom.pack(pady=15)
        tk.Label(bottom, text="Discount", bg=BG, font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        discount = tk.Entry(bottom, width=10, relief="solid", bd=1)
        discount.insert(0, "0")
        discount.grid(row=0, column=1, padx=5, ipady=5)
        tk.Label(bottom, text="Payment", bg=BG, font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)
        payment = ttk.Combobox(bottom, values=["Cash", "Card", "UPI"], state="readonly", width=12)
        payment.set("Cash")
        payment.grid(row=0, column=3, padx=5)
        current_total = {"value": Decimal("0.00")}

        def load_bill():
            if not order_cb.get(): return
            rows = self.db.query("""
                SELECT m.item_name, oi.quantity, oi.unit_price, oi.quantity*oi.unit_price AS total
                FROM order_items oi JOIN menu_items m ON oi.item_id=m.item_id
                WHERE oi.order_id=%s
            """, (order_cb.get(),), fetch=True) or []
            detail.delete("1.0", tk.END)
            subtotal = Decimal("0.00")
            detail.insert(tk.END, f"Bill for Order #{order_cb.get()}\n")
            detail.insert(tk.END, "-" * 55 + "\n\n")
            for r in rows:
                line = Decimal(str(r["total"]))
                subtotal += line
                detail.insert(tk.END, f"{r['item_name']:<25} x{r['quantity']:<3} @ ${Decimal(str(r['unit_price'])):>7.2f} = ${line:>7.2f}\n")
            tax = subtotal * Decimal("0.05")
            current_total["value"] = subtotal
            detail.insert(tk.END, "\n" + "-" * 55)
            detail.insert(tk.END, f"\nSubtotal: ${subtotal:.2f}\nTax 5%:   ${tax:.2f}\n")

        def confirm_payment():
            if not order_cb.get(): return
            subtotal = current_total["value"]
            if subtotal <= 0:
                messagebox.showwarning("Load Bill", "Load the bill before confirming payment.")
                return
            try:
                disc = Decimal(discount.get() or "0")
            except Exception:
                messagebox.showerror("Invalid Discount", "Discount must be numeric")
                return
            tax = subtotal * Decimal("0.05")
            final = subtotal + tax - disc
            self.db.query("INSERT INTO bills(order_id,item_total,tax,discount,final_amount,payment_method) VALUES(%s,%s,%s,%s,%s,%s)", (order_cb.get(), subtotal, tax, disc, final, payment.get()))
            self.db.query("UPDATE orders SET status='Billed' WHERE order_id=%s", (order_cb.get(),))
            table = self.db.query("SELECT table_id FROM orders WHERE order_id=%s", (order_cb.get(),), fetch=True)
            if table and table[0]["table_id"]:
                self.db.query("UPDATE restaurant_tables SET status='Available' WHERE table_id=%s", (table[0]["table_id"],))
            messagebox.showinfo("Paid", f"Payment completed. Final amount: ${final:.2f}")
            win.destroy()

        self.button(top, "Load Bill", load_bill, 12).pack(side="left", padx=12)
        self.button(bottom, "Confirm Payment", confirm_payment, 18, GREEN).grid(row=0, column=4, padx=15)

    def reports_window(self):
        if self.current_user["role"].lower() != "admin":
            messagebox.showerror("Access Denied", "Only admin users can view reports.")
            return
        win = tk.Toplevel(self.root)
        win.title("Reports")
        win.geometry("900x560")
        win.configure(bg=BG)
        header = tk.Frame(win, bg=BG)
        header.pack(fill="x", padx=20, pady=(18, 8))
        tk.Label(header, text="Reports", bg=BG, fg=MAROON, font=("Arial", 20, "bold")).pack(side="left")
        text = tk.Text(win, height=26, width=105, relief="solid", bd=1, font=("Consolas", 10))
        text.pack(padx=20, pady=10)
        total = self.db.query("SELECT COALESCE(SUM(final_amount),0) AS total_sales, COUNT(*) AS total_orders FROM bills", fetch=True)[0]
        top_items = self.db.query("""
            SELECT m.item_name, SUM(oi.quantity) AS qty, SUM(oi.quantity*oi.unit_price) AS sales
            FROM order_items oi JOIN menu_items m ON oi.item_id=m.item_id
            GROUP BY m.item_name ORDER BY qty DESC LIMIT 5
        """, fetch=True) or []
        history = self.db.query("""
            SELECT o.order_id, o.order_date, c.name AS customer, b.final_amount, o.status
            FROM orders o LEFT JOIN customers c ON o.customer_id=c.customer_id
            LEFT JOIN bills b ON o.order_id=b.order_id
            ORDER BY o.order_id DESC LIMIT 10
        """, fetch=True) or []
        text.insert(tk.END, "RESTAURANT REPORTS\n")
        text.insert(tk.END, "==================\n\n")
        text.insert(tk.END, f"Total Sales: ${Decimal(str(total['total_sales'])):.2f}\n")
        text.insert(tk.END, f"Total Paid Orders: {total['total_orders']}\n\n")
        text.insert(tk.END, "Top Items:\n")
        for r in top_items:
            text.insert(tk.END, f"- {r['item_name']}: {r['qty']} sold, ${Decimal(str(r['sales'])):.2f}\n")
        text.insert(tk.END, "\nRecent Orders:\n")
        for r in history:
            amount = r['final_amount'] if r['final_amount'] is not None else 0
            text.insert(tk.END, f"#{r['order_id']} | {r['order_date']} | {r['customer']} | ${Decimal(str(amount)):.2f} | {r['status']}\n")
        text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantApp(root)
    root.mainloop()
