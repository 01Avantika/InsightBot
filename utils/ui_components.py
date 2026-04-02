"""
utils/ui_components.py — Custom Sidebar and UI Utilities
"""
import streamlit as st

def identity_sidebar(user):
    """
    Renders the custom InsightBot sidebar with a profile section,
    navigation links (increased font size), and logout logic.
    Hides default Streamlit navigation elements.
    """
    
    # ---------------- CSS INJECTION (Hides defaults & Styles custom UI) ----------------
    # This targets the main Streamlit app component structure.
    # It removes default sidebars and stylizes our custom container.
    st.markdown("""
        <style>
            /* 1. HIDE DEFAULT STREAMLIT SIDEBAR ELEMENTS */
            /* This hides the file list on the left */
            [data-testid="stSidebarNav"] {display: none;}
            
            /* 2. STYLE CUSTOM SIDEBAR PANELS */
            /* Customizing the main sidebar container width and background tint */
            [data-testid="stSidebar"] {
                min-width: 280px !important;
                background: linear-gradient(180deg, rgba(124, 58, 237, 0.08), rgba(0,0,0,0));
            }
            
            /* Branding section style */
            .sidebar-branding {
                padding: 1.5rem 1rem;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                margin-bottom: 1.5rem;
            }

            /* INCREASED FONT SIZE FOR NAV LINKS (PageLink components) */
            /* Targeting the specific paragraph element inside the PageLink component */
            [data-testid="stSidebar"] .stPageLink {
                padding: 0.8rem 0.5rem; /* Better vertical spacing */
            }
            [data-testid="stSidebar"] .stPageLink p {
                font-size: 1.1rem !important; /* Larger text */
                font-weight: 600 !important;
            }
            
            /* Hover/Active states for links */
            [data-testid="stSidebar"] .stPageLink:hover {
                background: rgba(124, 58, 237, 0.1) !important;
                border-radius: 8px;
            }

            /* Custom Logout button in sidebar (Red design) */
            div.stButton > button[key="sidebar_logout"] {
                width: 100%;
                margin-top: 3rem;
                background-color: #ef4444 !important; /* Material Red */
                color: white !important;
                border: none !important;
                font-weight: 600 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # 1. NEW BRANDING SECTION: InsightBot
        st.markdown(f"""
            <div class="sidebar-branding">
                <div style="font-size: 1.5rem; font-weight: 800; color: #a78bfa;">🤖 InsightBot</div>
                <div style="color: #64748b; font-size: 0.8rem; margin-top: 2px;">AI-Powered Analytics</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write(" ") # Spacer
        
        # 2. Navigation
        st.markdown("#### Navigation", unsafe_allow_html=True)
        
        # PAGE LINKS: Size increased via CSS in st.markdown above
        # The order matches the requested SaaS structure from image_4.png
        st.page_link("pages/dashboard.py", label="Overview",         icon="📊")
        st.page_link("pages/analyze.py",   label="Analysis Run",     icon="📁")
        st.page_link("pages/chat.py",      label="AI Analysis Chat", icon="💬")
        st.page_link("pages/files.py",     label="All Files",        icon="📂")
        st.page_link("pages/settings.py",  label="Setting",           icon="⚙️")
        st.page_link("pages/history.py",   label="Report History",    icon="📜")
        
        st.divider()
        
        # 3. Custom Logout Button (Styled and Logged)
        if st.button("Logout", key="sidebar_logout", use_container_width=True):
            # Clear all session variables to effectively log out
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            # Redirect to the main entry point (login.py or app.py)
            st.switch_page("app.py")