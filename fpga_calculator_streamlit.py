import streamlit as st
import struct
import time
import math
import numpy as np
from dataclasses import dataclass
from typing import List, Literal
from binary_support import precision_profile, lookup_table, twos_complement, binary_string_to_int_list, int_list_to_binary_string, binary_point_removal, twos_complement_bin_rational, list_to_string, remove_msbs, binary_point_alignment
from binary_conversions import real_to_twos_comp_binary, hexadecimal_to_binary, ieee754_hex_to_binary, binary_to_real, binary_to_hexadecimal, binary_to_ieee754
from binary_math import binary_division, binary_multiplier, binary_adder, binary_subtraction

# --- Page Configuration ---
# 1. Page Settings
st.set_page_config(page_title="", layout="centered")
st.write("This calculator can perform data type conversions and it can perform basic math operations on five different data types.  Select the input type, the output type, the number of integer bits and the number of fraction bits. The number of integer bits and the number of fraction bits are needed for division and for hexadecimal values.  There is no need for prefixes such as 0x or 0b.  The input box will accept data in the form of: <operand1><operator><operand2> or <operand1>")

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

	/* --- NUMPAD RIGID LAYOUT OVERRIDES --- */
	.numpad-wrapper {
		max-width: 280px;
		margin: 0 auto; /* Centers the matrix block on desktop and mobile layout */
		text-align: center;
	}
	.numpad-table {
		width: 100%;
		border-collapse: separate;
		border-spacing: 5px; /* Adjusts gap space symmetrically between keys */
	}
	/* Ensures Streamlit internal button targets scale inside table grid fields */
	.numpad-table div.stButton > button {
		width: 100% !important;
		padding: 8px 0 !important;
	}
	</style>
	""",
	unsafe_allow_html=True
)

button_pressed = None

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

	show_numpad = st.checkbox("Show Mobile Number Pad")
	
	if show_numpad:
		# Use standard HTML tables to build the 4-column matrix layout safely
		st.markdown('<div class="numpad-wrapper"><h3>Number Pad</h3><table class="numpad-table">', unsafe_allow_html=True)
		
		buttons_matrix = [
			('7', '8', '9', '/'),
			('4', '5', '6', '*'),
			('1', '2', '3', '-'),
			('0', '.', 'R', '+'),
			('A', 'B', 'C', 'D'),
			('E', 'F', 'Enter', '=')
		]

		for row_idx, row in enumerate(buttons_matrix):
			st.markdown('<tr>', unsafe_allow_html=True)
			for col_idx, val in enumerate(row):
				st.markdown('<td>', unsafe_allow_html=True)
				if st.button(val, key=f"btn_{val}_{row_idx}_{col_idx}"):
					button_pressed = val
				st.markdown('</td>', unsafe_allow_html=True)
			st.markdown('</tr>', unsafe_allow_html=True)
			
		st.markdown('</table></div>', unsafe_allow_html=True)
	else:
		# Balanced 2-column wide control buttons layout
		st.markdown('<div class="numpad-wrapper"><table class="numpad-table"><tr><td>', unsafe_allow_html=True)
		if st.button("Reset", key="btn_Reset_default"):
			button_pressed = "Reset"
		st.markdown('</td><td>', unsafe_allow_html=True)
		if st.button("Enter", key="btn_Enter_default"):
			button_pressed = "Enter"
		st.markdown('</td></tr></table></div>', unsafe_allow_html=True)

keyboard_enter_pressed = False

if typed_input != st.session_state.main_display_var:
	st.session_state.main_display_var = typed_input
	keyboard_enter_pressed = True

def verify_real_input(input_string):
	try:
		float(input_string)
		return False
	except ValueError:
		return True

def verify_hex_input(input_string):
	try:
		int(input_string, 16)

		if (len(input_string) > (int_bits + frac_bits)/4):
			return True

		return False
	except ValueError:
		return True

def verify_bin_input(input_string):
	try:
		int(input_string.replace('.', ''), 2) # Enforces 0s and 1s only
		return ((input_string.count('.') > 1) or ((input_string[0] != '0') and (input_string[0] != '1')) or (input_string[-1] == '.'))
	except ValueError:
		return True

def is_valid_hex(s):
	"""Returns True if valid hex, False if invalid."""
	try:
		int(s, 16)
		return True
	except ValueError:
		return False	

def verify_fp32_input(input_string):
	return len(input_string) != 8 or not is_valid_hex(input_string)

def verify_fp64_input(input_string):
	return len(input_string) != 16 or not is_valid_hex(input_string)

def verify_operator(input_string):
	return input_string not in "+-*/"

def convert_to_binary(operand):
	if (input_mode[1] == "REAL"):
		n_binary_string = real_to_twos_comp_binary(operand, int_bits, frac_bits)
		n_int_list = binary_string_to_int_list(n_binary_string)
	elif (input_mode[1] == "HEX"):
		n_binary_string = hexadecimal_to_binary(operand, int_bits, frac_bits, lookup_table)
		n_int_list = binary_string_to_int_list(n_binary_string)
	elif (input_mode[1] == "FP32"):
		current_profile = precision_profile["SINGLE"]
		p = current_profile
		n_binary_string = ieee754_hex_to_binary(operand, p, lookup_table)
		n_int_list = n_binary_string
	elif (input_mode[1] == "FP64"):
		current_profile = precision_profile["DOUBLE"]
		p = current_profile
		n_binary_string = ieee754_hex_to_binary(operand, p, lookup_table)
		n_int_list = n_binary_string
	else: 
		n_int_list = binary_string_to_int_list(operand)

	return n_int_list

def binary_math_operation(operand1, operand2, operator):
	if (operator == "/"):
		if (output_mode[1] == "FP32"):
			current_profile = precision_profile["SINGLE"]
			p = current_profile

			if (1 + p.exponent_size + p.mantissa_size) < (int_bits + frac_bits):
				max_size = int_bits + frac_bits
			else:
				max_size = 64
		elif (output_mode[1] == "FP64"):
			current_profile = precision_profile["DOUBLE"]
			p = current_profile

			if (1 + p.exponent_size + p.mantissa_size) < (int_bits + frac_bits):
				max_size = int_bits + frac_bits
			else:
				max_size = 128
		else:
			max_size = int_bits + frac_bits

		operand1_no_bin_point, operand2_no_bin_point, operand1_fraction_size, operand2_fraction_size = binary_point_alignment(operand1, operand2, False)

		if (operand1[0] == 1):
			operand1_2s_comp, op1_carry = twos_complement(operand1_no_bin_point)
			sign_operand1 = 1
		else:
			operand1_2s_comp = operand1_no_bin_point
			sign_operand1 = 0

		if (operand2[0] == 1):
			operand2_2s_comp, op2_carry = twos_complement(operand2_no_bin_point)
			sign_operand2 = 1
		else:
			operand2_2s_comp = operand2_no_bin_point
			sign_operand2 = 0

		quotient = binary_division(operand1_2s_comp, operand2_2s_comp, max_size)

		if ((sign_operand1 ^ sign_operand2) == 1):
			quotient_size = len(quotient)

			if ('.' in quotient):
				quotient_radix_index = quotient.index('.')
				quotient.pop(quotient_radix_index)
			else:
				quotient_radix_index = quotient_size

			if (quotient_radix_index < quotient_size):
				quotient_fraction_size = quotient_size - (quotient_radix_index + 1)
			else:
				quotient_fraction_size = 0

			quotient_no_bin_point = quotient
			quotient_2s_comp, carry_quotient = twos_complement(quotient_no_bin_point)

			quotient_2s_comp_bin_point = quotient_2s_comp[:quotient_size - quotient_fraction_size - 1] + ['.'] + quotient_2s_comp[quotient_size - quotient_fraction_size - 1:]

			math_result_2s_comp = quotient_2s_comp_bin_point
		else:
			math_result_2s_comp = quotient
		math_result = math_result_2s_comp
	elif (operator == "*"):
		math_result = binary_multiplier(operand1, operand2)
	elif (operator == "+"):
		addend_a, addend_b, operand1_fraction_size, operand2_fraction_size = binary_point_alignment(operand1, operand2, False)

		if (operand1_fraction_size > operand2_fraction_size):
			fraction_size = operand1_fraction_size
		else:
			fraction_size = operand2_fraction_size

		n_sum, n_carry = binary_adder(addend_a, addend_b)

		if ((operand1[0] == 0) and (operand2[0] == 0) and (n_sum[0] == 1)) or ((operand1[0] == 1) and (operand2[0] == 1) and (n_sum[0] == 0)):
			sum_result = [n_carry] + n_sum
		else:
			sum_result = n_sum

		binary_point_index = len(sum_result) - fraction_size

		math_result = sum_result[:binary_point_index] + ['.'] + sum_result[binary_point_index:]
	elif (operator == "-"):
		math_result = binary_subtraction(operand1, operand2)

	return math_result

def convert_from_binary(operand):
	if (output_mode[1] == "REAL"):
		conversion_result = binary_to_real(operand)
	elif (output_mode[1] == "HEX"):
		conversion_result = binary_to_hexadecimal(operand, lookup_table)
	elif (output_mode[1] == "FP32"):
		conversion_result = binary_to_ieee754(operand, precision_profile["SINGLE"], lookup_table)
	elif (output_mode[1] == "FP64"):
		conversion_result = binary_to_ieee754(operand, precision_profile["DOUBLE"], lookup_table)
	else:
		operand_int_list = int_list_to_binary_string(operand, len(operand))
		conversion_result = "".join(operand_int_list)
	return conversion_result                                                                                                                  

def input_mode_changed():
	mode = input_mode[1]

	if mode == "HEX":
		dialog = tk.Toplevel(root)
		dialog.title("Hexadecimal Options")
		dialog.geometry("400x175")

		ttk.Label(
			dialog,
			text=f"HEX input OPTIONS",
			font=("Arial", 10, "bold")
		).pack(pady=10)

		ttk.Label(
			dialog,
			text="Set the number of integer bits and the number of fraction bits and allow enough room for the sign bit. No need for '0x' or for '.'. Sign extension will be done automatically if not enough nibbles are entered and it will be based on the most signficant nibble",
			wraplength = 350,
			justify = "left"
		).pack(padx=10, pady=10)

		dialog.after(10000, dialog.destroy)

def output_mode_changed():
	mode = output_mode[1]

	if mode == "HEX":
		dialog = tk.Toplevel(root)
		dialog.title("Hexadecimal Options")
		dialog.geometry("400x175")

		ttk.Label(
			dialog,
			text=f"HEX output OPTIONS",
			font=("Arial", 10, "bold")
		).pack(pady=10)

		ttk.Label(
			dialog,
			text="The number of bits in the output will be equal to 'Integer bits' + 'Fraction_bits' if the input is 'BIN' or 'HEX'. The value will have no hexadecimal point and it will be scaled by the number of fractional bits.",
			wraplength = 350,
			justify = "left"
		).pack(padx=10, pady=10)

		dialog.after(10000, dialog.destroy)

def parse_input_string(input_string):
	# No regex options would work here, so this is a brute force state machine
	state = 'Empty_String_Check'
	data_length = len(input_string)
	input_index = 0
	left = ""
	op = ""
	right = ""
	operand1_present = False
	operator_present = False
	operand2_present = False

	while (True):
		match state:
			case 'Empty_String_Check':
				if not input_string:
					return left, op, right
				else:
					state = 'First_Character'
			case 'First_Character':
				if (input_string[input_index] == '+'):
					state = 'First_Operand'
				elif (input_string[input_index] == '-') or (input_string[input_index].isalnum()):
					left += input_string[input_index]

					if (len(input_string) > 1):
						input_index = input_index + 1
						state = 'First_Operand'
					else:
						return left, op, right
				else:
					return left, op, right
			case 'First_Operand':
				while input_string[input_index] not in ("+", "-", "*", "/", ""):
					left += input_string[input_index]

					if (input_index < data_length-1):
						input_index = input_index + 1
					else:
						operand1_present = True
						return left, op, right
				else:
					operand1_present = True
					operator_present = True
					op = input_string[input_index]
					input_index = input_index + 1

				if (input_index < len(input_string)):
					if (input_string[input_index] not in ("")):
						state = 'Second_Operand'
					else:
						operand2_present = False
						return left, op, right
				else:
					operand2_present = False
					return left, op, right
			case 'Second_Operand':
				while input_string[input_index] not in (""):
					right += input_string[input_index]

					if (input_index < data_length-1):
						input_index = input_index + 1
					else:
						operand2_present = True
						return left, op, right

				operand2_present = True
				return left, op, right

def get_operands():
	raw_input = st.session_state.main_display_var
	operand1, operator, operand2 = parse_input_string(raw_input)
	return operand1, operand2, operator

# Process Button Actions
button_push_result = None

if typed_input != st.session_state.main_display_var:
	st.session_state.main_display_var = typed_input
	keyboard_enter_pressed = True

# Explicitly link your button press assignment here
button_push_result = button_pressed 

if button_push_result or keyboard_enter_pressed:
 
	if keyboard_enter_pressed and not button_push_result:
		button_push_result = 'Enter'

	# The 'R' routing logic now triggers cleanly because button_push_result is captured
	# The 'Reset' routing logic triggers cleanly without causing a framework crash
	if (button_push_result == 'Reset') or (button_push_result == 'R'):
		st.session_state.main_display_var = ""
		st.session_state.aux_display_var = ""
		
		# THE FIX: Bump the counter to force Streamlit to wipe the text field clean
		st.session_state.input_widget_counter += 1
		st.rerun()
		
	elif button_push_result in ('Enter'):
		# Parse inputs
		operand1, operand2, operator = get_operands()
		
		operand1_data_error = False
		operand2_data_error = False
		operator_error = False
		
		nibble_size = int_bits // 4
		operand2_present = True if operand2 != "" else False
		
		# Validation Pipeline based on Input Format
		if input_mode[1] == "REAL":
			operand1_data_error = verify_real_input(operand1)
			if operand2_present:
				operand2_data_error = verify_real_input(operand2)
				
		elif input_mode[1] == "HEX":
			if (len(operand1) < nibble_size) and (len(operand1) > 0):
				if any(item in operand1[0] for item in HEX_NEGATIVE_LIST):
					operand1 = operand1.rjust(nibble_size, "F")
				else:
					operand1 = operand1.rjust(nibble_size, "0")
			operand1_data_error = verify_hex_input(operand1)
			
			if operand2_present:
				if (len(operand2) < nibble_size) and (len(operand2) > 0):
					if any(item in operand2[0] for item in HEX_NEGATIVE_LIST):
						operand2 = operand2.rjust(nibble_size, "F")
					else:
						operand2 = operand2.rjust(nibble_size, "0")
				operand2_data_error = verify_hex_input(operand2)
				
		elif input_mode[1] == "BIN":
			operand1_data_error = verify_bin_input(operand1)
			if operand2_present:
				operand2_data_error = verify_bin_input(operand2)
				
		elif input_mode[1] == "FP32":
			exponent_size, mantissa_size = 8, 23
			operand1_data_error = verify_fp32_input(operand1)
			if operand2_present:
				operand2_data_error = verify_fp32_input(operand2)
				
		elif input_mode[1] == "FP64":
			exponent_size, mantissa_size = 11, 52
			operand1_data_error = verify_fp64_input(operand1)
			if operand2_present:
				operand2_data_error = verify_fp64_input(operand2)

		operator_error = verify_operator(operator)
		
		# Core Math Execution
		if not operand1_data_error and not operand2_data_error and not operator_error:
			operand1_binary = convert_to_binary(operand1)
			
			if operand2_present:
				operand2_binary = convert_to_binary(operand2)
				binary_result = binary_math_operation(operand1_binary, operand2_binary, operator)
				calculator_result = convert_from_binary(binary_result)
			else:
				calculator_result = convert_from_binary(operand1_binary)
			
			st.session_state.aux_display_var = str(calculator_result)
			st.rerun()
		else:
			st.session_state.main_display_var = ""
			if "input_win" in st.session_state:
				st.session_state.input_win = ""
			st.session_state.aux_display_var = "ERROR"
			st.rerun()
	else:
		# Append typed keys to your main input tracker
		st.session_state.main_display_var += str(button_push_result)
		st.rerun()