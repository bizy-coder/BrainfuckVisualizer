import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from itertools import dropwhile, takewhile

class BrainfuckInterpreter:
	def __init__(self, code, input_data, tape_len=30000, max_steps=100000):
		self.code = [c for c in code if c in'><+-.,[]']
		self.input_data = input_data
		self.input_pointer = 0
		self.tape = [0] * tape_len
		self.pointer = 0
		self.instruction_pointer = 0
		self.output = ""
		self.states = []
		self.max_steps = max_steps
		self.save_state()

	def save_state(self):
		self.states.append({
			'tape': self.tape.copy(),
			'pointer': self.pointer,
			'instruction_pointer': self.instruction_pointer,
			'output': self.output,
			'input_pointer': self.input_pointer
		})

	def load_state(self, index):
		state = self.states[index]
		self.tape = state['tape'].copy()
		self.pointer = state['pointer']
		self.instruction_pointer = state['instruction_pointer']
		self.output = state['output']
		self.input_pointer = state['input_pointer']

	def step(self):
		if self.instruction_pointer >= len(self.code) or len(self.states) > self.max_steps:
			return False

		command = self.code[self.instruction_pointer]
		if command == '>':
			self.pointer = (self.pointer + 1) % len(self.tape)
		elif command == '<':
			self.pointer = (self.pointer - 1) % len(self.tape)
		elif command == '+':
			self.tape[self.pointer] = (self.tape[self.pointer] + 1) % 256
		elif command == '-':
			self.tape[self.pointer] = (self.tape[self.pointer] - 1) % 256
		elif command == '.':
			self.output += chr(self.tape[self.pointer])
		elif command == ',':
			if self.input_pointer < len(self.input_data):
				self.tape[self.pointer] = ord(self.input_data[self.input_pointer])
				self.input_pointer += 1
			else:
				self.tape[self.pointer] = 0
		elif command == '[':
			if self.tape[self.pointer] == 0:
				bracket_count = 1
				while bracket_count > 0:
					self.instruction_pointer += 1
					if self.code[self.instruction_pointer] == '[':
						bracket_count += 1
					elif self.code[self.instruction_pointer] == ']':
						bracket_count -= 1
		elif command == ']':
			if self.tape[self.pointer] != 0:
				bracket_count = 1
				while bracket_count > 0:
					self.instruction_pointer -= 1
					if self.code[self.instruction_pointer] == ']':
						bracket_count += 1
					elif self.code[self.instruction_pointer] == '[':
						bracket_count -= 1
		else:
			self.instruction_pointer += 1
			return 1
		self.instruction_pointer += 1
		self.save_state()
		return True

class BrainfuckUI:
	def __init__(self, master):
		self.master = master
		self.master.title("Advanced Brainfuck Interpreter")
		self.master.geometry("800x900")
		self.master.configure(bg='#f0f0f0')
		self.interpreter = None
		self.current_state = 0

		self.create_widgets()

		self.master.bind('<Configure>', self.on_resize)




	def on_resize(self, event=None):
		# Wait a short moment for the resize to complete
		self.master.after(100, self.update_display)

	def create_widgets(self):
		self.notebook = ttk.Notebook(self.master)
		self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

		self.settings_frame = ttk.Frame(self.notebook, padding="10")
		self.results_frame = ttk.Frame(self.notebook, padding="10")

		self.notebook.add(self.settings_frame, text="Settings")
		self.notebook.add(self.results_frame, text="Results")

		self.create_settings_widgets()
		self.create_results_widgets()

	def create_settings_widgets(self):
		# Code input
		ttk.Label(self.settings_frame, text="Code:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
		self.code_entry = scrolledtext.ScrolledText(self.settings_frame, width=70, height=10, font=("Consolas", 10))
		self.code_entry.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

		# Input
		ttk.Label(self.settings_frame, text="Input:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
		self.input_entry = scrolledtext.ScrolledText(self.settings_frame, width=70, height=5, font=("Consolas", 10))
		self.input_entry.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

		# Tape length and Max steps
		ttk.Label(self.settings_frame, text="Tape Length:").grid(row=4, column=0, sticky=tk.W)
		self.tape_len_var = tk.StringVar(value="30000")
		ttk.Entry(self.settings_frame, textvariable=self.tape_len_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=(0, 10))

		ttk.Label(self.settings_frame, text="Max Steps:").grid(row=4, column=1, sticky=tk.E)
		self.max_steps_var = tk.StringVar(value="100000")
		ttk.Entry(self.settings_frame, textvariable=self.max_steps_var, width=10).grid(row=4, column=2, sticky=tk.W)

		# Run button
		self.run_button = ttk.Button(self.settings_frame, text="Run", command=self.run_code)
		self.run_button.grid(row=5, column=0, columnspan=3, pady=10)

		# Configure weights
		for i in range(6):
			self.settings_frame.rowconfigure(i, weight=1)
		for i in range(3):
			self.settings_frame.columnconfigure(i, weight=1)

	def create_results_widgets(self):
		# Tape display
		ttk.Label(self.results_frame, text="Tape:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
		self.tape_display = scrolledtext.ScrolledText(self.results_frame, width=70, height=2, font=("Consolas", 10), state="disabled")
		self.tape_display.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E))
		self.tape_display.tag_configure("emphasis", font=("Consolas", 11, "bold", "underline"))

		# Code display
		ttk.Label(self.results_frame, text="Code Execution:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
		self.code_display = scrolledtext.ScrolledText(self.results_frame, width=70, height=10, font=("Consolas", 10), state="disabled")
		self.code_display.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
		self.code_display.tag_configure("emphasis", font=("Consolas", 11, "bold", "underline"))

		# Input display
		ttk.Label(self.results_frame, text="Input:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
		self.input_display = scrolledtext.ScrolledText(self.results_frame, width=70, height=3, font=("Consolas", 10), state="disabled")
		self.input_display.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
		self.input_display.tag_configure("emphasis", font=("Consolas", 11, "bold", "underline"))

		# Output display
		ttk.Label(self.results_frame, text="Output:").grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
		self.output_display = scrolledtext.ScrolledText(self.results_frame, width=70, height=5, font=("Consolas", 10), state="disabled")
		self.output_display.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E))

		# Navigation controls
		nav_frame = ttk.Frame(self.results_frame)
		nav_frame.grid(row=8, column=0, columnspan=3, pady=10)

		self.prev_button = ttk.Button(nav_frame, text="<", command=self.prev_state, state="disabled")
		self.prev_button.grid(row=0, column=0, padx=5)

		self.state_var = tk.StringVar()
		self.state_label = ttk.Label(nav_frame, textvariable=self.state_var)
		self.state_label.grid(row=0, column=1, padx=5)

		self.next_button = ttk.Button(nav_frame, text=">", command=self.next_state, state="disabled")
		self.next_button.grid(row=0, column=2, padx=5)

		# State slider
		self.state_slider = ttk.Scale(self.results_frame, from_=0, to=0, orient="horizontal", command=self.update_state)
		self.state_slider.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

		# Configure weights
		for i in range(10):
			self.results_frame.rowconfigure(i, weight=1)
		for i in range(3):
			self.results_frame.columnconfigure(i, weight=1)

	def wait_for_widget(self, widget):
		def check_width():
			if widget.winfo_width() > 1:
				return True
			widget.update_idletasks()
			self.master.after(10, check_width)
		check_width()

	def run_code(self):
		code = self.code_entry.get("1.0", tk.END).strip()
		input_data = self.input_entry.get("1.0", tk.END).strip()
		
		try:
			tape_len = int(self.tape_len_var.get())
			max_steps = int(self.max_steps_var.get())
		except ValueError:
			messagebox.showerror("Invalid Input", "Tape length and Max steps must be integers.")
			return

		self.interpreter = BrainfuckInterpreter(code, input_data, tape_len, max_steps)
		self.code = code
		while self.interpreter.step():
			pass

		self.current_state = len(self.interpreter.states) - 1
		self.state_slider.configure(to=self.current_state)
		self.state_slider.set(self.current_state)
		
		# self.update_display()
		
		self.next_button.config(state="normal")
		self.prev_button.config(state="normal")
		
		self.output_display.see(tk.END)
		
		# Switch to Results tab
		self.notebook.select(1)

		self.update_display()
	
	def update_display(self):
		if not hasattr(self, 'interpreter') or not self.interpreter:
			return

		if not self.interpreter or self.current_state >= len(self.interpreter.states):
			return

		state = self.interpreter.states[self.current_state]
		state2 = self.interpreter.states[self.current_state - 1 if self.current_state > 0 else self.current_state]

		self.wait_for_widget(self.tape_display)

		# Update tape display
		visible_tape = state["tape"]
		self.tape_display.config(state="normal")
		self.tape_display.delete("1.0", tk.END)
		tape_width = (self.tape_display.winfo_width() // 30 or 10) + 1  # Approximate number of cells that fit in a line
		for i in range(0, len(visible_tape), tape_width or 10):
			line = visible_tape[i:i + tape_width]
			line_str = " ".join(f"{cell:<3d}" for cell in line)
			self.tape_display.insert(tk.END, line_str + "\n")

		# Remove the last newline
		self.tape_display.delete("end-1c", tk.END)

		# Highlight the current cell
		current_cell_index = state['pointer']
		row = current_cell_index // tape_width + 1
		col = (current_cell_index % tape_width) * 4
		self.tape_display.tag_add("emphasis", f"{row}.{col}", f"{row}.{col + 3}")
		self.tape_display.see(f"{row}.{col}")
		self.tape_display.config(state="disabled")

		# Update code display
		code_str = self.code
		self.code_display.config(state="normal")
		self.code_display.delete("1.0", tk.END)
		self.code_display.insert(tk.END, code_str)

		# Find the position of the current instruction
		bf_chars = "><+-.,[]"
		char_count = 0
		for i, char in enumerate(code_str):
			if char in bf_chars:
				if char_count == state2['instruction_pointer']:
					start = self.code_display.index(f"1.0 + {i} chars")
					end = self.code_display.index(f"{start} + 1 chars")
					self.code_display.tag_add("emphasis", start, end)
					self.code_display.see(start)
					break
				char_count += 1

		self.code_display.config(state="disabled")

		# Update input display
		input_str = self.interpreter.input_data
		self.input_display.config(state="normal")
		self.input_display.delete("1.0", tk.END)
		self.input_display.insert(tk.END, input_str)
		self.input_display.tag_remove("emphasis", "1.0", tk.END)

		start = self.input_display.index(f"1.0 + {state['input_pointer']} chars")
		end = self.input_display.index(f"{start} + 1 chars")
		self.input_display.tag_add("emphasis", start, end)
		self.input_display.see(start)
		self.input_display.config(state="disabled")

		# Update output display
		self.output_display.config(state="normal")
		self.output_display.delete("1.0", tk.END)
		self.output_display.insert(tk.END, state["output"])
		self.output_display.see(tk.END)
		self.output_display.config(state="disabled")

		# Update state label
		self.state_var.set(f"State: {self.current_state + 1}/{len(self.interpreter.states)}")

	def prev_state(self):
		if self.current_state > 0:
			self.current_state -= 1
			self.state_slider.set(self.current_state)
			self.update_display()

	def next_state(self):
		if self.current_state < len(self.interpreter.states) - 1:
			self.current_state += 1
			self.state_slider.set(self.current_state)
			self.update_display()

	def update_state(self, value):
		self.current_state = int(float(value))
		self.update_display()

if __name__ == "__main__":
	root = tk.Tk()
	app = BrainfuckUI(root)
	root.mainloop()