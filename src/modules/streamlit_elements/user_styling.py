import streamlit as st


def hide_sidebar():
    no_sidebar_style = """
        <style>
            div[data-testid="stSidebarNav"] {display: none;}
        </style>
    """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)


def multiselect_overflow():
    multiselect_overflow_style = """
        <style>
            div[data-baseweb="select"] > div {
                max-height: 200px;
                overflow: auto;
            }
        </style>
    """
    st.markdown(multiselect_overflow_style, unsafe_allow_html=True)


def user_styling():
    hide_sidebar()
    multiselect_overflow()
