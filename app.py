import streamlit as st
import pandas as pd
import os
import platform
import json
import altair as alt

try:
    from streamlit_gsheets import GSheetsConnection
    HAS_GSHEETS = True
except ImportError:
    HAS_GSHEETS = False



# 페이지 기본 설정 (대시보드 제목, 아이콘, 레이아웃)
st.set_page_config(
    page_title="Money Dashboard",
    page_icon="💰",
    layout="wide",
)

# Custom CSS 주입 (Kraken Design System)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
    
    /* 1. 전체 비주얼 테마: White 배경(#ffffff), Near Black 텍스트(#101114) */
    .stApp {
        background-color: #ffffff !important;
        color: #101114 !important;
        font-family: 'Kraken-Product', 'Helvetica Neue', 'IBM Plex Sans', Helvetica, Arial, sans-serif !important;
    }
    
    /* 사이드바 배경 및 테두리 (Cool Gray 8% 불투명도 적용) */
    [data-testid="stSidebar"] {
        background-color: rgba(104, 107, 130, 0.08) !important;
        border-right: 1px solid #dedee5 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
        color: #101114 !important;
        font-family: 'Kraken-Product', 'IBM Plex Sans', sans-serif !important;
    }
    
    /* 2. 타이포그래피: Display(Kraken-Brand) 및 UI/Body(Kraken-Product) 규격 준수 */
    h1 {
        font-family: 'Kraken-Brand', 'IBM Plex Sans', Helvetica, Arial, sans-serif !important;
        font-weight: 700 !important;
        font-size: 48px !important;
        letter-spacing: -1px !important;
        color: #101114 !important;
        line-height: 1.17 !important;
        margin-top: 10px !important;
        margin-bottom: 15px !important;
    }
    
    h2 {
        font-family: 'Kraken-Brand', 'IBM Plex Sans', Helvetica, Arial, sans-serif !important;
        font-weight: 700 !important;
        font-size: 36px !important;
        letter-spacing: -0.5px !important;
        color: #101114 !important;
        line-height: 1.22 !important;
        margin-top: 25px !important;
        margin-bottom: 15px !important;
    }
    
    h3 {
        font-family: 'Kraken-Brand', 'IBM Plex Sans', Helvetica, Arial, sans-serif !important;
        font-weight: 700 !important;
        font-size: 28px !important;
        letter-spacing: -0.5px !important;
        color: #101114 !important;
        line-height: 1.29 !important;
        margin-top: 20px !important;
        margin-bottom: 10px !important;
    }
    
    /* 3. 컨테이너: White 배경, Border Gray 테두리, 12px radius, 매우 은은한 그림자(whisper-level shadow) */
    .money-card {
        background-color: #ffffff !important;
        border: 1px solid #dedee5 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
        box-shadow: rgba(0, 0, 0, 0.03) 0px 4px 24px !important;
    }
    
    .money-card-title {
        font-size: 14px !important;
        color: #686b82 !important;
        margin-bottom: 8px !important;
        font-weight: 500 !important;
    }
    
    .money-card-value {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #101114 !important;
    }
    
    /* 4. 버튼: 12px radius, Kraken Purple (#7132f5) 배경, White 텍스트 (Primary) */
    div.stButton > button[data-testid="stBaseButton-primary"] {
        background-color: #7132f5 !important;
        color: #ffffff !important;
        font-family: 'Kraken-Product', 'IBM Plex Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 13px 16px !important;
        box-shadow: rgba(0, 0, 0, 0.03) 0px 4px 24px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    div.stButton > button[data-testid="stBaseButton-primary"]:hover {
        background-color: #5741d8 !important;
        color: #ffffff !important;
    }
    
    div.stButton > button[data-testid="stBaseButton-primary"]:active {
        background-color: #5b1ecf !important;
        transform: translateY(1px) !important;
    }
    
    /* 4.2 자산 업데이트 버튼 (Secondary) 스타일: 크기를 작고 컴팩트하게 조절 */
    div.stButton > button[data-testid="stBaseButton-secondary"] {
        background-color: rgba(148, 151, 169, 0.08) !important;
        color: #101114 !important;
        font-family: 'Kraken-Product', 'IBM Plex Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 12px !important;
        border: 1px solid #dedee5 !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
        width: auto !important;
        display: inline-block !important;
    }
    
    div.stButton > button[data-testid="stBaseButton-secondary"]:hover {
        background-color: rgba(148, 151, 169, 0.15) !important;
        border-color: #9497a9 !important;
    }
    
    /* Streamlit 입력 폼 디자인 변경 */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-color: #dedee5 !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="input"] > div {
        background-color: #ffffff !important;
        border-color: #dedee5 !important;
        border-radius: 8px !important;
    }
    
    input {
        color: #101114 !important;
    }
    
    /* Metric block 재정의 */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #dedee5 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: rgba(0, 0, 0, 0.03) 0px 4px 24px !important;
    }
    
    div[data-testid="stMetricLabel"] > div {
        color: #686b82 !important;
        font-weight: 500 !important;
    }
    
    div[data-testid="stMetricValue"] > div {
        color: #101114 !important;
        font-weight: 700 !important;
    }
    
    /* 헤더 투명화 및 불필요한 기본 UI(메뉴, 배포 버튼)만 숨김 - 사이드바 토글 버튼은 노출 */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    div[data-testid="stAppDeployButton"] {
        display: none !important;
    }
    #MainMenu {
        display: none !important;
    }
    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 메인 타이틀
st.markdown("<h1>Money Dashboard</h1>", unsafe_allow_html=True)
st.markdown("개인 지출과 수입을 시각화하고 자산 및 계좌 잔액을 효율적으로 관리하세요.")

# 대시보드 자산 구성 및 예외 정의
ASSET_GROUPS = {
    "카드": ["쿠팡와우카드", "토스모임카드", "아빠신한카드"],
    "운영계좌": ["토스모임계좌", "미래에셋네이버", "기타현금"],
    "투자/저축": ["하나증권", "우리은행네이버", "OK저축은행"]
}

EXCLUDED_ASSETS = ["아빠신한카드"]

# 계좌 평탄화 리스트
ALL_ACCOUNTS = []
for group_name, accs in ASSET_GROUPS.items():
    ALL_ACCOUNTS.extend(accs)

# 구글 스프레드시트 연동 관련 헬퍼 함수 정의
def get_gsheets_connection():
    if not HAS_GSHEETS:
        return None
    try:
        # st.secrets 내에 [connections.gsheets] 설정이 있고 private_key가 등록된 경우 개행문자(\\n) 자동 보정
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            gsheets_conf = st.secrets["connections"]["gsheets"]
            if "private_key" in gsheets_conf:
                key_str = gsheets_conf["private_key"]
                if "\\n" in key_str:
                    st.secrets["connections"]["gsheets"]["private_key"] = key_str.replace("\\n", "\n")
        
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except Exception as e:
        return None

# 자산 설정 파일(settings.json) 입출력 함수 정의
SETTINGS_FILE = "settings.json"

def load_settings():
    # 1. 구글 스프레드시트에서 로드 시도
    conn = get_gsheets_connection()
    if conn:
        try:
            df_settings = conn.read(worksheet="Settings", ttl="1h")
            settings_dict = {}
            if df_settings is not None and not df_settings.empty:
                for idx, r in df_settings.iterrows():
                    acc = r.get("Account")
                    bal = r.get("Balance")
                    if acc:
                        try:
                            settings_dict[acc] = int(bal)
                        except:
                            settings_dict[acc] = 0
            
            # 누락된 계좌 0원으로 채움
            for acc in ALL_ACCOUNTS:
                if acc not in settings_dict:
                    settings_dict[acc] = 0
            
            # 로컬 백업 저장
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings_dict, f, ensure_ascii=False, indent=4)
            return settings_dict
        except Exception as e:
            try:
                local_settings = {}
                if os.path.exists(SETTINGS_FILE):
                    try:
                        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                            local_settings = json.load(f)
                    except:
                        pass
                df_settings = pd.DataFrame([
                    {"Account": acc, "Balance": local_settings.get(acc, 0)}
                    for acc in ALL_ACCOUNTS
                ])
                conn.create(worksheet="Settings", data=df_settings)
                return {acc: local_settings.get(acc, 0) for acc in ALL_ACCOUNTS}
            except Exception as ex:
                st.error(f"구글 시트에 Settings 탭을 연동하지 못했습니다: {e} / {ex}")

    # 2. 로컬 백업 파일에서 로드 (오프라인 모드)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {acc: 0 for acc in ALL_ACCOUNTS}

def save_settings(settings_data):
    # 1. 구글 스프레드시트에 저장 시도
    conn = get_gsheets_connection()
    if conn:
        try:
            df_settings = pd.DataFrame([
                {"Account": acc, "Balance": settings_data.get(acc, 0)}
                for acc in ALL_ACCOUNTS
            ])
            conn.update(worksheet="Settings", data=df_settings)
        except Exception as e:
            st.error(f"구글 시트에 기초 자산 설정을 저장하지 못했습니다: {e}")

    # 2. 로컬 백업 파일에 항상 저장
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"로컬 파일 저장 실패: {e}")

# CSV 데이터 로드 함수 (구글 스프레드시트 우선 로드 및 로컬 백업)
@st.cache_data
def load_data():
    file_path = "expense_data.csv"
    
    # 1. 구글 스프레드시트에서 로드 시도
    conn = get_gsheets_connection()
    if conn:
        try:
            df = conn.read(worksheet="Transactions", ttl="1h")
            if df is not None and not df.empty:
                # 데이터 타입 및 날짜 포맷팅 검증
                df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
                df = df.dropna(subset=['Date'])
                df = df.sort_values(by='Date').reset_index(drop=True)
                
                # 로컬 CSV 파일에 백업 저장
                df_to_save = df.copy()
                df_to_save['Date'] = df_to_save['Date'].dt.strftime('%Y-%m-%d')
                df_to_save.to_csv(file_path, index=False, encoding='utf-8-sig')
                
                # 안내 문구 (구글 연동 완료 표시)
                st.sidebar.success("✅ 구글 스프레드시트 데이터 연동 중")
                return df
            else:
                return pd.DataFrame(columns=['Date', 'Account', 'Category', 'Amount', 'Type', 'Memo'])
        except Exception as e:
            try:
                df_empty = pd.DataFrame(columns=['Date', 'Account', 'Category', 'Amount', 'Type', 'Memo'])
                conn.create(worksheet="Transactions", data=df_empty)
                return df_empty
            except Exception as ex:
                st.error(f"구글 시트 로드 중 에러 발생, 로컬 CSV 백업을 사용합니다: {e} / {ex}")

    # 2. 로컬 CSV 파일에서 로드 (오프라인 모드)
    st.sidebar.warning("⚠️ 로컬 오프라인 데이터 사용 중")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
        df = df.dropna(subset=['Date'])
        df = df.sort_values(by='Date').reset_index(drop=True)
        return df
    else:
        df = pd.DataFrame(columns=['Date', 'Account', 'Category', 'Amount', 'Type', 'Memo'])
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        return df

# 데이터 불러오기
df = load_data()

# 대시보드 탭과 자산 설정 탭 구현
tab_dashboard, tab_settings = st.tabs(["📊 대시보드", "⚙️ 자산 설정"])

# 1. 대시보드 탭 로직
with tab_dashboard:
    if st.session_state.get('tx_deleted'):
        st.success("거래가 성공적으로 삭제되었습니다! 🗑️")
        del st.session_state['tx_deleted']
    if st.session_state.get('tx_added'):
        st.success("거래가 성공적으로 추가되었습니다! ➕")
        del st.session_state['tx_added']

    if not df.empty:
        # ------------------ 사이드바 필터 ------------------
        st.sidebar.header("🔍 필터 옵션")
        
        if st.sidebar.button("🔄 자산 업데이트", key="refresh_cache_btn", type="secondary"):
            st.cache_data.clear()
            st.rerun()
            
        st.sidebar.markdown("---")
        
        # 날짜 범위 설정을 위해 데이터의 최소/최대 날짜 산출
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        
        # 📅 날짜 조회 기간 필터 (st.sidebar.date_input 범위 설정 지원)
        selected_date_range = st.sidebar.date_input(
            "조회 기간을 선택하세요:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_range_picker"
        )
        
        # 선택 결과 튜플 처리 (사용자가 범위 선택 중일 때 오류 방지 포함)
        if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
            start_date, end_date = selected_date_range
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            calculation_date = end_date
        else:
            # 시작일만 선택된 경우 시작일 이후의 데이터 조회
            start_date = pd.to_datetime(selected_date_range[0])
            filtered_df = df[df['Date'] >= start_date]
            calculation_date = pd.to_datetime(max_date)
            
        # 대시보드 대제목 배치
        st.markdown("<h2>🏦 자산 현황</h2>", unsafe_allow_html=True)

        # 1. 자산/계좌 필터 (대시보드 메인 본문 상단 배치 - 콤팩트 디자인)
        st.markdown("<p style='font-size: 13px; color: #686b82; margin-bottom: 4px; font-weight: 500;'>🏦 자산/계좌 필터</p>", unsafe_allow_html=True)
        asset_filter_preset = st.selectbox(
            "자산/계좌를 선택하세요:",
            options=["전체 보기", "직접 선택"],
            index=0,
            key="asset_filter_preset",
            label_visibility="collapsed"
        )
        
        if asset_filter_preset == "전체 보기":
            selected_accounts = ALL_ACCOUNTS
        else: # 직접 선택
            selected_accounts = st.multiselect(
                "대상 자산/계좌 직접 선택:",
                options=ALL_ACCOUNTS,
                default=[acc for acc in ALL_ACCOUNTS if acc not in EXCLUDED_ASSETS],
                key="selected_accounts_multiselect"
            )
            
        # 선택된 자산으로 데이터 필터링
        filtered_df = filtered_df[filtered_df['Account'].isin(selected_accounts)]
        
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

        # 2. 카테고리 필터 생성 (사이드바 - 상시 전체 목록 노출)
        ALL_CATEGORIES = [
            "전체", "급여", "이자", "기타 수입",
            "식비", "카페/디저트", "교통비", "쇼핑", "옷/의류",
            "주거비", "문화생활", "의료/건강", "구독료", "교육비", "생활용품", "경조사비", "기타 지출"
        ]
        selected_category = st.sidebar.selectbox("카테고리를 선택하세요:", ALL_CATEGORIES)
        
        # 선택된 카테고리 데이터 필터링
        if selected_category != "전체":
            filtered_df = filtered_df[filtered_df['Category'] == selected_category]

        # ------------------ 새 거래 추가 Form (사이드바 - dynamic) ------------------
        st.sidebar.markdown("---")
        st.sidebar.subheader("➕ 새 거래 추가")
        
        new_date = st.sidebar.date_input("날짜", value=pd.Timestamp.now().date(), key="new_date")
        new_account = st.sidebar.selectbox("자산/계좌", ALL_ACCOUNTS, key="new_account")
        
        # 아빠신한카드인 경우 자산제외 판단 문구 출력
        if new_account == "아빠신한카드":
            st.sidebar.markdown(
                '<span style="background-color: rgba(104,107,130,0.12); color: #484b5e; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; display: block; margin-top:-10px; margin-bottom:12px;">⚠️ 자산제외</span>', 
                unsafe_allow_html=True
            )
            
        new_type = st.sidebar.selectbox("구분", ["Income", "Expense"], key="new_type")
        
        # 구분값(Income/Expense)에 따른 분류(Category) 목록 동적 정의
        if new_type == "Income":
            category_options = ["급여", "이자", "기타 수입"]
        else:
            category_options = ["식비", "카페/디저트", "교통비", "쇼핑", "옷/의류", "주거비", "문화생활", "의료/건강", "구독료", "교육비", "생활용품", "경조사비", "기타 지출"]
            
        new_category = st.sidebar.selectbox("분류", category_options, key="new_category")
        new_amount = st.sidebar.number_input("금액 (원)", min_value=0, step=1000, value=0, key="new_amount")
        new_memo = st.sidebar.text_input("메모", value="", key="new_memo")
        
        submit_button = st.sidebar.button("거래 추가", key="submit_tx_btn", type="primary")
        
        if submit_button:
            if new_amount > 0:
                new_row_df = pd.DataFrame([{
                    'Date': new_date.strftime('%Y-%m-%d'),
                    'Account': new_account,
                    'Category': new_category,
                    'Amount': new_amount,
                    'Type': new_type,
                    'Memo': new_memo
                }])
                
                # 1. 구글 스프레드시트에 저장 시도
                conn = get_gsheets_connection()
                if conn:
                    try:
                        current_df = conn.read(worksheet="Transactions", ttl=0)
                        new_row = pd.DataFrame([{
                            'Date': new_date.strftime('%Y-%m-%d'),
                            'Account': new_account,
                            'Category': new_category,
                            'Amount': new_amount,
                            'Type': new_type,
                            'Memo': new_memo
                        }])
                        if current_df is not None and not current_df.empty:
                            if 'Date' in current_df.columns:
                                current_df['Date'] = pd.to_datetime(current_df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
                            updated_df = pd.concat([current_df, new_row], ignore_index=True)
                        else:
                            updated_df = new_row
                        conn.update(worksheet="Transactions", data=updated_df)
                    except Exception as e:
                        st.error(f"구글 시트에 거래를 추가하지 못했습니다: {e}")
                
                # 2. 로컬 CSV 백업 파일에 항상 추가
                new_row_df.to_csv("expense_data.csv", mode='a', header=False, index=False, encoding='utf-8-sig')
                
                st.cache_data.clear()
                st.session_state['tx_added'] = True
                st.rerun()
            else:
                st.sidebar.warning("금액을 0원보다 크게 입력해 주세요.")

        # ------------------ 주요 지표 계산 ------------------
        income_df = filtered_df[filtered_df['Type'] == 'Income']
        expense_df = filtered_df[filtered_df['Type'] == 'Expense']
        
        total_income = income_df['Amount'].sum()
        total_expense = expense_df['Amount'].sum()
        
        # 아빠신한카드 지출액 계산 (자산 필터에 포함된 경우에만 집계됨)
        dad_card_expense = expense_df[expense_df['Account'] == '아빠신한카드']['Amount'].sum()
        
        # 순 잔액 = 총 수입 - (총 지출 - 아빠신한카드 지출)
        balance = total_income - (total_expense - dad_card_expense)
        
        # ------------------ 상단 요약 카드 (Metrics) ------------------
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="💵 총 수입 (Income)", 
                value=f"{total_income:,.0f} 원", 
                delta=None
            )
        with col2:
            st.metric(
                label="💸 총 지출 (Expense)", 
                value=f"{total_expense:,.0f} 원", 
                delta=f"-{total_expense:,.0f} 원" if total_expense > 0 else "0 원",
                delta_color="inverse"
            )
        with col3:
            st.metric(
                label="📈 순 잔액 (Balance)", 
                value=f"{balance:,.0f} 원", 
                delta=f"+{balance:,.0f} 원" if balance >= 0 else f"{balance:,.0f} 원",
                delta_color="normal"
            )
        
        st.markdown("---")
        
        # ------------------ 3. 자산별 잔액 및 수입/지출 통계 ------------------

        
        # settings.json 또는 구글 스프레드시트에서 설정된 자산 잔액 로드
        base_balances = load_settings()
        
        # 자산 잔액은 수입/지출 내역과 무관하게 사용자가 등록한 잔액 그대로 노출
        account_balances = {acc: base_balances.get(acc, 0) for acc in ALL_ACCOUNTS}
            
        stat_col1, stat_col2 = st.columns([3, 2])
        
        with stat_col1:
            st.markdown("<h3 style='margin-top:0;'>💰 그룹별 자산 현황</h3>", unsafe_allow_html=True)
            # 카드를 제외하고 운영계좌와 투자/저축 그룹만 노출
            display_groups = {k: v for k, v in ASSET_GROUPS.items() if k in ["운영계좌", "투자/저축"]}
            acc_cols = st.columns(2)
            
            for idx, (group_name, accounts) in enumerate(display_groups.items()):
                # 그룹별 총액 계산 (EXCLUDED_ASSETS 즉, '아빠신한카드' 등은 총액 연산에서 제외)
                group_total = sum(account_balances.get(acc, 0) for acc in accounts if acc not in EXCLUDED_ASSETS)
                
                # 개별 자산 항목 HTML 생성 (Markdown 오작동 방지용 한 줄 구조)
                items_html = ""
                for acc in accounts:
                    val = account_balances.get(acc, 0)
                    val_color = "#101114"
                    if val < 0:
                        val_color = "#c0392b"
                    
                    # 제외 대상 자산은 라벨 뒤에 (제외) 표시와 흐린 색상 스타일 적용
                    if acc in EXCLUDED_ASSETS:
                        acc_label = f'<span style="color: #9497a9;">{acc} (제외)</span>'
                    else:
                        acc_label = f'<span style="color: #686b82;">{acc}</span>'
                    
                    items_html += f'<div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 6px;">{acc_label}<span style="font-weight: 600; color: {val_color};">{val:,.0f} 원</span></div>'
                    
                group_total_color = "#7132f5" if group_total >= 0 else "#c0392b"
                
                # 깨짐 없는 깔끔한 인라인 HTML 레이아웃 코드
                card_html = (
                    f'<div class="money-card">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">'
                    f'<span style="font-weight: 700; font-size: 16px; color: #101114;">{group_name}</span>'
                    f'<span style="font-weight: 700; font-size: 16px; color: {group_total_color};">{group_total:,.0f} 원</span>'
                    f'</div>'
                    f'<div style="border-top: 1px solid #dedee5; margin-bottom: 12px; height: 1px;"></div>'
                    f'<div style="display: flex; flex-direction: column;">'
                    f'{items_html}'
                    f'</div>'
                    f'</div>'
                )
                
                with acc_cols[idx]:
                    st.markdown(card_html, unsafe_allow_html=True)
                    
        with stat_col2:
            st.markdown("<h3 style='margin-top:0;'>📊 수입/지출 비중</h3>", unsafe_allow_html=True)
            
            # Altair 인터랙티브 수입/지출 차트 구현 (축 제목 제거, x축 라벨 제거)
            inc_exp_data = pd.DataFrame({
                '구분': ['수입', '지출'],
                '금액': [total_income, total_expense]
            })
            inc_exp_chart = alt.Chart(inc_exp_data).mark_bar(
                cornerRadiusEnd=6,
                height=22
            ).encode(
                x=alt.X('금액:Q', title=None, axis=alt.Axis(labels=False, ticks=False, grid=True, gridColor='#dedee5')),
                y=alt.Y('구분:N', title=None, sort=None, axis=alt.Axis(labelColor='#101114', labelFontSize=12)),
                color=alt.Color('구분:N', scale=alt.Scale(domain=['수입', '지출'], range=['#7132f5', '#9497a9']), legend=None),
                tooltip=[
                    alt.Tooltip('구분:N', title='구분'),
                    alt.Tooltip('금액:Q', title='금액', format=',.0f')
                ]
            ).properties(
                height=150,
                background='#ffffff'
            ).configure_view(
                stroke=None
            )
            
            st.altair_chart(inc_exp_chart, width="stretch")

        st.markdown("---")
        
        # ------------------ 소비 분석 차트 (Altair 인터랙티브 시각화) ------------------
        st.markdown("<h2>📊 소비 분석</h2>", unsafe_allow_html=True)
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("🗂️ 카테고리별 지출 금액")
            if not expense_df.empty:
                cat_expense = expense_df.groupby('Category')['Amount'].sum().reset_index()
                
                # Altair 가로 막대 차트 (축 제목 제거, x축 라벨 제거)
                cat_chart = alt.Chart(cat_expense).mark_bar(
                    color='#7132f5',
                    cornerRadiusEnd=6,
                    height=20
                ).encode(
                    x=alt.X('Amount:Q', title=None, axis=alt.Axis(labels=False, ticks=False, grid=True, gridColor='#dedee5')),
                    y=alt.Y('Category:N', title=None, sort='-x', axis=alt.Axis(labelColor='#101114', labelFontSize=11)),
                    tooltip=[
                        alt.Tooltip('Category:N', title='카테고리'),
                        alt.Tooltip('Amount:Q', title='지출 금액', format=',.0f')
                    ]
                ).properties(
                    height=300,
                    background='#ffffff'
                ).configure_view(
                    stroke=None
                )
                
                st.altair_chart(cat_chart, width="stretch")
            else:
                st.info("선택한 조건에 해당하는 지출 데이터가 없습니다.")
                
        with chart_col2:
            st.subheader("📅 일자별 지출 추이")
            if not expense_df.empty:
                daily_expense = expense_df.groupby('Date')['Amount'].sum().reset_index()
                daily_expense = daily_expense.sort_values(by='Date')
                daily_expense['날짜'] = daily_expense['Date'].dt.strftime('%Y-%m-%d')
                
                # Altair 인터랙티브 라인 차트 (라인 끊김 현상 방지를 위해 Line과 Point 레이어 명시적 결합)
                base_trend = alt.Chart(daily_expense).encode(
                    x=alt.X('날짜:N', title=None, axis=alt.Axis(labelAngle=-45, labelColor='#101114', labelFontSize=10)),
                    y=alt.Y('Amount:Q', title=None, axis=alt.Axis(grid=True, gridColor='#dedee5'))
                )
                
                trend_line = base_trend.mark_line(
                    color='#7132f5',
                    strokeWidth=3
                )
                
                trend_points = base_trend.mark_point(
                    color='#7132f5',
                    fill='#ffffff',
                    size=60,
                    strokeWidth=2
                )
                
                trend_chart = alt.layer(trend_line, trend_points).encode(
                    tooltip=[
                        alt.Tooltip('날짜:N', title='날짜'),
                        alt.Tooltip('Amount:Q', title='지출 금액', format=',.0f')
                    ]
                ).properties(
                    height=300,
                    background='#ffffff'
                ).configure_view(
                    stroke=None
                )
                
                st.altair_chart(trend_chart, width="stretch")
            else:
                st.info("선택한 조건에 해당하는 지출 데이터가 없습니다.")

        st.markdown("---")

        # ------------------ 상세 데이터 내역 ------------------
        st.markdown("<h2>📑 상세 내역 표</h2>", unsafe_allow_html=True)
        
        display_df = filtered_df.copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        display_df = display_df[['Date', 'Account', 'Category', 'Amount', 'Type', 'Memo']]
        
        st.dataframe(
            display_df.sort_values(by='Date', ascending=False), 
            width="stretch"
        )
        
        # 최근 거래 삭제 기능 추가
        st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
        st.markdown("<h3>🗑️ 거래 내역 삭제 및 수정</h3>", unsafe_allow_html=True)
        st.markdown(
            "잘못 입력한 항목이 있다면 최근 내역에서 선택하여 삭제할 수 있습니다.<br>"
            "*(더 상세한 내용 수정은 연동된 <b>[구글 스프레드시트]</b>에서 셀을 직접 편집하셔도 실시간으로 반영됩니다!)*", 
            unsafe_allow_html=True
        )
        
        # 전체 데이터 중 최근 20개 거래 추출 (가장 최신 것이 위로 오게 정렬)
        df_sorted_raw = df.copy()
        df_sorted_raw['Date_Str'] = df_sorted_raw['Date'].dt.strftime('%Y-%m-%d')
        df_sorted_raw['display'] = df_sorted_raw.apply(
            lambda r: f"[{r['Date_Str']}] {r['Account']} | {r['Category']} | {r['Amount']:,.0f}원 | {r['Type']} | {r['Memo']}",
            axis=1
        )
        
        # 날짜 내림차순 정렬 후 최신 20개
        df_sorted_raw = df_sorted_raw.sort_values(by='Date', ascending=False)
        recent_txs = df_sorted_raw.head(20)
        
        if not recent_txs.empty:
            tx_to_delete_display = st.selectbox(
                "삭제할 거래를 선택하세요:",
                recent_txs['display'].tolist(),
                key="tx_delete_selectbox"
            )
            
            # Master df에서 매칭되는 인덱스 찾기
            selected_idx = recent_txs[recent_txs['display'] == tx_to_delete_display].index[0]
            
            delete_btn = st.button("선택한 거래 삭제", key="delete_tx_btn", type="primary")
            if delete_btn:
                # master df에서 삭제
                updated_df = df.drop(selected_idx).reset_index(drop=True)
                
                # 1. 구글 스프레드시트 업데이트
                conn = get_gsheets_connection()
                if conn:
                    try:
                        df_to_save = updated_df.copy()
                        df_to_save['Date'] = df_to_save['Date'].dt.strftime('%Y-%m-%d')
                        conn.update(worksheet="Transactions", data=df_to_save)
                    except Exception as e:
                        st.error(f"구글 시트 업데이트에 실패했습니다: {e}")
                
                # 2. 로컬 CSV 백업 파일 업데이트
                df_to_save = updated_df.copy()
                df_to_save['Date'] = df_to_save['Date'].dt.strftime('%Y-%m-%d')
                df_to_save.to_csv("expense_data.csv", index=False, encoding='utf-8-sig')
                
                st.cache_data.clear()
                st.session_state['tx_deleted'] = True
                st.rerun()
        else:
            st.info("삭제할 거래 내역이 없습니다.")
        
    else:
        st.warning("데이터가 비어 있습니다. 구글 스프레드시트 또는 로컬 데이터를 확인해 주세요.")

# 2. 자산 설정 탭 로직
with tab_settings:
    st.markdown("<h2>⚙️ 자산별 현재 잔액 설정</h2>", unsafe_allow_html=True)
    st.markdown("각 자산/계좌의 현재 잔액을 설정합니다. 이곳에 입력하신 잔액이 대시보드의 자산 현황에 그대로 표시됩니다.")
    st.markdown("---")
    
    # 설정 저장 성공 안내 문구 출력 (Rerun 시에도 유지)
    if st.session_state.get('settings_saved'):
        st.success("자산 잔액 설정이 성공적으로 저장되었습니다! 💾")
        del st.session_state['settings_saved']
        
    current_settings = load_settings()
    new_settings = {}
    
    # 자산 잔액 입력을 위한 폼 구성
    with st.form("settings_form"):
        for group_name, accounts in ASSET_GROUPS.items():
            st.markdown(f"<h3>📂 {group_name}</h3>", unsafe_allow_html=True)
            cols = st.columns(len(accounts))
            for idx, acc in enumerate(accounts):
                with cols[idx]:
                    # 음수(카드 한도 또는 잔액 등) 입력도 가능하도록 min_value 제한 없음
                    new_settings[acc] = st.number_input(
                        f"{acc} 잔액 (원)", 
                        step=10000, 
                        value=int(current_settings.get(acc, 0)),
                        key=f"setting_{acc}"
                    )
            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
            
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        save_btn = st.form_submit_button("설정 저장", type="primary")
        
        if save_btn:
            save_settings(new_settings)
            st.session_state['settings_saved'] = True
            st.rerun()
