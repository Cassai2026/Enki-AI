# -*- coding: utf-8 -*-
import json
import sqlite3
import os


class FormDatabase:
    def __init__(self, db_path="data/form_submissions.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS form_submissions (id INTEGER PRIMARY KEY AUTOINCREMENT, form_name TEXT NOT NULL, data TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, reviewed BOOLEAN DEFAULT 0, notes TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS data_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        c.execute("CREATE TABLE IF NOT EXISTS review_queue (id INTEGER PRIMARY KEY AUTOINCREMENT, submission_id INTEGER NOT NULL, status TEXT DEFAULT 'pending', ai_response TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (submission_id) REFERENCES form_submissions(id))")
        conn.commit()
        conn.close()

    def submit_form(self, form_name, form_data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO form_submissions (form_name, data) VALUES (?, ?)", (form_name, json.dumps(form_data)))
        sid = c.lastrowid
        c.execute("INSERT INTO review_queue (submission_id) VALUES (?)", (sid,))
        conn.commit()
        conn.close()
        return sid

    def add_data(self, category, key, value):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        vs = json.dumps(value) if not isinstance(value, str) else value
        c.execute("INSERT INTO data_entries (category, key, value) VALUES (?, ?, ?)", (category, key, vs))
        eid = c.lastrowid
        conn.commit()
        conn.close()
        return eid

    def get_pending_reviews(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT fs.id, fs.form_name, fs.data, fs.timestamp, rq.id as review_id FROM form_submissions fs JOIN review_queue rq ON fs.id = rq.submission_id WHERE rq.status = 'pending' ORDER BY fs.timestamp DESC")
        rows = [dict(r) for r in c.fetchall()]
        for r in rows:
            r["data"] = json.loads(r["data"])
        conn.close()
        return rows

    def mark_reviewed(self, submission_id, ai_response=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE form_submissions SET reviewed = 1 WHERE id = ?", (submission_id,))
        if ai_response:
            c.execute("UPDATE review_queue SET status = 'completed', ai_response = ? WHERE submission_id = ?", (ai_response, submission_id))
        else:
            c.execute("UPDATE review_queue SET status = 'completed' WHERE submission_id = ?", (submission_id,))
        conn.commit()
        conn.close()
        return True

    def get_all_submissions(self, limit=100):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM form_submissions ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in c.fetchall()]
        for r in rows:
            r["data"] = json.loads(r["data"])
        conn.close()
        return rows

    def get_data_by_category(self, category):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM data_entries WHERE category = ? ORDER BY timestamp DESC", (category,))
        rows = [dict(r) for r in c.fetchall()]
        for r in rows:
            try:
                r["value"] = json.loads(r["value"])
            except Exception:
                pass
        conn.close()
        return rows

    def get_latest_data(self, category, key):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT value FROM data_entries WHERE category = ? AND key = ? ORDER BY timestamp DESC LIMIT 1", (category, key))
        result = c.fetchone()
        conn.close()
        if result:
            try:
                return json.loads(result["value"])
            except Exception:
                return result["value"]
        return None


db = FormDatabase()