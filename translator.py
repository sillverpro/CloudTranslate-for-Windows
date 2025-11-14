import os
import sys
import json
import datetime
import requests
import customtkinter as ctk
from tkinter import messagebox, filedialog

# -------------------------------
# Paths & config / data handling
# -------------------------------

def get_base_dir():
    """
    Ensure data files are stored next to the script / exe (portable).
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # Running as normal .py
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
USAGE_PATH = os.path.join(BASE_DIR, "usage.json")
HISTORY_PATH = os.path.join(BASE_DIR, "history.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        messagebox.showerror(
            "Config missing",
            f"config.json not found in:\n{BASE_DIR}\n\nPlease create it with your Google API key."
        )
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    if "google_api_key" not in cfg or not cfg["google_api_key"]:
        messagebox.showerror("Config error", "google_api_key is missing in config.json")
        sys.exit(1)

    if "monthly_limit" not in cfg:
        cfg["monthly_limit"] = 500000

    return cfg


def load_usage(monthly_limit):
    """
    usage.json structure:
    {
      "month_key": "2025-11",
      "used_chars": 12345,
      "monthly_limit": 500000
    }
    """
    current_month_key = datetime.datetime.now().strftime("%Y-%m")

    if not os.path.exists(USAGE_PATH):
        data = {
            "month_key": current_month_key,
            "used_chars": 0,
            "monthly_limit": monthly_limit
        }
        save_usage(data)
        return data

    with open(USAGE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Reset if new month
    if data.get("month_key") != current_month_key:
        data["month_key"] = current_month_key
        data["used_chars"] = 0

    # Ensure monthly_limit is up to date with config
    data["monthly_limit"] = monthly_limit
    save_usage(data)
    return data


def save_usage(data):
    with open(USAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_history():
    """
    history.json structure:
    {
      "entries": [
        {
          "timestamp": "2025-11-13 15:32:00",
          "source_lang": "en",
          "target_lang": "th",
          "chars": 123,
          "source_text": "...",
          "translated_text": "..."
        }
      ]
    }
    """
    if not os.path.exists(HISTORY_PATH):
        data = {"entries": []}
        save_history(data)
        return data

    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "entries" not in data:
        data["entries"] = []
    return data


def save_history(data):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -------------------------------
# Languages & display helpers
# -------------------------------

# Real language codes + names
LANG_CODES = {
    "en": "English",
    "th": "Thai",
    "ar": "Arabic",
    "zh": "Chinese",
    "fr": "French",
    "ru": "Russian",
    "es": "Spanish",
    "ja": "Japanese",
    "ko": "Korean",
    "de": "German",
}


def format_lang(code: str) -> str:
    return f"{LANG_CODES.get(code, code)} ({code})"


def build_lang_display_list():
    """
    Returns list for ComboBox, with group separators as strings starting with '---'.
    Order:
    English, Thai
    --- WHO Languages ---
    Arabic, Chinese, French, Russian, Spanish
    --- Extra Languages ---
    Japanese, Korean, German
    """
    display = []
    # Main
    display.append(format_lang("en"))
    display.append(format_lang("th"))
    # WHO
    display.append("--- WHO Languages ---")
    for c in ["ar", "zh", "fr", "ru", "es"]:
        display.append(format_lang(c))
    # Extra
    display.append("--- Extra Languages ---")
    for c in ["ja", "ko", "de"]:
        display.append(format_lang(c))
    return display


def is_separator_item(text: str) -> bool:
    return text.strip().startswith("---")


def get_display_for_code(code: str, display_list) -> str:
    """Find the first display string matching a language code."""
    code_part = f"({code})"
    for item in display_list:
        if is_separator_item(item):
            continue
        if item.endswith(code_part):
            return item
    # fallback if not found
    return display_list[0]


def parse_lang(display_text: str) -> str:
    # e.g. "English (en)" → "en"
    if "(" in display_text and ")" in display_text:
        return display_text.split("(")[-1].strip(")")
    return display_text


# -------------------------------
# Google Translation (no detect)
# -------------------------------

def google_translate(api_key, text, source_lang, target_lang):
    """
    Uses Google Cloud Translation API v2 (REST).
    No language detection, just source -> target.
    """
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        "key": api_key
    }
    data = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }

    response = requests.post(url, params=params, data=data, timeout=20)
    response.raise_for_status()
    res_json = response.json()
    translations = res_json.get("data", {}).get("translations", [])
    if not translations:
        raise ValueError("No translation returned from API.")
    return translations[0].get("translatedText", "")


# -------------------------------
# App UI (CustomTkinter)
# -------------------------------

class TranslatorApp(ctk.CTk):

    def __init__(self, config):
        super().__init__()

        self.config_data = config
        self.api_key = config["google_api_key"]
        self.usage_data = load_usage(config["monthly_limit"])
        self.history_data = load_history()

        self.title("CloudTranslate for Windows")
        self.geometry("900x600")
        self.minsize(850, 550)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Language display list with separators
        self.lang_display_list = build_lang_display_list()
        self.last_from_valid = get_display_for_code("en", self.lang_display_list)
        self.last_to_valid = get_display_for_code("th", self.lang_display_list)

        self.create_widgets()
        self.update_char_count()
        self.update_usage_labels()
        self.load_history_to_ui()

    def create_widgets(self):
        # ===== Top frame: language selection + swap =====
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        for col in range(5):
            top_frame.grid_columnconfigure(col, weight=1 if col == 2 else 0)

        from_label = ctk.CTkLabel(top_frame, text="From:", font=ctk.CTkFont(size=12, weight="bold"))
        from_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")

        self.from_combo = ctk.CTkComboBox(
            top_frame,
            values=self.lang_display_list,
            width=200,
            command=self.on_from_changed
        )
        self.from_combo.set(self.last_from_valid)
        self.from_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        swap_button = ctk.CTkButton(
            top_frame,
            text="Swap",
            width=80,
            fg_color="black",
            hover_color="#222222",
            text_color="white",
            command=self.swap_languages
        )
        swap_button.grid(row=0, column=2, padx=5, pady=5)

        to_label = ctk.CTkLabel(top_frame, text="To:", font=ctk.CTkFont(size=12, weight="bold"))
        to_label.grid(row=0, column=3, padx=(10, 5), pady=5, sticky="e")

        self.to_combo = ctk.CTkComboBox(
            top_frame,
            values=self.lang_display_list,
            width=200,
            command=self.on_to_changed
        )
        self.to_combo.set(self.last_to_valid)
        self.to_combo.grid(row=0, column=4, padx=(5, 10), pady=5, sticky="e")

        # ===== Middle frame: text areas and buttons =====
        mid_frame = ctk.CTkFrame(self)
        mid_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        mid_frame.grid_columnconfigure(0, weight=1)
        mid_frame.grid_rowconfigure(1, weight=1)
        mid_frame.grid_rowconfigure(3, weight=1)

        # --- Input header: "Text to translate" + Paste + Clear + char count ---
        header1 = ctk.CTkFrame(mid_frame, fg_color="transparent")
        header1.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header1.grid_columnconfigure(1, weight=1)

        input_label = ctk.CTkLabel(header1, text="Text to translate", font=ctk.CTkFont(size=12, weight="bold"))
        input_label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")

        self.char_label = ctk.CTkLabel(header1, text="Chars: 0", font=ctk.CTkFont(size=10))
        self.char_label.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        paste_btn = ctk.CTkButton(
            header1,
            text="Paste",
            width=80,
            fg_color="black",
            hover_color="#222222",
            text_color="white",
            command=self.paste_text
        )
        paste_btn.grid(row=0, column=2, padx=5, pady=5)

        clear_btn = ctk.CTkButton(
            header1,
            text="Clear",
            width=80,
            fg_color="black",
            hover_color="#222222",
            text_color="white",
            command=self.clear_texts
        )
        clear_btn.grid(row=0, column=3, padx=5, pady=5)

        # --- Input textbox ---
        self.input_text = ctk.CTkTextbox(mid_frame, height=150)
        self.input_text.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.input_text.bind("<<Modified>>", self.on_text_modified)

        # --- Output header: "Translated Text" + Copy + Export ---
        header2 = ctk.CTkFrame(mid_frame, fg_color="transparent")
        header2.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 0))
        header2.grid_columnconfigure(1, weight=1)

        output_label = ctk.CTkLabel(header2, text="Translated Text", font=ctk.CTkFont(size=12, weight="bold"))
        output_label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")

        copy_btn = ctk.CTkButton(
            header2,
            text="Copy",
            width=80,
            fg_color="black",
            hover_color="#222222",
            text_color="white",
            command=self.copy_output
        )
        copy_btn.grid(row=0, column=2, padx=5, pady=5)

        export_btn = ctk.CTkButton(
            header2,
            text="Export (.txt)",
            width=110,
            fg_color="black",
            hover_color="#222222",
            text_color="white",
            command=self.export_txt
        )
        export_btn.grid(row=0, column=3, padx=5, pady=5)

        # --- Output textbox ---
        self.output_text = ctk.CTkTextbox(mid_frame, height=150)
        self.output_text.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.output_text.configure(state="normal")

        # --- Translate button (full width, max 300, centered) ---
        translate_frame = ctk.CTkFrame(mid_frame, fg_color="transparent")
        translate_frame.grid(row=4, column=0, pady=(5, 10))
        translate_frame.grid_columnconfigure(0, weight=1)

        self.translate_btn = ctk.CTkButton(
            translate_frame,
            text="Translate",
            width=300,
            fg_color="black",
            hover_color="#222222",
            text_color="white",
            command=self.translate
        )
        self.translate_btn.grid(row=0, column=0, pady=5, sticky="n")

        # ===== Bottom frame: usage + history =====
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        bottom_frame.grid_rowconfigure(2, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.usage_label = ctk.CTkLabel(
            bottom_frame,
            text="Usage: 0 / 500,000 chars",
            font=ctk.CTkFont(size=11)
        )
        self.usage_label.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")

        self.reset_label = ctk.CTkLabel(
            bottom_frame,
            text="Resets monthly",
            font=ctk.CTkFont(size=10)
        )
        self.reset_label.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="e")

        history_label = ctk.CTkLabel(
            bottom_frame,
            text="History (latest first)",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        history_label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")

        self.history_box = ctk.CTkTextbox(bottom_frame, height=120)
        self.history_box.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.history_box.configure(state="disabled")

    # ---------- Combobox handlers (prevent separator selection) ----------

    def on_from_changed(self, value):
        if is_separator_item(value):
            # revert to last real language
            self.from_combo.set(self.last_from_valid)
        else:
            self.last_from_valid = value

    def on_to_changed(self, value):
        if is_separator_item(value):
            self.to_combo.set(self.last_to_valid)
        else:
            self.last_to_valid = value

    # ---------- Events & helpers ----------

    def on_text_modified(self, event=None):
        self.input_text.edit_modified(False)
        self.update_char_count()

    def update_char_count(self):
        text = self.input_text.get("1.0", "end-1c")
        count = len(text)
        self.char_label.configure(text=f"Chars: {count}")

    def update_usage_labels(self):
        used = self.usage_data.get("used_chars", 0)
        limit = self.usage_data.get("monthly_limit", 500000)
        remaining = max(limit - used, 0)

        self.usage_label.configure(
            text=f"Usage this month: {used:,} / {limit:,} chars (Remaining: {remaining:,})"
        )

        month_key = self.usage_data.get("month_key")
        try:
            reset_date = datetime.datetime.strptime(month_key + "-01", "%Y-%m-%d")
            year = reset_date.year + (1 if reset_date.month == 12 else 0)
            month = 1 if reset_date.month == 12 else reset_date.month + 1
            next_reset = datetime.datetime(year, month, 1)
            self.reset_label.configure(
                text=f"Resets around: {next_reset.strftime('%Y-%m-%d')}"
            )
        except Exception:
            self.reset_label.configure(text="Resets monthly")

    def swap_languages(self):
        from_val = self.from_combo.get()
        to_val = self.to_combo.get()
        self.from_combo.set(to_val)
        self.to_combo.set(from_val)
        # update last valid states
        if not is_separator_item(to_val):
            self.last_from_valid = to_val
        if not is_separator_item(from_val):
            self.last_to_valid = from_val

    def paste_text(self):
        try:
            text = self.clipboard_get()
        except Exception:
            text = ""
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", text)
        self.update_char_count()

    def copy_output(self):
        text = self.output_text.get("1.0", "end-1c")
        if not text.strip():
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Translated text copied to clipboard.")

    def export_txt(self):
        text = self.output_text.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showwarning("No text", "There is no translated text to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Exported", f"Translated text saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

    def clear_texts(self):
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.update_char_count()

    def append_history_entry(self, entry):
        self.history_data["entries"].insert(0, entry)
        if len(self.history_data["entries"]) > 500:
            self.history_data["entries"] = self.history_data["entries"][:500]
        save_history(self.history_data)
        self.load_history_to_ui()

    def load_history_to_ui(self):
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")

        entries = self.history_data.get("entries", [])
        if not entries:
            self.history_box.insert("1.0", "No history yet.")
            self.history_box.configure(state="disabled")
            return

        current_date = None
        for e in entries:
            ts = e.get("timestamp", "")
            try:
                dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M")
            except Exception:
                date_str = ts.split(" ")[0] if " " in ts else ts
                time_str = ""
            if date_str != current_date:
                current_date = date_str
                self.history_box.insert("end", f"\n=== {current_date} ===\n")

            sl = e.get("source_lang", "")
            tl = e.get("target_lang", "")
            chars = e.get("chars", 0)
            s_text = e.get("source_text", "").replace("\n", " ")
            t_text = e.get("translated_text", "").replace("\n", " ")

            short_source = (s_text[:60] + "...") if len(s_text) > 60 else s_text
            short_target = (t_text[:60] + "...") if len(t_text) > 60 else t_text

            line = f"[{time_str}] {sl}->{tl} ({chars} chars)\n  {short_source}\n  → {short_target}\n"
            self.history_box.insert("end", line)

        self.history_box.configure(state="disabled")

    def translate(self):
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("No text", "Please enter text to translate.")
            return

        src_display = self.from_combo.get()
        tgt_display = self.to_combo.get()
        source_lang = parse_lang(src_display)
        target_lang = parse_lang(tgt_display)

        if source_lang == target_lang:
            if not messagebox.askyesno(
                "Same language",
                "Source and target languages are the same. Continue?"
            ):
                return

        char_count = len(text)
        self.update_char_count()

        limit_heavy = 5000
        if char_count >= limit_heavy:
            if not messagebox.askyesno(
                "Large text",
                f"This translation will use {char_count:,} characters.\nContinue?"
            ):
                return

        used = self.usage_data.get("used_chars", 0)
        limit = self.usage_data.get("monthly_limit", 500000)
        upcoming_total = used + char_count

        if upcoming_total > limit:
            if not messagebox.askyesno(
                "Limit warning",
                f"This will exceed your monthly limit of {limit:,} characters.\n"
                f"Current used: {used:,}\nThis text: {char_count:,}\n\nContinue anyway?"
            ):
                return

        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", "Translating...")
        self.update_idletasks()

        try:
            translated = google_translate(self.api_key, text, source_lang, target_lang)
        except requests.HTTPError as e:
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", f"HTTP error: {e}\n{getattr(e.response, 'text', '')}")
            return
        except Exception as e:
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", f"Error: {e}")
            return

        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", translated)

        self.usage_data["used_chars"] = upcoming_total
        save_usage(self.usage_data)
        self.update_usage_labels()

        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_lang": source_lang,
            "target_lang": target_lang,
            "chars": char_count,
            "source_text": text,
            "translated_text": translated
        }
        self.append_history_entry(entry)

    def on_close(self):
        if messagebox.askokcancel("Exit", "Do you really want to close the translator?"):
            self.destroy()


def main():
    cfg = load_config()
    app = TranslatorApp(cfg)
    app.mainloop()


if __name__ == "__main__":
    main()
