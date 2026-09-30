import streamlit as st
import struct
import time
import math
import numpy as np
from dataclasses import dataclass
from typing import List, Literal
from binary_support import precision_profile, lookup_table, twos_complement, binary_string_to_int_list, int_list_to_binary_string, binary_point_removal, twos_complement_bin_rational, list_to_string, remove_msbs, binary_point_alignment
from binary_conversions import real_to_twos_comp_binary, hexadecimal_to_binary, ieee754_hex_to_binary, binary_to_real, binary_to_hexadecimal, binary_to_ieee754
from binary_math import binary_division, binary_multiplier, binary_adder, binary_subtraction, binary_modulo, binary_twos_complement
from binary_logic import binary_and, binary_or, binary_xor, binary_not
from calculator_top import compute_evaluation_step

# --- Page Configuration ---
# 1. Page Settings
st.set_page_config(page_title="", layout="centered")
st.write("This calculator handles basic math, data type conversions, and logic operations (logic limited to hex and bin) across five data types. Operating entirely in binary, it delivers nearly infinite precision. Division and hexadecimal values require specifying the number of integer and fraction bits. Prefixes like 0x or 0b are unnecessary. The input box accepts formats like <operand1><operator><operand2> or <operand1>, using operators: +, -, *, /, %, &, |, ^, ~ (invert), or ! (2's comp)")

# Initialize display tracking variables
if "display" not in st.session_state:
	st.session_state.display = ""

# Initialize display tracking variables
if "display" not in st.session_state:
	st.session_state.display = ""
	
# THE FIX: Track widget versions to force-clear text fields
if "input_widget_counter" not in st.session_state:
	st.session_state.input_widget_counter = 0

st.markdown(
	"""
	<style>
	/* Reduces vertical padding between all block containers */
	[data-testid="stVerticalBlock"] {
		gap: 0.5rem !important;
	}
	</style>
	""",
	unsafe_allow_html=True
)

# --- Initialize Session State for Variables ---
# This mimics Tkinter's instance variables (xxx) across app reruns
if "main_display_var" not in st.session_state:
	st.session_state.main_display_var = ""
if "aux_display_var" not in st.session_state:
	st.session_state.aux_display_var = ""

# --- Constants & Helper Arrays ---
HEX_NEGATIVE_LIST = ["8", "9", "A", "B", "C", "D", "E", "F", "a", "b", "c", "d", "e", "f"]
MAX_FLOAT_SINGLE = 3.4028234663852886e+38
MAX_FLOAT_DOUBLE = 1.7976931348623157e+308
MODES = [
	("Real", "REAL"), 
	("Hex", "HEX"), 
	("2's Comp Bin", "BIN"), 
	("IEEE-754 Single", "FP32"), 
	("IEEE-754 Double", "FP64")
]

# ---------------------------------------------------------
# Placeholder Dummy Methods for Logic (Replace with yours)
# ---------------------------------------------------------

# ---------------------------------------------------------
# 1. Main & Secondary Displays
# ---------------------------------------------------------
# We use st.text_input to act as display entries
# 3. Displays
# Track whether the user presses Enter on their physical keyboard inside the text field
# --- Complete Layout & Color Isolation Styling ---
st.markdown(
	"""
	<style>
	/* 1. FORCE THE FULL OUTER PAGE BACKGROUND (Warm Cream/Yellow) */
	[data-testid="stAppViewContainer"] {
		background-color: #fef3c7 !important;
	}

	/* 2. STYLE THE MAIN APP CONTAINER AS A CENTERED CARD (Light Blue) */
	[data-testid="stMainBlockContainer"] {
		background-color: #e0f2fe !important;
		border: 2px solid #bae6fd !important;
		padding: 40px !important;
		border-radius: 16px !important;
		box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.05);
		max-width: 550px !important;
		margin: 40px auto !important;
	}

	/* Clean up internal component spacing and match container background */
	[data-testid="stVerticalBlock"], 
	[data-testid="stVerticalBlockBorderWrapper"],
	[data-testid="stVComponentBlock"] div {
		background-color: #e0f2fe !important;
		gap: 0.6rem !important;
	}

	/* 3. TIGHTEN THE OUTPUT WINDOW (st.code text box) */
	.stCodeBlock, .stCodeBlock pre {
		margin-bottom: 0px !important;
		padding: 4px 10px !important;
		background-color: #ffffff !important;
		border-radius: 6px !important;
	}
	
	.stCodeBlock code {
		font-family: monospace !important;
		font-size: 1.1rem !important;
	}
	</style>
	""",
	unsafe_allow_html=True
)

# Detect if the value inside the input window changed (user typed/pasted and hit Enter)
with st.container(border=True):
	label_col1, widget_col1 = st.columns([1, 4], vertical_alignment="center")

	with label_col1:
		st.write("Input ")

	with widget_col1:
		typed_input = st.text_input(
			"xxx", 
			value=st.session_state.main_display_var, 
			key=f"input_win_{st.session_state.input_widget_counter}",
			label_visibility="collapsed"
		)

	label_col2, widget_col2 = st.columns([1, 4], vertical_alignment="center")

	with label_col2:
		st.write("Output ")

	with widget_col2:
		st.code(st.session_state.aux_display_var, language="text")		

	# ---------------------------------------------------------
	# 2. Configuration Panel (Bit Widths)
	# ---------------------------------------------------------
	col1, col2 = st.columns(2)
	with col1:
		int_bits = int(st.text_input("Integer Bits:", value=16))
	with col2:
		frac_bits = int(st.text_input("Fraction Bits:", value=16))

	# ---------------------------------------------------------
	# 3. Format Selectors
	# ---------------------------------------------------------
	f_col1, f_col2 = st.columns(2)

	with f_col1:
		st.caption("Input Format")
		input_mode = st.radio(
			"In Mode", 
			options=MODES, 
			format_func=lambda x: x[0],  
			label_visibility="collapsed"
		)

	with f_col2:
		st.caption("Output Format")
		output_mode = st.radio(
			"Out Mode", 
			options=MODES, 
			format_func=lambda x: x[0],  
			label_visibility="collapsed"
		)

	buttons = [
		('Reset', 'Enter')
	]

	button_value = None
	button_pressed = False

	# Build rows horizontally inside the centered container tracking layout
	for row in buttons:
		cols = st.columns(2) 
		for i, val in enumerate(row):
			with cols[i]:
				if st.button(val, key=f"btn_{val}_{i}", use_container_width=True):
					button_value = val
					button_pressed = True

keyboard_enter_pressed = False

if typed_input != st.session_state.main_display_var:
	st.session_state.main_display_var = typed_input
	keyboard_enter_pressed = True

# Process Button Actions
button_push_result = None

if typed_input != st.session_state.main_display_var:
	st.session_state.main_display_var = typed_input
	keyboard_enter_pressed = True

# Explicitly link your button press assignment here
button_push_result = button_value 

if (button_push_result in ('Reset', 'Enter')) or keyboard_enter_pressed or button_pressed:
 
	if keyboard_enter_pressed and not button_push_result:
		button_push_result = 'Enter'

	# The 'R' routing logic now triggers cleanly because button_push_result is captured
	# The 'Reset' routing logic triggers cleanly without causing a framework crash
	if button_push_result == 'Reset' or button_push_result == 'R':
		st.session_state.main_display_var = ""
		st.session_state.aux_display_var = ""
		
		# THE FIX: Bump the counter to force Streamlit to wipe the text field clean
		st.session_state.input_widget_counter += 1
		st.rerun()
	elif button_push_result in ('Enter'):
		main_display_value, calculator_result = compute_evaluation_step(st.session_state.main_display_var, input_mode[1], output_mode[1], int_bits, frac_bits, False)
		st.session_state.main_display_var = main_display_value
		st.session_state.aux_display_var = calculator_result
		st.rerun()
	else:
		# Append typed keys to your main input tracker
		st.session_state.main_display_var += str(button_push_result)
#        st.rerun()