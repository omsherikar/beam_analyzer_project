import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from fpdf import FPDF
from datetime import datetime
import tempfile
from geneticalgorithm import geneticalgorithm as ga

class BeamAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Beam Analysis Tool with AI Optimization")
        self.root.geometry("1000x750")
        self.root.minsize(800, 650)
      
        self.current_data = None
        self.figure = plt.figure(figsize=(8, 6))
    
        self.create_material_database()
        self.create_section_database()
        self.create_widgets()
        self.setup_layout()
        self.setup_menu()
        
    
        self.update_ui_state()

    def create_material_database(self):
        """Initialize the material properties database"""
        self.materials = {
            'A36 Steel': {
                'E': 200e9,          # Young's modulus (Pa)
                'σ_yield': 250e6,    # Yield strength (Pa)
                'color': '#FF6B6B',   # Display color
                'safety_factor': 1.5, # Recommended safety factor
                'cost': 0.5           # Cost ($/kg)
            },
            'Aluminum 6061': {
                'E': 68.9e9,
                'σ_yield': 276e6,
                'color': '#4ECDC4',
                'safety_factor': 1.8,
                'cost': 2.0
            },
            'Concrete': {
                'E': 30e9,
                'σ_yield': 30e6,
                'color': '#C5CBE3',
                'safety_factor': 2.0,
                'cost': 0.1
            }
        }

    def create_section_database(self):
        """Initialize the cross-section database with calculation methods"""
        self.sections = {
            'Rectangular': {
                'function': self.calc_rectangular_section,
                'params': [
                    {'name': 'Width', 'unit': 'mm', 'default': '100'},
                    {'name': 'Height', 'unit': 'mm', 'default': '200'}
                ]
            },
            'I-beam': {
                'function': self.calc_I_section,
                'params': [
                    {'name': 'Width', 'unit': 'mm', 'default': '150'},
                    {'name': 'Height', 'unit': 'mm', 'default': '300'},
                    {'name': 'Flange Thickness', 'unit': 'mm', 'default': '15'},
                    {'name': 'Web Thickness', 'unit': 'mm', 'default': '10'}
                ]
            },
            'Circular': {
                'function': self.calc_circular_section,
                'params': [
                    {'name': 'Diameter', 'unit': 'mm', 'default': '150'}
                ]
            }
        }

    def create_widgets(self):
        """Create all GUI components"""
        # Control Frame
        self.control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        
        # File Selection
        self.file_label = ttk.Label(self.control_frame, text="Beam Data File:")
        self.file_entry = ttk.Entry(self.control_frame, width=40)
        self.browse_btn = ttk.Button(self.control_frame, text="Browse", command=self.load_file)
        
        # Material Selection
        self.material_label = ttk.Label(self.control_frame, text="Material:")
        self.material_combo = ttk.Combobox(
            self.control_frame, 
            values=list(self.materials.keys()),
            state="readonly"
        )
        self.material_combo.current(0)
        self.material_combo.bind("<<ComboboxSelected>>", self.on_material_change)
        
        # Section Selection
        self.section_label = ttk.Label(self.control_frame, text="Cross-Section:")
        self.section_combo = ttk.Combobox(
            self.control_frame,
            values=list(self.sections.keys()),
            state="readonly"
        )
        self.section_combo.current(0)
        self.section_combo.bind("<<ComboboxSelected>>", self.on_section_change)
        
        # Section Parameters Frame
        self.section_params_frame = ttk.Frame(self.control_frame)
        self.section_entries = {}
        self.setup_section_parameters()
        
        # Analysis Buttons
        self.analyze_btn = ttk.Button(
            self.control_frame, 
            text="Run Analysis", 
            command=self.run_analysis
        )
        
        # AI Optimization Frame
        self.optimization_frame = ttk.LabelFrame(self.control_frame, text="AI Design Optimization", padding=5)
        
        # Optimization objectives
        ttk.Label(self.optimization_frame, text="Optimize for:").grid(row=0, column=0, sticky=W)
        self.optimization_var = StringVar(value="Cost")
        objectives = ["Cost", "Weight", "Deflection", "Safety Factor"]
        self.objective_combo = ttk.Combobox(
            self.optimization_frame,
            textvariable=self.optimization_var,
            values=objectives,
            state="readonly"
        )
        self.objective_combo.grid(row=0, column=1, sticky=EW, padx=5)
        
        # Constraints
        ttk.Label(self.optimization_frame, text="Max Deflection (mm):").grid(row=1, column=0, sticky=W)
        self.deflection_entry = ttk.Entry(self.optimization_frame, width=8)
        self.deflection_entry.insert(0, "10")
        self.deflection_entry.grid(row=1, column=1, sticky=W, padx=5)
        
        ttk.Label(self.optimization_frame, text="Min Safety Factor:").grid(row=2, column=0, sticky=W)
        self.safety_factor_entry = ttk.Entry(self.optimization_frame, width=8)
        self.safety_factor_entry.insert(0, "1.5")
        self.safety_factor_entry.grid(row=2, column=1, sticky=W, padx=5)
        
        # Optimize button
        self.optimize_btn = ttk.Button(
            self.optimization_frame,
            text="Find Optimal Design",
            command=self.run_optimization,
            state=DISABLED
        )
        self.optimize_btn.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.optimization_frame,
            orient=HORIZONTAL,
            mode='determinate'
        )
        self.progress.grid(row=4, column=0, columnspan=2, sticky="ew")
        
        self.optimization_frame.columnconfigure(1, weight=1)
        
        # Results Display
        self.results_frame = ttk.LabelFrame(self.root, text="Results", padding=10)
        self.results_text = Text(self.results_frame, height=10, wrap=WORD)
        self.results_scroll = ttk.Scrollbar(
            self.results_frame,
            orient=VERTICAL,
            command=self.results_text.yview
        )
        self.results_text.configure(yscrollcommand=self.results_scroll.set)
        
        # Plot Area
        self.plot_frame = ttk.Frame(self.root)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        
        # Status Bar
        self.status_var = StringVar()
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=SUNKEN,
            anchor=W
        )

    def setup_layout(self):
        """Arrange widgets in the window"""
        # Control Frame Layout
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # File Selection
        self.file_label.grid(row=0, column=0, sticky=W, pady=5)
        self.file_entry.grid(row=0, column=1, padx=5, sticky=EW)
        self.browse_btn.grid(row=0, column=2, pady=5)
        
        # Material Selection
        self.material_label.grid(row=1, column=0, sticky=W, pady=5)
        self.material_combo.grid(row=1, column=1, columnspan=2, sticky=EW, pady=5)
        
        # Section Selection
        self.section_label.grid(row=2, column=0, sticky=W, pady=5)
        self.section_combo.grid(row=2, column=1, columnspan=2, sticky=EW, pady=5)
        
        # Section Parameters
        self.section_params_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Analysis Button
        self.analyze_btn.grid(row=4, column=0, columnspan=3, pady=10)
        
        # Optimization Frame
        self.optimization_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Results Frame
        self.results_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.results_text.grid(row=0, column=0, sticky="nsew")
        self.results_scroll.grid(row=0, column=1, sticky="ns")
        
        # Plot Frame
        self.plot_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=10, sticky="nsew")
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        
        # Status Bar
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Configure grid weights
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.control_frame.columnconfigure(1, weight=1)
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)

    def setup_menu(self):
        """Create the menu bar"""
        menubar = Menu(self.root)
        
        # File Menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Analysis", command=self.new_analysis)
        file_menu.add_command(label="Open...", command=self.load_file_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results...", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help Menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

    def setup_section_parameters(self):
        """Create input fields for the current section type"""
        # Clear existing widgets
        for widget in self.section_params_frame.winfo_children():
            widget.destroy()
        
        self.section_entries = {}
        section_type = self.section_combo.get()
        params = self.sections[section_type]['params']
        
        for i, param in enumerate(params):
            # Create label
            label = ttk.Label(
                self.section_params_frame,
                text=f"{param['name']} ({param['unit']}):"
            )
            label.grid(row=i//2, column=(i%2)*2, sticky=W, padx=5, pady=2)
            
            # Create entry field
            entry = ttk.Entry(self.section_params_frame, width=8)
            entry.insert(0, param['default'])
            entry.grid(row=i//2, column=(i%2)*2+1, sticky=W, padx=5, pady=2)
            
            # Store reference to entry
            self.section_entries[param['name']] = entry

    # Section Calculation Methods
    def calc_rectangular_section(self, width, height):
        """Calculate properties for rectangular section"""
        width_m = float(width)/1000
        height_m = float(height)/1000
        area = width_m * height_m
        I = (width_m * height_m**3)/12
        S = I / (height_m/2)
        return {'A': area, 'I': I, 'S': S}

    def calc_I_section(self, width, height, flange_thick, web_thick):
        """Calculate properties for I-beam section"""
        # Convert to meters
        w = float(width)/1000
        h = float(height)/1000
        tf = float(flange_thick)/1000
        tw = float(web_thick)/1000
        
        # Calculate area
        A = (2 * w * tf) + ((h - 2*tf) * tw)
        
        # Calculate moment of inertia
        I = (w * h**3)/12 - ((w-tw)*(h-2*tf)**3)/12
        
        # Section modulus
        S = I / (h/2)
        
        return {'A': A, 'I': I, 'S': S}

    def calc_circular_section(self, diameter):
        """Calculate properties for circular section"""
        dia_m = float(diameter)/1000
        area = np.pi * (dia_m/2)**2
        I = np.pi * (dia_m**4)/64
        S = I / (dia_m/2)
        return {'A': area, 'I': I, 'S': S}

    # Event Handlers
    def on_material_change(self, event):
        """Handle material selection change"""
        self.update_ui_state()

    def on_section_change(self, event):
        """Handle section type change"""
        self.setup_section_parameters()
        self.update_ui_state()

    def load_file_dialog(self):
        """Open file dialog to select beam data file"""
        filepath = filedialog.askopenfilename(
            filetypes=[
                ("Excel files", "*.xlsx;*.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            self.file_entry.delete(0, END)
            self.file_entry.insert(0, filepath)
            self.load_file()

    def load_file(self):
        """Load beam data from selected file"""
        filepath = self.file_entry.get()
        if not filepath:
            return
        
        try:
            if filepath.endswith('.csv'):
                self.current_data = pd.read_csv(filepath)
            else:
                self.current_data = pd.read_excel(filepath)
            
            # Verify required columns
            required_cols = {'Distance (m)', 'SF (kN)', 'BM (kN-m)'}
            if not required_cols.issubset(self.current_data.columns):
                raise ValueError("File missing required columns")
            
            self.status_var.set(f"Loaded: {os.path.basename(filepath)}")
            self.update_ui_state()
            
        except Exception as e:
            messagebox.showerror(
                "Load Error",
                f"Failed to load file:\n{str(e)}\n\n"
                "Please ensure the file contains:\n"
                "- Distance (m)\n- SF (kN)\n- BM (kN-m) columns"
            )
            self.current_data = None
            self.update_ui_state()

    def run_analysis(self):
        """Perform beam analysis with current settings"""
        if self.current_data is None:
            return
        
        try:
            # Get selected material
            material = self.material_combo.get()
            material_props = self.materials[material]
            
            # Get section properties
            section_type = self.section_combo.get()
            section_func = self.sections[section_type]['function']
            
            # Get parameter values from entries
            param_values = []
            for param in self.sections[section_type]['params']:
                value = self.section_entries[param['name']].get()
                if not value or not self.validate_number(value):
                    raise ValueError(f"Invalid {param['name']} value")
                param_values.append(value)
            
            # Calculate section properties
            section_props = section_func(*param_values)
            
            # Get beam data
            x = self.current_data['Distance (m)'].values
            sf = self.current_data['SF (kN)'].values
            bm = self.current_data['BM (kN-m)'].values
            
            # Calculate stresses (convert kN to N)
            max_bm = np.max(np.abs(bm))
            max_sf = np.max(np.abs(sf))
            
            bending_stress = (max_bm * 1000) / section_props['S']  # Pa
            shear_stress = (max_sf * 1000) / section_props['A']    # Pa
            
            # Calculate safety factors
            bending_sf = material_props['σ_yield'] / bending_stress
            shear_sf = material_props['σ_yield'] / (shear_stress * 1.5)  # Approximate
            
            # Display results
            self.display_results(
                material=material,
                section_type=section_type,
                max_bm=max_bm,
                max_sf=max_sf,
                bending_stress=bending_stress,
                shear_stress=shear_stress,
                bending_sf=bending_sf,
                shear_sf=shear_stress,
                required_sf=material_props['safety_factor']
            )
            
            # Plot diagrams
            self.plot_diagrams(x, sf, bm, material_props['color'])
            
            self.status_var.set("Analysis completed successfully")
            
        except Exception as e:
            messagebox.showerror(
                "Analysis Error",
                f"Failed to complete analysis:\n{str(e)}"
            )
            self.status_var.set("Analysis failed")

    def run_optimization(self):
        """Use genetic algorithms to find optimal beam design with timeout handling"""
        try:
            # Get constraints
            max_deflection = float(self.deflection_entry.get())/1000  # Convert to meters
            min_safety_factor = float(self.safety_factor_entry.get())
            
            # Disable button during optimization
            self.optimize_btn.config(state=DISABLED)
            self.progress["value"] = 0
            self.root.update()
            
            # Setup optimization problem
            def fitness_function(X):
                try:
                    # Update progress bar
                    self.progress["value"] += 1
                    if self.progress["value"] >= 100:
                        self.progress["value"] = 0
                    self.root.update()
                    
                    # X contains design parameters [material_index, section_type_index, param1, param2...]
                    material = list(self.materials.keys())[int(X[0])]
                    section = list(self.sections.keys())[int(X[1])]
                    
                    # Get material properties
                    mat_props = self.materials[material]
                    
                    # Calculate section properties
                    section_func = self.sections[section]['function']
                    params = [str(x) for x in X[2:2+len(self.sections[section]['params'])]]
                    
                    try:
                        section_props = section_func(*params)
                    except:
                        return 1e12  # Large penalty for invalid parameters
                    
                    # Calculate stresses and deflections
                    max_bm = np.max(np.abs(self.current_data['BM (kN-m)'].values)) * 1000  # N-m
                    max_sf = np.max(np.abs(self.current_data['SF (kN)'].values)) * 1000    # N
                    
                    bending_stress = max_bm / section_props['S']
                    shear_stress = max_sf / section_props['A']
                    
                    # Calculate deflection (simplified)
                    L = self.current_data['Distance (m)'].max()
                    deflection = (5 * max_bm * L**2) / (48 * mat_props['E'] * section_props['I'])
                    
                    # Calculate objectives
                    if self.optimization_var.get() == "Cost":
                        # Estimate weight and cost
                        volume = section_props['A'] * L
                        density = 7850 if "Steel" in material else 2700  # kg/m3 (simplified)
                        weight = volume * density
                        cost = weight * mat_props['cost']
                        objective = cost
                    elif self.optimization_var.get() == "Weight":
                        volume = section_props['A'] * L
                        density = 7850 if "Steel" in material else 2700
                        objective = volume * density
                    elif self.optimization_var.get() == "Deflection":
                        objective = deflection
                    else:  # Safety Factor
                        bending_sf = mat_props['σ_yield'] / bending_stress
                        objective = -bending_sf  # Negative because we want to maximize
                    
                    # Penalty for constraints
                    penalty = 0
                    if deflection > max_deflection:
                        penalty += 1e6 * (deflection - max_deflection)
                    
                    bending_sf = mat_props['σ_yield'] / bending_stress
                    if bending_sf < min_safety_factor:
                        penalty += 1e6 * (min_safety_factor - bending_sf)
                    
                    return objective + penalty
                except Exception as e:
                    print(f"Error in fitness function: {e}")
                    return 1e12  # Return large penalty if error occurs
            
            # Calculate total number of parameters
            num_params = 2 + max(len(s['params']) for s in self.sections.values())
            
            # Setup algorithm parameters with reduced complexity
            algorithm_param = {
                'max_num_iteration': 30,  # Reduced from 50
                'population_size': 15,    # Reduced from 20
                'mutation_probability': 0.1,
                'elit_ratio': 0.01,
                'crossover_probability': 0.5,
                'parents_portion': 0.3,
                'crossover_type': 'uniform',
                'max_iteration_without_improv': 5  # Reduced from 10
            }
            
            # Variable bounds
            varbound = []
            # Material index (integer)
            varbound.append([0, len(self.materials)-1])
            # Section type index (integer)
            varbound.append([0, len(self.sections)-1])
            # Section parameters (continuous)
            for section in self.sections.values():
                for param in section['params']:
                    default = float(param['default'])
                    varbound.append([default*0.5, default*2])  # Allow ±50% variation
            
            # Convert to numpy array
            varbound = np.array(varbound[:num_params])
            
            # Create variable types array (first 2 are int, rest are real)
            var_types = np.array(['int']*2 + ['real']*(num_params-2))
            
            # Run optimization with timeout handling
            try:
                model = ga(
                    function=fitness_function,
                    dimension=num_params,
                    variable_type_mixed=var_types,
                    variable_boundaries=varbound,
                    algorithm_parameters=algorithm_param,
                    convergence_curve=False
                )
                
                model.run()
                
                # Check if we got a valid solution
                if not hasattr(model, 'output_dict') or model.output_dict is None:
                    raise RuntimeError("Optimization failed to produce results")
                
                # Apply best solution
                solution = model.output_dict['variable']
                self.material_combo.current(int(solution[0]))
                self.section_combo.current(int(solution[1]))
                self.on_section_change(None)
                
                # Set parameter values
                section_params = self.sections[self.section_combo.get()]['params']
                for i, param in enumerate(section_params):
                    self.section_entries[param['name']].delete(0, END)
                    self.section_entries[param['name']].insert(0, f"{solution[2+i]:.1f}")
                
                self.run_analysis()
                self.status_var.set("Optimization complete - best design found")
                
            except Exception as e:
                messagebox.showerror("Optimization Error", 
                                   f"Optimization failed to complete:\n{str(e)}\n\n"
                                   "Try adjusting the constraints or optimization parameters.")
                self.status_var.set("Optimization failed")
                
        except Exception as e:
            messagebox.showerror("Optimization Error", f"Failed to start optimization:\n{str(e)}")
        finally:
            self.optimize_btn.config(state=NORMAL)
            self.progress["value"] = 0

    def display_results(self, material, section_type, max_bm, max_sf, 
                       bending_stress, shear_stress, bending_sf, shear_sf, required_sf):
        """Display analysis results in the text box"""
        self.results_text.config(state=NORMAL)
        self.results_text.delete(1.0, END)
        
        # Add results content
        self.results_text.insert(END, f"BEAM ANALYSIS RESULTS\n{'='*40}\n\n")
        self.results_text.insert(END, f"Material: {material}\n")
        self.results_text.insert(END, f"Cross-Section: {section_type}\n\n")
        
        self.results_text.insert(END, "MAXIMUM VALUES:\n")
        self.results_text.insert(END, f"- Bending Moment: {max_bm:.2f} kN-m\n")
        self.results_text.insert(END, f"- Shear Force: {max_sf:.2f} kN\n\n")
        
        self.results_text.insert(END, "STRESS ANALYSIS:\n")
        self.results_text.insert(END, f"- Bending Stress: {bending_stress/1e6:.2f} MPa\n")
        self.results_text.insert(END, f"- Shear Stress: {shear_stress/1e6:.2f} MPa\n\n")
        
        self.results_text.insert(END, "SAFETY FACTORS:\n")
        self.results_text.insert(END, f"- Bending: {bending_sf:.2f} (Required: {required_sf:.1f})\n")
        self.results_text.insert(END, f"- Shear: {shear_sf:.2f}\n\n")
        
        # Add safety status
        if bending_sf >= required_sf:
            self.results_text.insert(END, "DESIGN STATUS: SAFE\n", 'safe')
        else:
            self.results_text.insert(END, "DESIGN STATUS: UNSAFE\n", 'unsafe')
        
        # Configure text tags
        self.results_text.tag_config('safe', foreground='green')
        self.results_text.tag_config('unsafe', foreground='red')
        self.results_text.config(state=DISABLED)

    def plot_diagrams(self, x, sf, bm, color):
        """Plot shear force and bending moment diagrams"""
        self.figure.clear()
        
        # Shear Force Diagram
        ax1 = self.figure.add_subplot(211)
        ax1.plot(x, sf, color=color, linewidth=2)
        ax1.fill_between(x, sf, color=color, alpha=0.3)
        ax1.set_title('Shear Force Diagram (SFD)')
        ax1.set_ylabel('Shear Force (kN)')
        ax1.grid(True)
        
        # Bending Moment Diagram
        ax2 = self.figure.add_subplot(212)
        ax2.plot(x, bm, color=color, linewidth=2)
        ax2.fill_between(x, bm, color=color, alpha=0.3)
        ax2.set_title('Bending Moment Diagram (BMD)')
        ax2.set_xlabel('Distance along beam (m)')
        ax2.set_ylabel('Bending Moment (kN-m)')
        ax2.grid(True)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def export_results(self):
        """Export analysis results to PDF"""
        if not hasattr(self, 'current_data') or self.current_data is None:
            messagebox.showwarning("No Data", "Please load and analyze data before exporting")
            return
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            plot_path = os.path.join(temp_dir, "beam_diagrams.png")
            
            # Save plot image
            self.figure.savefig(plot_path, dpi=150, bbox_inches='tight')
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Beam Analysis Report", 0, 1, 'C')
            pdf.ln(10)
            
            # Add text content
            pdf.set_font("Arial", '', 12)
            pdf.multi_cell(0, 7, self.results_text.get(1.0, END))
            pdf.ln(10)
            
            # Add plot image
            pdf.image(plot_path, x=10, w=190)
            
            # Ask for save location
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"beam_analysis_{timestamp}.pdf"
            )
            
            if save_path:
                pdf.output(save_path)
                messagebox.showinfo(
                    "Export Successful",
                    f"Report successfully saved to:\n{save_path}"
                )
                self.status_var.set(f"Report saved to {os.path.basename(save_path)}")
        
        except Exception as e:
            messagebox.showerror(
                "Export Failed",
                f"Could not export results:\n{str(e)}"
            )

    def new_analysis(self):
        """Reset the application for a new analysis"""
        self.current_data = None
        self.file_entry.delete(0, END)
        self.results_text.config(state=NORMAL)
        self.results_text.delete(1.0, END)
        self.results_text.config(state=DISABLED)
        self.figure.clear()
        self.canvas.draw()
        self.update_ui_state()
        self.status_var.set("Ready for new analysis")

    def show_help(self):
        """Display help information"""
        messagebox.showinfo(
            "Help",
            "Beam Analysis Tool Help\n\n"
            "1. Load beam data file (CSV or Excel)\n"
            "2. Select material and cross-section type\n"
            "3. Enter section dimensions\n"
            "4. Click 'Run Analysis'\n"
            "5. Use 'Find Optimal Design' for AI-powered optimization\n"
            "6. Export results if needed"
        )

    def show_about(self):
        """Display about information"""
        messagebox.showinfo(
            "About",
            "Beam Analysis Tool with AI Optimization\n\n"
            "Version 2.1\n"
            "© 2023 Structural Engineering Tools"
        )

    def update_ui_state(self):
        """Update UI elements based on current state"""
        # Enable/disable buttons based on data availability
        if self.current_data is not None:
            self.analyze_btn.config(state=NORMAL)
            self.optimize_btn.config(state=NORMAL)
        else:
            self.analyze_btn.config(state=DISABLED)
            self.optimize_btn.config(state=DISABLED)

    def validate_number(self, input_str):
        """Validate that input is a positive number"""
        try:
            value = float(input_str)
            return value > 0
        except ValueError:
            return False

if __name__ == "__main__":
    root = Tk()
    app = BeamAnalyzerApp(root)
    root.mainloop()
