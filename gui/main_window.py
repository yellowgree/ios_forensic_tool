import tkinter as tk
from tkinter import ttk
import sys
import os
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox

from gui.styles import apply_styles
from gui.events_utils import (
    browse_backup_path,
    toggle_password_entry,
    update_file_list_from_backup_tree_click,
    update_backup_tree_from_file_list_double_click
)
from gui.load_backup_utils import load_backup
from artifact_analyzer.device.device_info import show_device_info

def start_gui():
    """GUI 애플리케이션을 초기화하고 시작합니다."""
    rootWindow = tk.Tk()
    rootWindow.title("iOS Forensic Viewer")
    
    # 시스템 DPI 감지 및 스케일링 설정
    if sys.platform.startswith('win'):
        from ctypes import windll
        try:
            windll.shcore.SetProcessDpiAwareness(1)  # 프로세스 DPI 인식 활성화
        except Exception:
            pass
    
    # 스타일 적용 및 색상 가져오기
    colors = apply_styles(rootWindow)
    
    # 창 크기 설정 (더 큰 초기 크기로 설정)
    rootWindow.minsize(1200, 800)
    rootWindow.geometry("1200x800")
    rootWindow.configure(bg=colors['bg_light'])
    
    # 아이콘 설정 (아이콘 파일이 있는 경우)
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            rootWindow.iconbitmap(icon_path)
    except Exception:
        pass
    
    setup_gui(rootWindow, colors)
    rootWindow.mainloop()

def setup_gui(rootWindow, colors):
    """GUI 레이아웃을 구성합니다."""
    # 메인 컨테이너
    main_frame = ttk.Frame(rootWindow)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # ==== 헤더 섹션 (더 작게 조정) ====
    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill="x", padx=10, pady=(5, 10))
    
    # 앱 로고/아이콘 추가
    try:
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "forensic_logo.png")
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((32, 32), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = ttk.Label(header_frame, image=logo_photo)
            logo_label.image = logo_photo  # 참조 유지
            logo_label.pack(side="left", padx=(0, 10))
        else:
            # 아이콘이 없는 경우 대체 텍스트 표시
            icon_frame = ttk.Frame(header_frame, width=32, height=32, style="IconPlaceholder.TFrame")
            icon_frame.pack(side="left", padx=(0, 10))
            ttk.Label(icon_frame, text="🔍", font=("Arial", 16)).place(relx=0.5, rely=0.5, anchor="center")
    except Exception:
        # 오류 발생 시 대체 텍스트 표시
        icon_frame = ttk.Frame(header_frame, width=32, height=32, style="IconPlaceholder.TFrame")
        icon_frame.pack(side="left", padx=(0, 10))
        ttk.Label(icon_frame, text="🔍", font=("Arial", 16)).place(relx=0.5, rely=0.5, anchor="center")
    
    # 앱 제목
    ttk.Label(header_frame, text="iOS Forensic Viewer", style="Header.TLabel").pack(side="left")
    
    # 오른쪽 상단에 테마 전환 버튼 추가
    theme_btn = ttk.Button(header_frame, text="🌙", width=3, style="Icon.TButton")
    theme_btn.pack(side="right", padx=5)
    
    # 입력 변수 초기화
    backup_path_var = tk.StringVar()
    enable_pw_var = tk.IntVar(value=0)
    password_var = tk.StringVar()
    
    # ==== 상단 제어 영역 (더 작게 조정) ====
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(fill="x", padx=10, pady=5)
    control_frame.columnconfigure(0, weight=1)  # 왼쪽 프레임 비율
    control_frame.columnconfigure(1, weight=1)  # 오른쪽 프레임 비율
    uniform_height = 65  # 적절한 높이 값으로 조정하세요

    # 왼쪽: 백업 로드 프레임
    load_frame = ttk.Frame(control_frame, style="Card.TFrame", padding=10, height=uniform_height)
    load_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
    load_frame.pack_propagate(False)
    # 백업 로드 그리드 (더 작게 조정)
    load_grid = ttk.Frame(load_frame)
    load_grid.pack(fill="x", expand=True)
    load_grid.columnconfigure(1, weight=1)
    
    # 백업 경로 입력
    ttk.Label(load_grid, text="백업 경로:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    path_entry = ttk.Entry(load_grid, textvariable=backup_path_var)
    path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    # 버튼 프레임
    btn_frame = ttk.Frame(load_grid)
    btn_frame.grid(row=0, column=2, padx=5, pady=5, sticky="e")
    
    browse_button = ttk.Button(btn_frame, text="찾아보기", width=10)
    browse_button.pack(side="left", padx=2)
    
    load_backup_button = ttk.Button(btn_frame, text="백업 로드", style="Accent.TButton", width=12)
    load_backup_button.pack(side="left", padx=2)
    
    # 오른쪽: 비밀번호 프레임
    pw_frame = ttk.Frame(control_frame, style="Card.TFrame", padding=10, height=uniform_height)
    pw_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
    pw_frame.pack_propagate(False)  # 내부 위젯이 프레임 크기를 변경하지 못하게 함

    # 비밀번호 입력
    pw_grid = ttk.Frame(pw_frame)
    pw_grid.pack(fill="x", expand=True)
    
    enable_pw_check = ttk.Checkbutton(pw_grid, text="암호화된 백업", variable=enable_pw_var)
    enable_pw_check.pack(side="left", padx=5)
    
    ttk.Label(pw_grid, text="비밀번호:").pack(side="left", padx=(10, 5))
    password_entry = ttk.Entry(pw_grid, textvariable=password_var, show="*", state="disabled")
    password_entry.pack(side="left", fill="x", expand=True, padx=5)
    
    # 패스워드 토글 버튼
    pw_toggle_btn = ttk.Button(pw_grid, text="👁", width=3, style="Icon.TButton")
    pw_toggle_btn.pack(side="right", padx=5)
    
    # 비밀번호 입력 토글 설정
    enable_pw_check.configure(
        command=lambda: toggle_password_entry(enable_pw_var, password_entry, password_var)
    )
    
    # ==== 아티팩트 분석 탭 컨테이너 ====
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    
    # === 첫 번째 탭: 백업 탐색 ===
    explorer_tab = ttk.Frame(notebook, padding=5)
    notebook.add(explorer_tab, text="  백업 탐색  ")
    
    # 콘텐츠 영역 (PanedWindow - 더 큰 영역으로 조정)
    paned = ttk.PanedWindow(explorer_tab, orient="horizontal")
    paned.pack(fill="both", expand=True)
    
    # 백업 트리 프레임
    backup_tree_widgets = create_backup_tree_frame(paned, colors)
    paned.add(backup_tree_widgets['backup_tree_frame'], weight=3)
    
    # 파일 리스트 프레임
    file_list_widgets = create_file_list_frame(paned, colors)
    paned.add(file_list_widgets['file_list_frame'], weight=7)
    
    # === 두 번째 탭: 아티팩트 분석 ===
    artifact_tab = ttk.Frame(notebook, padding=5)
    notebook.add(artifact_tab, text="  아티팩트 분석  ")
    
    # 아티팩트 분석 옵션
    artifact_options = create_artifact_analysis_options(artifact_tab, backup_path_var, colors)
    
    # === 세 번째 탭: 대시보드 ===
    dashboard_tab = ttk.Frame(notebook, padding=5)
    notebook.add(dashboard_tab, text="  대시보드  ")
    
    # 대시보드 내용 (간단한 요약 정보)
    #create_dashboard_content(dashboard_tab, colors)
    
    # ==== 상태 표시줄 ====
    status_bar = ttk.Frame(main_frame, style="Statusbar.TFrame")
    status_bar.pack(fill="x", padx=10, pady=(5, 0))
    
    status_label = ttk.Label(status_bar, text="준비됨", padding=(10, 5))
    status_label.pack(side="left")
    
    # 진행 상태 표시
    progress = ttk.Progressbar(status_bar, mode="determinate", length=200)
    progress.pack(side="right", padx=10)
    progress["value"] = 0
    
    # 메모리 사용량 표시
    memory_label = ttk.Label(status_bar, text="메모리: 0 MB", padding=(10, 5))
    memory_label.pack(side="right")
    
    # ==== 이벤트 연결 ====
    browse_button.configure(
        command=lambda: browse_backup_path(backup_path_var, password_entry, password_var, enable_pw_var)
    )
    
    load_backup_button.configure(
        command=lambda: load_backup(
            backup_path_var.get(),
            password_var.get(),
            backup_tree_widgets['backup_tree'],
            enable_pw_var,
            file_list_widgets['file_list_tree'],
            status_label,
        )
    )
    
    # 트리뷰 이벤트 바인딩
    backup_tree_widgets['backup_tree'].bind(
        "<<TreeviewSelect>>",
        lambda event: update_file_list_from_backup_tree_click(
            event,
            file_list_widgets['file_list_tree'],
            backup_tree_widgets['backup_tree']
        )
    )
    
    file_list_widgets['file_list_tree'].bind(
        "<Double-Button-1>",
        lambda event: update_backup_tree_from_file_list_double_click(
            event,
            file_list_widgets['file_list_tree'],
            backup_tree_widgets['backup_tree']
        )
    )
    
    # 비밀번호 표시/숨김 토글
    pw_toggle_var = tk.BooleanVar(value=False)
    pw_toggle_btn.configure(
        command=lambda: toggle_password_visibility(password_entry, pw_toggle_var, pw_toggle_btn)
    )
    
    # 탭 변경 이벤트
    notebook.bind("<<NotebookTabChanged>>", lambda e: update_status_on_tab_change(e, notebook, status_label))

def toggle_password_visibility(password_entry, toggle_var, toggle_btn):
    """비밀번호 표시/숨김을 전환합니다."""
    current_state = toggle_var.get()
    if current_state:
        password_entry.config(show="*")
        toggle_btn.config(text="👁")
    else:
        password_entry.config(show="")
        toggle_btn.config(text="🔒")
    toggle_var.set(not current_state)

def update_status_on_tab_change(event, notebook, status_label):
    """탭이 변경될 때 상태 표시줄을 업데이트합니다."""
    tab_id = notebook.select()
    tab_text = notebook.tab(tab_id, "text").strip()
    status_label.config(text=f"{tab_text} 모드 활성화됨")

def create_backup_tree_frame(parent, colors):
    """백업 트리 프레임을 생성합니다."""
    frame = ttk.Frame(parent, padding=5)
    
    # 프레임 헤더
    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", pady=(0, 5))
    
    # 아이콘과 제목
    icon_label = ttk.Label(header_frame, text="📁", font=("Arial", 12))
    icon_label.pack(side="left", padx=(0, 5))
    ttk.Label(header_frame, text="백업 구조", style="Subheader.TLabel").pack(side="left")
    
    # 검색 입력 프레임
    search_frame = ttk.Frame(frame, style="Search.TFrame")
    search_frame.pack(fill="x", pady=(0, 5))
    
    # 검색 아이콘
    search_icon = ttk.Label(search_frame, text="🔍", font=("Arial", 10))
    search_icon.pack(side="left", padx=(5, 0))
    
    search_var = tk.StringVar()
    
    # 검색 입력 필드
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
    
    # 검색 버튼
    search_btn = ttk.Button(search_frame, text="검색", width=8)
    search_btn.pack(side="right", padx=5, pady=5)
    
    # 트리뷰와 스크롤바를 위한 프레임
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill="both", expand=True)
    
    # 트리뷰 스크롤바
    tree_scrollbar = ttk.Scrollbar(tree_frame)
    tree_scrollbar.pack(side="right", fill="y")
    
    # 백업 구조 트리뷰 (강화된 스타일링)
    backup_tree = ttk.Treeview(
        tree_frame,
        selectmode="browse",
        yscrollcommand=tree_scrollbar.set,
        style="BackupExplorer.Treeview"
    )
    backup_tree.pack(side="left", fill="both", expand=True)
    
    # 트리뷰 컬럼 설정
    backup_tree["columns"] = ("size", "date", "type")
    backup_tree.column("#0", width=250, minwidth=180)
    backup_tree.column("size", width=80, minwidth=50, anchor="e")
    backup_tree.column("date", width=120, minwidth=80, anchor="center")
    backup_tree.column("type", width=0, stretch=False)  # 숨겨진 타입 컬럼
    
    # 트리뷰 헤더 설정
    backup_tree.heading("#0", text="파일/폴더", anchor="w")
    backup_tree.heading("size", text="크기", anchor="e")
    backup_tree.heading("date", text="날짜", anchor="center")
    
    # 아이콘 정의
    folder_icon = "📁"
    file_icon = "📄"
    image_icon = "🖼️"
    document_icon = "📝"
    archive_icon = "🗃️"
    
    # 파일 타입에 따른 아이콘 선택 함수
    def get_file_icon(filename):
        # 파일 확장자에 따라 적절한 아이콘 반환
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            return image_icon
        elif filename.lower().endswith(('.doc', '.docx', '.pdf', '.txt')):
            return document_icon
        elif filename.lower().endswith(('.zip', '.tar', '.gz', '.rar')):
            return archive_icon
        else:
            return file_icon
    
    
    # 트리뷰에 항목을 추가하는 함수 (실제 백업 데이터 로드 시 사용)
    def add_tree_item(parent, name, size="", date="", item_type="file"):
        icon = folder_icon if item_type == "folder" else get_file_icon(name)
        return backup_tree.insert(parent, "end", text=f"{icon} {name}", values=(size, date, item_type))
    
    # 스크롤바 연결
    tree_scrollbar.config(command=backup_tree.yview)
    
    # 컨텍스트 메뉴 추가
    context_menu = tk.Menu(backup_tree, tearoff=0)
    context_menu.add_command(label="열기")
    context_menu.add_command(label="추출")
    context_menu.add_separator()
    context_menu.add_command(label="속성")
    
    def show_context_menu(event):
        context_menu.post(event.x_root, event.y_root)
    
    backup_tree.bind("<Button-3>", show_context_menu)
    

    
    return {
        'backup_tree_frame': frame,
        'backup_tree': backup_tree,
        'search_entry': search_entry,
        'search_button': search_btn,
        'add_tree_item': add_tree_item  # 외부에서 트리 항목을 추가할 수 있도록 함수 반환
    }

def create_file_list_frame(parent, colors):
    """파일 리스트 프레임을 생성합니다."""
    frame = ttk.Frame(parent, padding=5)
    
    # 프레임 헤더
    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", pady=(0, 5))
    
    # 아이콘과 제목
    icon_label = ttk.Label(header_frame, text="📋", font=("Arial", 12))
    icon_label.pack(side="left", padx=(0, 5))
    ttk.Label(header_frame, text="파일 목록", style="Subheader.TLabel").pack(side="left")
    
    # 검색 프레임
    search_frame = ttk.Frame(frame, style="Search.TFrame")
    search_frame.pack(fill="x", pady=(0, 10))
    
    # 검색 레이블과 입력 필드
    search_icon = ttk.Label(search_frame, text="🔍", font=("Arial", 10))
    search_icon.pack(side="left", padx=(5, 0))
    
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
    
    # 필터 콤보박스
    ttk.Label(search_frame, text="필터:").pack(side="left", padx=(10, 5))
    filter_var = tk.StringVar()
    filter_combo = ttk.Combobox(search_frame, textvariable=filter_var, width=12)
    filter_combo['values'] = ('모든 파일', '이미지', '문서', '데이터베이스', '설정 파일')
    filter_combo.current(0)
    filter_combo.pack(side="left", padx=5, pady=5)
    
    # 검색 버튼
    search_btn = ttk.Button(search_frame, text="검색", width=8)
    search_btn.pack(side="right", padx=5, pady=5)
    
    # 파일 목록 테이블
    table_frame = ttk.Frame(frame)
    table_frame.pack(fill="both", expand=True)
    
    # 파일 목록을 위한 트리뷰 (향상된 디자인)
    columns = ('name', 'size', 'type', 'date', 'permission')
    file_list_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style="FileList.Treeview")
    
    # 컬럼 헤더 설정
    file_list_tree.heading('name', text='파일명')
    file_list_tree.heading('size', text='크기')
    file_list_tree.heading('type', text='유형')
    file_list_tree.heading('date', text='수정일')
    file_list_tree.heading('permission', text='권한')
    
    # 컬럼 폭 설정
    file_list_tree.column('name', width=250)
    file_list_tree.column('size', width=80, anchor='e')
    file_list_tree.column('type', width=100)
    file_list_tree.column('date', width=140)
    file_list_tree.column('permission', width=80)
    
    file_list_tree.pack(side="left", fill="both", expand=True)
    
    # 수직 스크롤바
    v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=file_list_tree.yview)
    v_scrollbar.pack(side="right", fill="y")
    file_list_tree.configure(yscrollcommand=v_scrollbar.set)
    
    # 수평 스크롤바
    h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=file_list_tree.xview)
    h_scrollbar.pack(fill="x")
    file_list_tree.configure(xscrollcommand=h_scrollbar.set)
    
    # 파일 정보 요약 (향상된 정보 영역)
    info_frame = ttk.Frame(frame, style="InfoBar.TFrame", padding=5)
    info_frame.pack(fill="x", pady=5)
    
    # 파일 정보 뱃지
    file_count_label = ttk.Label(info_frame, text="항목: 0", style="Badge.TLabel", padding=(8, 3))
    file_count_label.pack(side="left", padx=(0, 10))
    
    selected_label = ttk.Label(info_frame, text="선택: 0", style="Badge.TLabel", padding=(8, 3))
    selected_label.pack(side="left", padx=10)
    
    total_size_label = ttk.Label(info_frame, text="총 크기: 0 KB", style="Badge.TLabel", padding=(8, 3))
    total_size_label.pack(side="left", padx=10)
    
    # 파일 작업 버튼 (향상된 버튼 디자인)
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill="x", pady=(5, 0))
    
    # 각 버튼에 아이콘 추가
    open_btn = ttk.Button(button_frame, text="✏️ 파일 열기", width=14, style="Action.TButton")
    open_btn.pack(side="left", padx=(0, 5))
    
    extract_btn = ttk.Button(button_frame, text="📤 추출", width=10, style="Action.TButton")
    extract_btn.pack(side="left", padx=5)
    
    export_btn = ttk.Button(button_frame, text="📋 내보내기", width=12, style="Action.TButton")
    export_btn.pack(side="left", padx=5)
    
    # 오른쪽 정렬된 버튼
    refresh_btn = ttk.Button(button_frame, text="🔄 새로고침", width=12, style="Action.TButton")
    refresh_btn.pack(side="right", padx=(5, 0))
    
    # 컨텍스트 메뉴
    context_menu = tk.Menu(file_list_tree, tearoff=0)
    context_menu.add_command(label="열기")
    context_menu.add_command(label="추출")
    context_menu.add_command(label="내보내기")
    context_menu.add_separator()
    context_menu.add_command(label="지문 분석")
    context_menu.add_command(label="메타데이터 보기")
    context_menu.add_separator()
    context_menu.add_command(label="속성")
    
    def show_context_menu(event):
        context_menu.post(event.x_root, event.y_root)
    
    file_list_tree.bind("<Button-3>", show_context_menu)
    
    return {
        'file_list_frame': frame,
        'file_list_tree': file_list_tree,
        'file_list_scrollbar': v_scrollbar,
        'file_count_label': file_count_label,
        'selected_label': selected_label,
        'total_size_label': total_size_label
    }

def create_artifact_analysis_options(parent, backup_path_var, colors):
    """아티팩트 분석 옵션을 생성합니다."""
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True)
    
    # 왼쪽 사이드바 - 아티팩트 카테고리
    sidebar = ttk.Frame(main_frame, style="Sidebar.TFrame", padding=10)
    sidebar.pack(side="left", fill="y", padx=(0, 10))
    
    # 카테고리 제목
    ttk.Label(sidebar, text="아티팩트 카테고리", style="SidebarHeader.TLabel").pack(anchor="w", pady=(0, 10))
    
    # 오른쪽 콘텐츠 영역 생성 (여기서 미리 생성)
    content_frame = ttk.Frame(main_frame, style="Content.TFrame", padding=10)
    content_frame.pack(side="right", fill="both", expand=True)
    
    # 카테고리 버튼 생성
    categories = [
        {"name": "디바이스 정보", "icon": "📱", "command": lambda: display_device_info(content_frame, backup_path_var.get())},
        {"name": "앱 목록", "icon": "📲", "command": lambda: display_app_list(content_frame, backup_path_var.get())},
        {"name": "메시지", "icon": "💬", "command": lambda: display_messages(content_frame, backup_path_var.get())},
        {"name": "통화 기록", "icon": "📞", "command": lambda: display_call_history(content_frame, backup_path_var.get())},
        {"name": "연락처", "icon": "👤", "command": lambda: display_contacts(content_frame, backup_path_var.get())},
        {"name": "위치 데이터", "icon": "📍", "command": lambda: display_location_data(content_frame, backup_path_var.get())},
        {"name": "사진 및 미디어", "icon": "🖼️", "command": lambda: display_photos_media(content_frame, backup_path_var.get())},
        {"name": "웹 브라우징", "icon": "🌐", "command": lambda: display_web_browsing(content_frame, backup_path_var.get())},
        {"name": "소셜 미디어", "icon": "👥", "command": lambda: display_social_media(content_frame, backup_path_var.get())},
        {"name": "설정 및 계정", "icon": "⚙️", "command": lambda: display_settings_accounts(content_frame, backup_path_var.get())},
    ]
    
    category_buttons = []
    selected_category = tk.StringVar()
    
    # 버튼 생성 함수
    def create_category_button(category, index):
        btn_frame = ttk.Frame(sidebar, style="SidebarItem.TFrame", padding=5)
        btn_frame.pack(fill="x", pady=2)
        
        # 선택 표시기
        indicator = ttk.Frame(btn_frame, width=3, style="Indicator.TFrame")
        indicator.pack(side="left", fill="y", padx=(0, 5))
        
        # 아이콘과 이름이 있는 버튼
        btn = ttk.Button(
            btn_frame,
            text=f"{category['icon']} {category['name']}",
            style="Sidebar.TButton",
            command=lambda: activate_category(index, category)
        )
        btn.pack(fill="x", expand=True)
        return {"button": btn, "indicator": indicator, "frame": btn_frame}
    
    # 카테고리 활성화 함수
    def activate_category(index, category):
        selected_category.set(category["name"])
        # 모든 버튼 비활성화 스타일 적용
        for i, btn_data in enumerate(category_buttons):
            if i == index:
                btn_data["frame"].configure(style="SidebarItemActive.TFrame")
                btn_data["indicator"].configure(style="IndicatorActive.TFrame")
            else:
                btn_data["frame"].configure(style="SidebarItem.TFrame")
                btn_data["indicator"].configure(style="Indicator.TFrame")
        
        # 카테고리에 맞는 콘텐츠 표시
        if category["command"]:
            category["command"]()  # 선택한 카테고리의 함수 실행
    
    # 카테고리 버튼 생성
    for i, category in enumerate(categories):
        button_data = create_category_button(category, i)
        category_buttons.append(button_data)
    
    # 시작 페이지 표시
    show_artifact_welcome_page(content_frame)
    
    return {
        "sidebar": sidebar, 
        "content_frame": content_frame,
        "category_buttons": category_buttons,
        "selected_category": selected_category
    }

def show_artifact_welcome_page(content_frame):
    """아티팩트 분석 시작 페이지를 표시합니다."""
    # 기존 위젯 삭제
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # 환영 메시지 및 안내 표시
    welcome_frame = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
    welcome_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    ttk.Label(welcome_frame, text="iOS 백업 아티팩트 분석", style="CardHeader.TLabel").pack(pady=(0, 20))
    ttk.Label(welcome_frame, text="왼쪽의 아티팩트 카테고리를 선택하여 분석을 시작하세요.", 
              style="CardText.TLabel", wraplength=400).pack(pady=10)
    
    # 아이콘 설명
    icon_frame = ttk.Frame(welcome_frame)
    icon_frame.pack(pady=20)
    
    icons = [
        {"icon": "📱", "text": "디바이스 정보"},
        {"icon": "💬", "text": "메시지"},
        {"icon": "👤", "text": "연락처"},
        {"icon": "🖼️", "text": "미디어"}
    ]
    
    for icon_data in icons:
        icon_item = ttk.Frame(icon_frame)
        icon_item.pack(side="left", padx=15)
        ttk.Label(icon_item, text=icon_data["icon"], font=("Arial", 24)).pack(anchor="center")
        ttk.Label(icon_item, text=icon_data["text"], style="CardText.TLabel").pack(anchor="center")

# 디바이스 정보 표시 함수
def display_device_info(content_frame, backup_path):
    """디바이스 정보를 콘텐츠 프레임에 표시합니다."""
    # 기존 위젯 삭제
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # 헤더 추가
    header_frame = ttk.Frame(content_frame)
    header_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(header_frame, text="📱 디바이스 정보", style="ContentHeader.TLabel").pack(side="left")
    ttk.Separator(content_frame, orient="horizontal").pack(fill="x", pady=(0, 15))
    
    try:
        # 디바이스 정보 추출
        info_data = extract_device_info(backup_path)
        
        if not info_data:
            display_error_message(content_frame, "디바이스 정보를 찾을 수 없습니다.")
            return
        
        # 정보 카드 생성
        info_card = ttk.Frame(content_frame, style="Card.TFrame", padding=15)
        info_card.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 기본 정보 섹션
        basic_info_frame = ttk.Frame(info_card)
        basic_info_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(basic_info_frame, text="기본 정보", style="CardSectionHeader.TLabel").pack(anchor="w", pady=(0, 10))
        
        # 정보 표시를 위한 그리드
        info_grid = ttk.Frame(basic_info_frame)
        info_grid.pack(fill="x")
        
        # 디바이스 기본 정보 표시
        info_items = [
            {"label": "기기 이름", "value": info_data.get("DeviceName", "알 수 없음")},
            {"label": "기기 모델", "value": info_data.get("ProductType", "알 수 없음")},
            {"label": "iOS 버전", "value": info_data.get("ProductVersion", "알 수 없음")},
            {"label": "일련번호", "value": info_data.get("SerialNumber", "알 수 없음")},
            {"label": "IMEI", "value": info_data.get("IMEI", "알 수 없음")},
            {"label": "전화번호", "value": info_data.get("PhoneNumber", "알 수 없음")},
            {"label": "마지막 백업 날짜", "value": info_data.get("LastBackupDate", "알 수 없음")}
        ]
        
        # 그리드에 정보 추가
        for i, item in enumerate(info_items):
            row = i // 2
            col = i % 2 * 2
            
            # 레이블
            label_frame = ttk.Frame(info_grid)
            label_frame.grid(row=row, column=col, sticky="w", padx=(0, 10), pady=5)
            ttk.Label(label_frame, text=item["label"] + ":", style="InfoLabel.TLabel").pack(anchor="w")
            
            # 값
            value_frame = ttk.Frame(info_grid)
            value_frame.grid(row=row, column=col+1, sticky="w", padx=(0, 20), pady=5)
            ttk.Label(value_frame, text=item["value"], style="InfoValue.TLabel").pack(anchor="w")
        
        # 추가 정보 섹션 (있는 경우)
        if "ICCID" in info_data or "MEID" in info_data or "BluetoothAddress" in info_data:
            ttk.Separator(info_card, orient="horizontal").pack(fill="x", pady=15)
            
            additional_frame = ttk.Frame(info_card)
            additional_frame.pack(fill="x")
            
            ttk.Label(additional_frame, text="추가 정보", style="CardSectionHeader.TLabel").pack(anchor="w", pady=(0, 10))
            
            # 추가 정보 그리드
            add_info_grid = ttk.Frame(additional_frame)
            add_info_grid.pack(fill="x")
            
            add_items = []
            if "ICCID" in info_data:
                add_items.append({"label": "ICCID", "value": info_data["ICCID"]})
            if "MEID" in info_data:
                add_items.append({"label": "MEID", "value": info_data["MEID"]})
            if "BluetoothAddress" in info_data:
                add_items.append({"label": "Bluetooth MAC", "value": info_data["BluetoothAddress"]})
            if "WiFiAddress" in info_data:
                add_items.append({"label": "WiFi MAC", "value": info_data["WiFiAddress"]})
                
            # 그리드에 추가 정보 추가
            for i, item in enumerate(add_items):
                row = i // 2
                col = i % 2 * 2
                
                # 레이블
                label_frame = ttk.Frame(add_info_grid)
                label_frame.grid(row=row, column=col, sticky="w", padx=(0, 10), pady=5)
                ttk.Label(label_frame, text=item["label"] + ":", style="InfoLabel.TLabel").pack(anchor="w")
                
                # 값
                value_frame = ttk.Frame(add_info_grid)
                value_frame.grid(row=row, column=col+1, sticky="w", padx=(0, 20), pady=5)
                ttk.Label(value_frame, text=item["value"], style="InfoValue.TLabel").pack(anchor="w")
    
    except Exception as e:
        display_error_message(content_frame, f"디바이스 정보를 로드하는 중 오류가 발생했습니다: {str(e)}")

def extract_device_info(backup_path):
    """백업에서 디바이스 정보를 추출합니다."""
    # 여기에는 기존 show_device_info 함수에서 정보를 추출하는 로직을 옮겨옵니다.
    # 예시 데이터 (실제로는 백업에서 추출)
    info_data = {
        "DeviceName": "iPhone",
        "ProductType": "iPhone12,1",
        "ProductVersion": "15.4.1",
        "SerialNumber": "C8PXD1ABCD12",
        "IMEI": "123456789012345",
        "PhoneNumber": "+82 10-1234-5678",
        "LastBackupDate": "2025-03-17 14:30:22",
        "ICCID": "8982123456789012345",
        "MEID": "A10000009876543",
        "BluetoothAddress": "00:11:22:33:44:55",
        "WiFiAddress": "AA:BB:CC:DD:EE:FF"
    }
    
    # 실제 구현에서는 백업 파일에서 디바이스 정보를 읽어옵니다.
    # 예: plist 파일을 파싱하여 정보 추출
    
    # 임시로 예시 데이터 반환
    return info_data


def display_error_message(content_frame, message):
    """오류 메시지를 표시합니다."""
    # 오류 메시지 프레임
    error_frame = ttk.Frame(content_frame, style="ErrorCard.TFrame", padding=15)
    error_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # 오류 아이콘과 메시지
    ttk.Label(error_frame, text="⚠️", font=("Arial", 24)).pack(pady=(0, 10))
    ttk.Label(error_frame, text=message, style="ErrorText.TLabel", wraplength=400).pack()

def display_app_list(content_frame, backup_path):
    """앱 목록을 콘텐츠 프레임에 표시합니다."""
    # 기존 위젯 삭제
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # 헤더 추가
    header_frame = ttk.Frame(content_frame)
    header_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(header_frame, text="📲 앱 목록", style="ContentHeader.TLabel").pack(side="left")
    ttk.Separator(content_frame, orient="horizontal").pack(fill="x", pady=(0, 15))
    
    # 앱 목록 카드
    app_card = ttk.Frame(content_frame, style="Card.TFrame", padding=15)
    app_card.pack(fill="both", expand=True, padx=5, pady=5)
    
    # 필터 및 검색 영역
    filter_frame = ttk.Frame(app_card)
    filter_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(filter_frame, text="앱 검색:", style="InfoLabel.TLabel").pack(side="left", padx=(0, 5))
    search_var = tk.StringVar()
    search_entry = ttk.Entry(filter_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=(0, 10))
    
    ttk.Button(filter_frame, text="검색", style="AccentButton.TButton", width=8).pack(side="left")
    
    # 앱 목록 표시 영역
    app_list_frame = ttk.Frame(app_card)
    app_list_frame.pack(fill="both", expand=True, pady=(10, 0))
    
    # 앱 목록 테이블
    columns = ("name", "bundle_id", "version", "install_date")
    app_tree = ttk.Treeview(app_list_frame, columns=columns, show="headings", selectmode="browse")
    
    # 헤더 설정
    app_tree.heading("name", text="앱 이름")
    app_tree.heading("bundle_id", text="번들 ID")
    app_tree.heading("version", text="버전")
    app_tree.heading("install_date", text="설치 날짜")
    
    # 컬럼 너비 설정
    app_tree.column("name", width=150)
    app_tree.column("bundle_id", width=200)
    app_tree.column("version", width=80, anchor="center")
    app_tree.column("install_date", width=150, anchor="center")
    
    # 스크롤바 추가
    scrollbar = ttk.Scrollbar(app_list_frame, orient="vertical", command=app_tree.yview)
    app_tree.configure(yscrollcommand=scrollbar.set)
    
    # 패킹
    app_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # 샘플 데이터 추가 (실제로는 백업에서 추출)
    sample_apps = [
        {"name": "Instagram", "bundle_id": "com.instagram.ios", "version": "230.0", "install_date": "2024-12-15"},
        {"name": "WhatsApp", "bundle_id": "net.whatsapp.WhatsApp", "version": "23.5.73", "install_date": "2024-10-22"},
        {"name": "YouTube", "bundle_id": "com.google.ios.youtube", "version": "18.10.1", "install_date": "2024-11-05"},
        {"name": "카카오톡", "bundle_id": "com.kakao.talk", "version": "10.4.5", "install_date": "2024-09-10"},
        {"name": "네이버", "bundle_id": "com.nhn.NAVER", "version": "11.14.0", "install_date": "2024-08-27"},
    ]
    
    for app in sample_apps:
        app_tree.insert("", "end", values=(app["name"], app["bundle_id"], app["version"], app["install_date"]))

def display_messages(content_frame, backup_path):
    """메시지를 콘텐츠 프레임에 표시합니다."""
    # 기존 위젯 삭제
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # 헤더 추가
    header_frame = ttk.Frame(content_frame)
    header_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(header_frame, text="💬 메시지", style="ContentHeader.TLabel").pack(side="left")
    ttk.Separator(content_frame, orient="horizontal").pack(fill="x", pady=(0, 15))
    
    # 메시지 카드
    message_card = ttk.Frame(content_frame, style="Card.TFrame", padding=15)
    message_card.pack(fill="both", expand=True, padx=5, pady=5)
    
    # 메시지 앱 선택 영역
    app_select_frame = ttk.Frame(message_card)
    app_select_frame.pack(fill="x", pady=(0, 15))
    
    ttk.Label(app_select_frame, text="메시지 앱:", style="InfoLabel.TLabel").pack(side="left", padx=(0, 5))
    
    app_var = tk.StringVar(value="기본 메시지")
    app_combo = ttk.Combobox(app_select_frame, textvariable=app_var, values=["기본 메시지", "WhatsApp", "카카오톡", "기타"])
    app_combo.pack(side="left", padx=(0, 10))
    
    ttk.Button(app_select_frame, text="조회", style="AccentButton.TButton", width=8).pack(side="left")
    
    # 메시지 표시 영역
    message_paned = ttk.PanedWindow(message_card, orient="horizontal")
    message_paned.pack(fill="both", expand=True, pady=(10, 0))
    
    # 왼쪽: 대화 목록
    convo_frame = ttk.Frame(message_paned)
    message_paned.add(convo_frame, weight=1)
    
    ttk.Label(convo_frame, text="대화 목록", style="CardSectionHeader.TLabel").pack(anchor="w", pady=(0, 10))
    
    # 대화 목록 표시
    convo_list = ttk.Treeview(convo_frame, columns=("contact", "last_msg", "date"), show="headings", selectmode="browse")
    convo_list.heading("contact", text="연락처")
    convo_list.heading("last_msg", text="마지막 메시지")
    convo_list.heading("date", text="날짜")
    
    convo_list.column("contact", width=100)
    convo_list.column("last_msg", width=150)
    convo_list.column("date", width=100, anchor="center")
    
    convo_scrollbar = ttk.Scrollbar(convo_frame, orient="vertical", command=convo_list.yview)
    convo_list.configure(yscrollcommand=convo_scrollbar.set)
    
    convo_list.pack(side="left", fill="both", expand=True)
    convo_scrollbar.pack(side="right", fill="y")
    
    # 오른쪽: 메시지 내용
    message_detail_frame = ttk.Frame(message_paned)
    message_paned.add(message_detail_frame, weight=2)
    
    ttk.Label(message_detail_frame, text="메시지 내용", style="CardSectionHeader.TLabel").pack(anchor="w", pady=(0, 10))
    
    # 메시지 내용 표시 영역
    message_content = tk.Text(message_detail_frame, wrap="word", state="disabled")
    message_content.pack(fill="both", expand=True)
    
    # 샘플 대화 목록 추가
    sample_convos = [
        {"contact": "홍길동", "last_msg": "안녕하세요", "date": "2025-03-17"},
        {"contact": "이철수", "last_msg": "내일 만나요", "date": "2025-03-16"},
        {"contact": "김영희", "last_msg": "확인했습니다", "date": "2025-03-15"},
    ]
    
    for convo in sample_convos:
        convo_list.insert("", "end", values=(convo["contact"], convo["last_msg"], convo["date"]))

def display_call_history(content_frame, backup_path):
    """통화 기록을 콘텐츠 프레임에 표시합니다."""
    # 기존 위젯 삭제
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # 헤더 추가
    header_frame = ttk.Frame(content_frame)
    header_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(header_frame, text="📞 통화 기록", style="ContentHeader.TLabel").pack(side="left")
    ttk.Separator(content_frame, orient="horizontal").pack(fill="x", pady=(0, 15))
    
    # 통화 기록 카드
    call_card = ttk.Frame(content_frame, style="Card.TFrame", padding=15)
    call_card.pack(fill="both", expand=True, padx=5, pady=5)
    
    # 필터 영역
    filter_frame = ttk.Frame(call_card)
    filter_frame.pack(fill="x", pady=(0, 15))
    
    ttk.Label(filter_frame, text="통화 유형:", style="InfoLabel.TLabel").pack(side="left", padx=(0, 5))
    
    call_type_var = tk.StringVar(value="모든 통화")
    call_type_combo = ttk.Combobox(filter_frame, textvariable=call_type_var, 
                                  values=["모든 통화", "수신", "발신", "부재중"])
    call_type_combo.pack(side="left", padx=(0, 15))
    
    ttk.Label(filter_frame, text="기간:", style="InfoLabel.TLabel").pack(side="left", padx=(0, 5))
    
    period_var = tk.StringVar(value="전체")
    period_combo = ttk.Combobox(filter_frame, textvariable=period_var, 
                               values=["전체", "오늘", "이번 주", "이번 달", "지난 달"])
    period_combo.pack(side="left", padx=(0, 10))
    
    ttk.Button(filter_frame, text="조회", style="AccentButton.TButton", width=8).pack(side="left")
    
    # 통화 기록 표시 영역
    call_frame = ttk.Frame(call_card)
    call_frame.pack(fill="both", expand=True, pady=(10, 0))
    
    # 통화 기록 테이블
    columns = ("name", "number", "type", "date", "duration")
    call_tree = ttk.Treeview(call_frame, columns=columns, show="headings", selectmode="browse")
    
    # 헤더 설정
    call_tree.heading("name", text="이름")
    call_tree.heading("number", text="전화번호")
    call_tree.heading("type", text="유형")
    call_tree.heading("date", text="날짜/시간")
    call_tree.heading("duration", text="통화 시간")
    
    # 컬럼 너비 설정
    call_tree.column("name", width=100)
    call_tree.column("number", width=120)
    call_tree.column("type", width=80, anchor="center")
    call_tree.column("date", width=150, anchor="center")
    call_tree.column("duration", width=100, anchor="center")
    
    # 스크롤바 추가
    scrollbar = ttk.Scrollbar(call_frame, orient="vertical", command=call_tree.yview)
    call_tree.configure(yscrollcommand=scrollbar.set)
    
    # 패킹
    call_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # 샘플 데이터 추가 (실제로는 백업에서 추출)
    sample_calls = [
        {"name": "홍길동", "number": "010-1234-5678", "type": "수신", "date": "2025-03-17 14:30", "duration": "02:45"},
        {"name": "이철수", "number": "010-8765-4321", "type": "발신", "date": "2025-03-16 09:15", "duration": "01:20"},
        {"name": "김영희", "number": "010-9876-5432", "type": "부재중", "date": "2025-03-15 18:45", "duration": "--:--"},
        {"name": "박지성", "number": "010-1111-2222", "type": "수신", "date": "2025-03-14 13:20", "duration": "00:45"},
        {"name": "최민수", "number": "010-3333-4444", "type": "발신", "date": "2025-03-13 16:50", "duration": "05:12"},
    ]
    
    for call in sample_calls:
        call_tree.insert("", "end", values=(call["name"], call["number"], call["type"], 
                                          call["date"], call["duration"]))
