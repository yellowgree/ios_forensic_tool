import tkinter as tk
from tkinter import ttk, messagebox
from artifact_analyzer.browser.safari.history import get_safari_history

def display_browser(content_frame, backup_path):
    # 기존 위젯 삭제
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # 헤더 추가
    header_frame = ttk.Frame(content_frame)
    header_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(header_frame, text="🌐 브라우저", style="ContentHeader.TLabel").pack(side="left")
    ttk.Separator(content_frame, orient="horizontal").pack(fill="x", pady=(0, 15))
    
    # 브라우저 카드
    browser_card = ttk.Frame(content_frame, style="Card.TFrame", padding=15)
    browser_card.pack(fill="both", expand=True, padx=5, pady=5)
    
    browser_select_frame = ttk.Frame(browser_card)
    browser_select_frame.pack(fill="x", pady=(0, 15))
    
    ttk.Label(browser_select_frame, text="브라우저:", style="InfoLabel.TLabel").pack(side="left", padx=(0, 5))
    
    app_var = tk.StringVar(value="Safari")
    app_combo = ttk.Combobox(browser_select_frame, textvariable=app_var, values=["Chrome", "Safari", "기타"])
    app_combo.pack(side="left", padx=(0, 10))
    
    # Treeview 생성 (표 형태 출력)
    columns = ("title", "url", "visit_time")
    history_tree = ttk.Treeview(browser_card, columns=columns, show="headings")
    
    history_tree.heading("title", text="Title", anchor="w")
    history_tree.heading("url", text="URI", anchor="w")
    history_tree.heading("visit_time", text="방문 시간", anchor="w")
    
    history_tree.column("title", width=180, anchor="w")
    history_tree.column("url", width=320, anchor="w")
    history_tree.column("visit_time", width=150, anchor="w")
    
    history_tree.pack(fill="both", expand=True, padx=5, pady=5)
    
    def fetch_history():
        if app_var.get() == "Safari":
            history = get_safari_history(backup_path)
            history_tree.delete(*history_tree.get_children())  # 기존 데이터 삭제
            
            if isinstance(history, str):
                messagebox.showerror("오류", history)
            else:
                for item in history:
                    title, url, visit_time = item
                    history_tree.insert("", "end", values=(title, url, visit_time))
    
    ttk.Button(browser_select_frame, text="조회", style="AccentButton.TButton", width=8, command=fetch_history).pack(side="left")
