"""Premium SaaS UI styles and custom CSS definitions for Streamlit.

Implements a Vercel/Linear/Stripe-inspired dark theme with glassmorphism,
gradient accents, and micro-animations.
"""


def get_custom_css() -> str:
    """Returns the custom CSS string for premium dark mode glassmorphism styling."""
    return """
    <style>
        /* ====================================================
           TYPOGRAPHY — Google Fonts
           ==================================================== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

        /* ====================================================
           DESIGN TOKENS (CSS Variables)
           ==================================================== */
        :root {
            --bg-primary: #0B0F19;
            --bg-secondary: #111827;
            --bg-card: #151F32;
            --bg-card-glass: rgba(21, 31, 50, 0.65);
            --accent-primary: #7C3AED;
            --accent-primary-glow: rgba(124, 58, 237, 0.25);
            --accent-secondary: #06B6D4;
            --accent-secondary-glow: rgba(6, 182, 212, 0.2);
            --text-primary: #F1F5F9;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            --border-subtle: rgba(255, 255, 255, 0.06);
            --border-hover: rgba(124, 58, 237, 0.3);
            --success: #10B981;
            --success-glow: rgba(16, 185, 129, 0.35);
            --danger: #EF4444;
            --danger-glow: rgba(239, 68, 68, 0.35);
            --warning: #F59E0B;
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 20px;
            --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
            --transition-smooth: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --shadow-card: 0 8px 32px -8px rgba(0, 0, 0, 0.4);
            --shadow-hover: 0 16px 48px -12px rgba(124, 58, 237, 0.15);
        }

        /* ====================================================
           GLOBAL BACKGROUND & BODY
           ==================================================== */
        html, body, [data-testid="stAppViewContainer"],
        [data-testid="stApp"] {
            background-color: var(--bg-primary) !important;
            font-family: 'Inter', -apple-system,
                BlinkMacSystemFont, sans-serif !important;
            color: var(--text-primary) !important;
        }
        [data-testid="stHeader"] {
            background-color: rgba(11, 15, 25, 0.8) !important;
            backdrop-filter: blur(12px) !important;
        }

        /* ====================================================
           SIDEBAR — Frosted Glass
           ==================================================== */
        [data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                rgba(17, 24, 39, 0.92) 0%,
                rgba(11, 15, 25, 0.95) 100%
            ) !important;
            backdrop-filter: blur(24px) saturate(180%) !important;
            border-right: 1px solid var(--border-subtle) !important;
        }
        [data-testid="stSidebar"] * {
            font-family: 'Inter', sans-serif !important;
        }
        [data-testid="stSidebar"] .stRadio > label {
            font-weight: 500 !important;
            color: var(--text-secondary) !important;
            letter-spacing: 0.01em !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            font-size: 0.7rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.12em !important;
            color: var(--text-muted) !important;
            font-weight: 600 !important;
            margin-top: 1rem !important;
        }

        /* ====================================================
           HEADING HIERARCHY — Outfit Font
           ==================================================== */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            letter-spacing: -0.025em !important;
        }
        h1 { font-size: 2rem !important; font-weight: 700 !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.15rem !important; color: var(--text-secondary) !important; }

        /* ====================================================
           APP TITLE — Animated Gradient Text
           ==================================================== */
        .app-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.65rem;
            font-weight: 800;
            background: linear-gradient(
                135deg,
                var(--accent-primary) 0%,
                var(--accent-secondary) 50%,
                var(--accent-primary) 100%
            );
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient-shift 4s ease infinite;
            margin-bottom: 6px;
            line-height: 1.3;
        }
        @keyframes gradient-shift {
            0%   { background-position: 0% 50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Hero title variant for main content area */
        .hero-title {
            font-family: 'Outfit', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(
                135deg,
                #FFFFFF 0%,
                var(--accent-primary) 40%,
                var(--accent-secondary) 100%
            );
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient-shift 6s ease infinite;
            margin-bottom: 8px;
            letter-spacing: -0.03em;
            line-height: 1.15;
        }
        .hero-subtitle {
            color: var(--text-secondary);
            font-size: 1.1rem;
            font-weight: 400;
            line-height: 1.6;
            max-width: 640px;
        }

        /* ====================================================
           VERSION BADGE
           ==================================================== */
        .version-badge {
            display: inline-block;
            background: rgba(124, 58, 237, 0.15);
            color: var(--accent-primary);
            font-size: 0.7rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 20px;
            border: 1px solid rgba(124, 58, 237, 0.25);
            letter-spacing: 0.05em;
            margin-bottom: 16px;
        }

        /* ====================================================
           GLASSMORPHISM CARD
           ==================================================== */
        .glass-card {
            background: var(--bg-card-glass) !important;
            backdrop-filter: blur(16px) saturate(160%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(160%) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-lg) !important;
            padding: 24px !important;
            margin-bottom: 20px !important;
            box-shadow: var(--shadow-card) !important;
            transition: all var(--transition-smooth) !important;
        }
        .glass-card:hover {
            transform: translateY(-3px) !important;
            border-color: var(--border-hover) !important;
            box-shadow: var(--shadow-hover) !important;
        }

        /* ====================================================
           KPI METRIC CARDS
           ==================================================== */
        .kpi-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 16px 12px;
            position: relative;
            overflow: hidden;
        }
        .kpi-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 40%;
            height: 2px;
            background: linear-gradient(
                90deg,
                transparent,
                var(--accent-primary),
                transparent
            );
            border-radius: 2px;
        }
        .kpi-icon {
            font-size: 1.5rem;
            margin-bottom: 4px;
            opacity: 0.9;
        }
        .kpi-val {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(
                135deg, var(--accent-primary),
                var(--accent-secondary)
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Outfit', sans-serif;
            margin: 6px 0 2px;
            line-height: 1.2;
        }
        .kpi-lbl {
            font-size: 0.72rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 600;
        }

        /* ====================================================
           STATUS INDICATOR — Pulsing Dot
           ==================================================== */
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            position: relative;
        }
        .status-dot.online {
            background-color: var(--success);
            box-shadow: 0 0 8px var(--success-glow);
            animation: pulse-green 2s ease-in-out infinite;
        }
        .status-dot.offline {
            background-color: var(--danger);
            box-shadow: 0 0 8px var(--danger-glow);
            animation: pulse-red 2s ease-in-out infinite;
        }
        @keyframes pulse-green {
            0%, 100% { box-shadow: 0 0 4px var(--success-glow); }
            50% { box-shadow: 0 0 16px var(--success-glow); }
        }
        @keyframes pulse-red {
            0%, 100% { box-shadow: 0 0 4px var(--danger-glow); }
            50% { box-shadow: 0 0 16px var(--danger-glow); }
        }

        /* ====================================================
           BUTTONS — Gradient Accent
           ==================================================== */
        .stButton>button {
            background: linear-gradient(
                135deg,
                var(--accent-primary) 0%,
                #6D28D9 100%
            ) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: var(--radius-sm) !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.875rem !important;
            padding: 10px 28px !important;
            transition: all var(--transition-fast) !important;
            box-shadow: 0 4px 14px -4px var(--accent-primary-glow) !important;
            letter-spacing: 0.01em !important;
        }
        .stButton>button:hover {
            transform: translateY(-1px) scale(1.01) !important;
            box-shadow: 0 8px 24px -4px var(--accent-primary-glow) !important;
            filter: brightness(1.1) !important;
        }
        .stButton>button:active {
            transform: translateY(0) scale(0.99) !important;
        }

        /* Download buttons — Secondary style */
        .stDownloadButton>button {
            background: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-sm) !important;
            font-weight: 500 !important;
            font-family: 'Inter', sans-serif !important;
            transition: all var(--transition-fast) !important;
        }
        .stDownloadButton>button:hover {
            border-color: var(--accent-primary) !important;
            background: rgba(124, 58, 237, 0.08) !important;
            transform: translateY(-1px) !important;
        }

        /* ====================================================
           CHAT MESSAGE BUBBLES
           ==================================================== */
        .chat-msg-user {
            background: linear-gradient(
                135deg,
                rgba(124, 58, 237, 0.12) 0%,
                rgba(124, 58, 237, 0.06) 100%
            ) !important;
            border: 1px solid rgba(124, 58, 237, 0.18) !important;
            border-radius: var(--radius-md) var(--radius-md)
                4px var(--radius-md) !important;
            padding: 14px 18px !important;
            margin: 12px 0 !important;
            max-width: 90%;
            margin-left: auto !important;
        }
        .chat-msg-user strong {
            color: var(--accent-primary) !important;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .chat-msg-assistant {
            background: var(--bg-card-glass) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) var(--radius-md)
                var(--radius-md) 4px !important;
            padding: 14px 18px !important;
            margin: 12px 0 !important;
            max-width: 90%;
            line-height: 1.65;
        }
        .chat-msg-assistant strong {
            color: var(--accent-secondary) !important;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* ====================================================
           TEXT INPUT & SELECT STYLING
           ==================================================== */
        .stTextInput>div>div>input,
        .stSelectbox>div>div>div {
            background-color: var(--bg-secondary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', sans-serif !important;
            transition: border-color var(--transition-fast) !important;
        }
        .stTextInput>div>div>input:focus {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 2px var(--accent-primary-glow) !important;
        }

        /* ====================================================
           DATAFRAME / TABLE STYLING
           ==================================================== */
        [data-testid="stTable"],
        [data-testid="stDataFrame"] {
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            overflow: hidden !important;
        }
        [data-testid="stDataFrame"] [data-testid="glideDataEditor"] {
            border-radius: var(--radius-md) !important;
        }

        /* ====================================================
           FILE UPLOADER
           ==================================================== */
        [data-testid="stFileUploader"] {
            border: 1px dashed rgba(124, 58, 237, 0.3) !important;
            border-radius: var(--radius-md) !important;
            background: rgba(124, 58, 237, 0.04) !important;
            transition: all var(--transition-fast) !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: var(--accent-primary) !important;
            background: rgba(124, 58, 237, 0.08) !important;
        }

        /* ====================================================
           EXPANDER STYLING
           ==================================================== */
        .streamlit-expanderHeader {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text-secondary) !important;
            font-weight: 500 !important;
        }

        /* ====================================================
           DIVIDER / SEPARATOR
           ==================================================== */
        hr {
            border: none !important;
            border-top: 1px solid var(--border-subtle) !important;
            margin: 24px 0 !important;
        }

        /* ====================================================
           WELCOME FEATURE GRID
           ==================================================== */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
            margin-top: 24px;
        }
        .feature-item {
            background: var(--bg-card-glass);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 20px;
            transition: all var(--transition-smooth);
        }
        .feature-item:hover {
            border-color: var(--border-hover);
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
        }
        .feature-item .icon {
            font-size: 1.8rem;
            margin-bottom: 10px;
            display: block;
        }
        .feature-item .title {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 1rem;
            color: var(--text-primary);
            margin-bottom: 6px;
        }
        .feature-item .desc {
            font-size: 0.85rem;
            color: var(--text-secondary);
            line-height: 1.5;
        }

        /* ====================================================
           LOADING SKELETON (for spinner areas)
           ==================================================== */
        @keyframes skeleton-pulse {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 0.8; }
        }
        .skeleton {
            background: linear-gradient(
                90deg,
                var(--bg-card) 25%,
                rgba(124, 58, 237, 0.08) 50%,
                var(--bg-card) 75%
            );
            background-size: 200% 100%;
            animation: skeleton-pulse 1.8s ease infinite;
            border-radius: var(--radius-sm);
            height: 16px;
            margin: 8px 0;
        }

        /* ====================================================
           SECTION HEADER STYLING
           ==================================================== */
        .section-header {
            margin-bottom: 24px;
        }
        .section-header h2 {
            margin-bottom: 4px !important;
        }
        .section-subtitle {
            color: var(--text-muted);
            font-size: 0.9rem;
            line-height: 1.5;
            margin-top: 0;
        }

        /* ====================================================
           SCROLLBAR STYLING
           ==================================================== */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--bg-card);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted);
        }

        /* ====================================================
           RADIO BUTTON OVERRIDES
           ==================================================== */
        .stRadio > div {
            gap: 2px !important;
        }
        .stRadio [data-testid="stMarkdownContainer"] p {
            font-size: 0.9rem !important;
            font-weight: 500 !important;
        }

        /* ====================================================
           METRIC DELTA OVERRIDE (for Streamlit built-in metrics)
           ==================================================== */
        [data-testid="stMetric"] {
            background: var(--bg-card-glass) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            padding: 16px !important;
        }

        /* ====================================================
           SPINNER / TOAST OVERRIDE
           ==================================================== */
        .stSpinner > div {
            border-top-color: var(--accent-primary) !important;
        }

        /* ====================================================
           PLOTLY CHART CONTAINER OVERRIDE
           ==================================================== */
        .stPlotlyChart {
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            overflow: hidden !important;
        }
    </style>
    """
