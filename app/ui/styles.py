"""Premium SaaS UI styles and custom CSS definitions for Streamlit."""


def get_custom_css() -> str:
    """Returns the custom CSS string for dark mode and glassmorphism styling."""
    return """
    <style>
        /* Import Premium Typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');

        /* Global Theme Overrides */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #090D16 !important;
            font-family: 'Inter', sans-serif !important;
            color: #E2E8F0 !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: rgba(13, 17, 23, 0.85) !important;
            backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
        [data-testid="stSidebar"] * {
            font-family: 'Outfit', sans-serif !important;
        }

        /* Custom Headers */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            color: #F8FAFC !important;
            letter-spacing: -0.02em !important;
        }

        /* Title style with subtle gradient */
        .app-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #FFFFFF 0%, #94A3B8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 25px;
        }

        /* Glassmorphism Card Wrapper */
        .glass-card {
            background: rgba(17, 25, 40, 0.6) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 16px !important;
            padding: 24px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .glass-card:hover {
            transform: translateY(-2px) !important;
            border-color: rgba(59, 130, 246, 0.2) !important;
            box-shadow: 0 12px 40px 0 rgba(59, 130, 246, 0.1) !important;
        }

        /* Custom KPI Card Styling */
        .kpi-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 10px;
        }
        .kpi-val {
            font-size: 2.2rem;
            font-weight: 700;
            color: #3B82F6;
            font-family: 'Outfit', sans-serif;
            margin: 5px 0;
            text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
        }
        .kpi-lbl {
            font-size: 0.8rem;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 500;
        }

        /* Custom Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-family: 'Outfit', sans-serif !important;
            padding: 8px 24px !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button:hover {
            transform: scale(1.02) !important;
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.4) !important;
        }

        /* Chat Message Styling */
        .chat-msg-user {
            background: rgba(37, 99, 235, 0.15) !important;
            border: 1px solid rgba(37, 99, 235, 0.2) !important;
            border-radius: 12px 12px 0 12px !important;
            padding: 12px 16px !important;
            margin: 10px 0 !important;
            align-self: flex-end;
        }
        .chat-msg-assistant {
            background: rgba(30, 41, 59, 0.5) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px 12px 12px 0 !important;
            padding: 12px 16px !important;
            margin: 10px 0 !important;
        }

        /* Interactive table/dataframes styling */
        [data-testid="stTable"], [data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }
    </style>
    """
