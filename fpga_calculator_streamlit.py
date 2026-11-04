import streamlit as st
import struct
import time
import math
import numpy as np
from dataclasses import dataclass
from typing import List, Literal
from calculator_top import compute_evaluation_step

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
    <div style="text-align: center;">
        <span style="
            display: inline-block; 
            border: 0px solid #ffffff; 
            border-radius: 0px; 
            padding: 0px 5px; 
            font-size: 12px; 
            background-color: #e0f2fe;
        ">
            FPGA Style Calculator
        </span>
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown(
	"""
	<style>
	/* 1. FORCE THE FULL OUTER PAGE BACKGROUND (Warm Cream/Yellow) */
	[data-testid="stAppViewContainer"] {
		background-color: #fef3c7 !important;
	}

	/* 2. STYLE THE MAIN APP CONTAINER AS A CENTERED CARD (Light Blue) */
/*	[data-testid="stMainBlockContainer"] {
		background-color: #e0f2fe !important;
		border: 2px solid #bae6fd !important;
		padding: 40px !important;
		border-radius: 16px !important;
		box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.05);
		max-width: 550px !important;
		margin: 200px auto !important;
		max-height: 500px;
	}
*/
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

st.markdown(
	"""
	<style>
		<meta name="description" content="An online arbitrary-precision calculator for FPGA engineers. Supports IEEE 754 floating-point, signed two's complement binary, and custom fixed-point binary math.">
		<meta name="keywords" content="FPGA calculator, programmer's calculator, IEEE 754 converter, two's complement calculator, fixed point binary point">
		<meta name="author" content="bldillahunt">

		<!-- Open Graph tags to look good when linked on Reddit, Discord, or GitHub -->
		<meta property="og:title" content="FPGA & Programmer's Calculator (Desktop Version)">
		<meta property="og:description" content="Arbitrary-precision binary math, IEEE 754 precision, and signed two's complement calculations.">
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
		('Reset', 'Enter', 'Help')
	]

	button_value = None
	button_pressed = False

	# Build rows horizontally inside the centered container tracking layout
	for row in buttons:
		cols = st.columns(3) 
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

if (button_push_result in ('Reset', 'Enter', "Help")) or keyboard_enter_pressed or button_pressed:
 
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
	elif (button_push_result == "Help"):
		# Format box using code block style
		st.code("Format:\n<operand1><operator><operand2>\nor\n<operand1>\nor<operator><operand1>")

		# Bullet points instructions
		st.markdown("""
		* **Inputs:** Supports Real, Hex, Bin, FP32, and FP64.
		* **Binary:** Entered in 2's complement with a binary point (no 0b).
		* **Operations:** Select math (+,-,*,/,%) or unary logic (&,|,^,~,!).
		""")

		# Close button built directly into the pop-up frame
		if st.button("Close", use_container_width=True):
			st.rerun()
	else:
		# Append typed keys to your main input tracker
		st.session_state.main_display_var += str(button_push_result)
#        st.rerun()
