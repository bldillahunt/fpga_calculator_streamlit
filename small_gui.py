import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="FPGA Developer Calculator", layout="centered")

# 2. Compact Desktop GUI CSS Overrides
st.markdown(
    """
    <style>
    /* Shrink overall page padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 550px !important; /* Forces the app to look like a desktop app window */
    }
    
    /* Minimize massive vertical gaps between widgets */
    [data-testid="stVerticalBlock"] {
        gap: 0.4rem !important;
    }
    
    /* Make input text fields tightly packed */
    div[data-testid="stTextInput"] {
        margin-bottom: 0px !important;
    }
    
    /* Tighten button paddings and make them uniformly sized like a keypad */
    div.stButton > button {
        width: 100% !important;
        padding-top: 0.3rem !important;
        padding-bottom: 0.3rem !important;
        margin: 0px !important;
        border-radius: 4px !important;
    }
    
    /* Make radio button lists more compact */
    div[data-testid="stRadio"] > div{
        gap: 0.2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("?? FPGA Developer Calculator")

# --- 1. INPUT WINDOW ---
user_input = st.text_input("Input Window", label_visibility="visible", placeholder="")

# --- 2. BIT DEFAULTS BOX ---
with st.container(border=True):
    st.caption("**Binary Division and Hexadecimal Output Defaults**")
    bit_col1, bit_col2 = st.columns(2)
    with bit_col1:
        st.number_input("Integer Bits:", min_value=0, value=16, step=1)
    with bit_col2:
        st.number_input("Fraction Bits:", min_value=0, value=16, step=1)

# --- 3. OUTPUT WINDOW ---
# We use an empty placeholder so lower button triggers can instantly push values up here
output_placeholder = st.empty()
with output_placeholder.container():
    st.text_input("Output Window", value="", disabled=True, key="output_win")

# --- 4. FORMAT SELECTION COLS ---
fmt_col1, fmt_col2 = st.columns(2)

formats = ["Real", "Hex", "2's Comp Bin", "IEEE-754 Single", "IEEE-754 Double"]

with fmt_col1:
    with st.container(border=True):
        st.radio("**Input Format**", options=formats, index=0, key="in_fmt")

with fmt_col2:
    with st.container(border=True):
        st.radio("**Output Format**", options=formats, index=0, key="out_fmt")

st.write("") # Tiny spacer before keypad

# --- 5. CALCULATOR KEYPAD GRID ---
# Row 1
k1, k2, k3, k4 = st.columns(4)
k1.button("7")
k2.button("8")
k3.button("9")
k4.button("/")

# Row 2
k5, k6, k7, k8 = st.columns(4)
k5.button("4")
k6.button("5")
k7.button("6")
k8.button("*")

# Row 3
k9, k10, k11, k12 = st.columns(4)
k9.button("1")
k10.button("2")
k11.button("3")
k12.button("-")

# Row 4
k13, k14, k15, k16 = st.columns(4)
k13.button("0")
k14.button(".")
k15.button("R")
k16.button("+")

# Row 5
k17, k18, k19, k20 = st.columns(4)
k17.button("A")
k18.button("B")
k19.button("C")
k20.button("D")

# Row 6
k21, k22, k23, k24 = st.columns(4)
k21.button("E")
k22.button("F")
k23.button("Enter", type="primary") # highlighted action button
k24.button("=")
