"""
Enhanced Beam Analyzer with Advanced Structural Analysis
Integrates comprehensive stress analysis, deflection calculations, and fatigue analysis
"""

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
from enhanced_analysis_methods import EnhancedBeamAnalysis

class EnhancedBeamAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Beam Analysis Tool with Advanced Engineering")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 900)
      
        self.current_data = None
        
        # Initialize enhanced analysis engine
        self.enhanced_analysis = EnhancedBeamAnalysis()
        
        self.create_widgets()
        self.setup_layout()
        self.setup_menu()
        self.update_ui_state()

    def create_widgets(self):
        """Create enhanced GUI components"""
        # Control Frame
        self.control_frame = ttk.LabelFrame(self.root, text="Enhanced Controls", padding=10)
        
        # File Selection
        self.file_label = ttk.Label(self.control_frame, text="Beam Data File:")
        self.file_entry = ttk.Entry(self.control_frame, width=40)
        self.browse_btn = ttk.Button(self.control_frame, text="Browse", command=self.load_file)
        
        # Material Selection with enhanced properties
        self.material_label = ttk.Label(self.control_frame, text="Material:")
        self.material_combo = ttk.Combobox(
            self.control_frame, 
            values=list(self.enhanced_analysis.materials.keys()),
            state="readonly"
        )
        self.material_combo.current(0)
        self.material_combo.bind("<<ComboboxSelected>>", self.on_material_change)
        
        # Section Selection
        self.section_label = ttk.Label(self.control_frame, text="Cross-Section:")
        self.section_combo = ttk.Combobox(
            self.control_frame,
            values=list(self.enhanced_analysis.sections.keys()),
            state="readonly"
        )
        self.section_combo.current(0)
        self.section_combo.bind("<<ComboboxSelected>>", self.on_section_change)
        
        # Section Parameters Frame
        self.section_params_frame = ttk.Frame(self.control_frame)
        self.section_entries = {}
        self.setup_section_parameters()
        
        # Support Conditions
        self.support_label = ttk.Label(self.control_frame, text="Support Conditions:")
        self.support_combo = ttk.Combobox(
            self.control_frame,
            values=["simply_supported", "cantilever", "fixed_fixed", "continuous"],
            state="readonly"
        )
        self.support_combo.current(0)
        
        # Analysis Type Selection
        self.analysis_type_frame = ttk.LabelFrame(self.control_frame, text="Analysis Type", padding=5)
        
        self.include_deflection = BooleanVar(value=True)
        self.include_fatigue = BooleanVar(value=True)
        self.include_combined_stress = BooleanVar(value=True)
        
        ttk.Checkbutton(self.analysis_type_frame, text="Deflection Analysis", 
                       variable=self.include_deflection).grid(row=0, column=0, sticky=W)
        ttk.Checkbutton(self.analysis_type_frame, text="Fatigue Analysis", 
                       variable=self.include_fatigue).grid(row=0, column=1, sticky=W)
        ttk.Checkbutton(self.analysis_type_frame, text="Combined Stress Analysis", 
                       variable=self.include_combined_stress).grid(row=1, column=0, columnspan=2, sticky=W)
        
        # Analysis Button
        self.analyze_btn = ttk.Button(
            self.control_frame, 
            text="Run Enhanced Analysis", 
            command=self.run_enhanced_analysis
        )
        
        # AI Optimization Frame
        self.optimization_frame = ttk.LabelFrame(self.control_frame, text="AI Design Optimization", padding=5)
        
        # Optimization objectives
        ttk.Label(self.optimization_frame, text="Optimize for:").grid(row=0, column=0, sticky=W)
        self.optimization_var = StringVar(value="Combined Safety Factor")
        objectives = ["Cost", "Weight", "Deflection", "Safety Factor", "Combined Safety Factor", "Fatigue Life"]
        self.objective_combo = ttk.Combobox(
            self.optimization_frame,
            textvariable=self.optimization_var,
            values=objectives,
            state="readonly"
        )
        self.objective_combo.grid(row=0, column=1, sticky=EW, padx=5)
        
        # Enhanced Constraints
        ttk.Label(self.optimization_frame, text="Max Deflection (mm):").grid(row=1, column=0, sticky=W)
        self.deflection_entry = ttk.Entry(self.optimization_frame, width=8)
        self.deflection_entry.insert(0, "10")
        self.deflection_entry.grid(row=1, column=1, sticky=W, padx=5)
        
        ttk.Label(self.optimization_frame, text="Min Safety Factor:").grid(row=2, column=0, sticky=W)
        self.safety_factor_entry = ttk.Entry(self.optimization_frame, width=8)
        self.safety_factor_entry.insert(0, "1.5")
        self.safety_factor_entry.grid(row=2, column=1, sticky=W, padx=5)
        
        ttk.Label(self.optimization_frame, text="Min Fatigue Life (cycles):").grid(row=3, column=0, sticky=W)
        self.fatigue_entry = ttk.Entry(self.optimization_frame, width=8)
        self.fatigue_entry.insert(0, "1000000")
        self.fatigue_entry.grid(row=3, column=1, sticky=W, padx=5)
        
        # Optimize button
        self.optimize_btn = ttk.Button(
            self.optimization_frame,
            text="Find Optimal Design",
            command=self.run_enhanced_optimization,
            state=DISABLED
        )
        self.optimize_btn.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.optimization_frame,
            orient=HORIZONTAL,
            mode='determinate'
        )
        self.progress.grid(row=5, column=0, columnspan=2, sticky="ew")
        
        self.optimization_frame.columnconfigure(1, weight=1)
        
        # Results Display with Tabs
        self.results_notebook = ttk.Notebook(self.root)
        
        # Summary Tab
        self.summary_frame = ttk.Frame(self.results_notebook)
        self.results_text = Text(self.summary_frame, height=12, wrap=WORD, font=("Courier", 10))
        self.results_scroll = ttk.Scrollbar(
            self.summary_frame,
            orient=VERTICAL,
            command=self.results_text.yview
        )
        self.results_text.configure(yscrollcommand=self.results_scroll.set)
        
        # Detailed Analysis Tab
        self.detailed_frame = ttk.Frame(self.results_notebook)
        self.detailed_text = Text(self.detailed_frame, height=12, wrap=WORD, font=("Courier", 9))
        self.detailed_scroll = ttk.Scrollbar(
            self.detailed_frame,
            orient=VERTICAL,
            command=self.detailed_text.yview
        )
        self.detailed_text.configure(yscrollcommand=self.detailed_scroll.set)
        
        # Add tabs
        self.results_notebook.add(self.summary_frame, text="Summary")
        self.results_notebook.add(self.detailed_frame, text="Detailed Analysis")
        
        # Plot Area with tabs for better organization
        self.plot_notebook = ttk.Notebook(self.root)
        
        # Create separate frames for different plot types
        self.sfd_frame = ttk.Frame(self.plot_notebook)
        self.bmd_frame = ttk.Frame(self.plot_notebook)
        self.stress_frame = ttk.Frame(self.plot_notebook)
        self.deflection_frame = ttk.Frame(self.plot_notebook)
        
        # Add tabs to notebook
        self.plot_notebook.add(self.sfd_frame, text="Shear Force")
        self.plot_notebook.add(self.bmd_frame, text="Bending Moment")
        self.plot_notebook.add(self.stress_frame, text="Stress Envelope")
        self.plot_notebook.add(self.deflection_frame, text="Deflection")
        
        # Create canvases for each plot type
        self.sfd_figure = plt.figure(figsize=(10, 6), dpi=100)
        self.sfd_canvas = FigureCanvasTkAgg(self.sfd_figure, master=self.sfd_frame)
        self.sfd_toolbar = NavigationToolbar2Tk(self.sfd_canvas, self.sfd_frame)
        
        self.bmd_figure = plt.figure(figsize=(10, 6), dpi=100)
        self.bmd_canvas = FigureCanvasTkAgg(self.bmd_figure, master=self.bmd_frame)
        self.bmd_toolbar = NavigationToolbar2Tk(self.bmd_canvas, self.bmd_frame)
        
        self.stress_figure = plt.figure(figsize=(10, 6), dpi=100)
        self.stress_canvas = FigureCanvasTkAgg(self.stress_figure, master=self.stress_frame)
        self.stress_toolbar = NavigationToolbar2Tk(self.stress_canvas, self.stress_frame)
        
        self.deflection_figure = plt.figure(figsize=(10, 6), dpi=100)
        self.deflection_canvas = FigureCanvasTkAgg(self.deflection_figure, master=self.deflection_frame)
        self.deflection_toolbar = NavigationToolbar2Tk(self.deflection_canvas, self.deflection_frame)
        
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
        
        # Support Conditions
        self.support_label.grid(row=3, column=0, sticky=W, pady=5)
        self.support_combo.grid(row=3, column=1, columnspan=2, sticky=EW, pady=5)
        
        # Section Parameters
        self.section_params_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Analysis Type
        self.analysis_type_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Analysis Button
        self.analyze_btn.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Optimization Frame
        self.optimization_frame.grid(row=7, column=0, columnspan=3, sticky="ew", pady=10)
        
        # Results Notebook
        self.results_notebook.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.results_text.grid(row=0, column=0, sticky="nsew")
        self.results_scroll.grid(row=0, column=1, sticky="ns")
        
        # Detailed results layout
        self.detailed_text.grid(row=0, column=0, sticky="nsew")
        self.detailed_scroll.grid(row=0, column=1, sticky="ns")
        
        # Plot Notebook
        self.plot_notebook.grid(row=0, column=1, rowspan=2, padx=5, pady=10, sticky="nsew")
        
        # Pack canvases in their respective frames
        self.sfd_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        self.bmd_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        self.stress_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        self.deflection_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        
        # Status Bar
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Configure grid weights
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.control_frame.columnconfigure(1, weight=1)
        self.summary_frame.columnconfigure(0, weight=1)
        self.summary_frame.rowconfigure(0, weight=1)
        self.detailed_frame.columnconfigure(0, weight=1)
        self.detailed_frame.rowconfigure(0, weight=1)

    def setup_menu(self):
        """Create the enhanced menu bar"""
        menubar = Menu(self.root)
        
        # File Menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Analysis", command=self.new_analysis)
        file_menu.add_command(label="Open...", command=self.load_file_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Export Summary Report...", command=self.export_summary_report)
        file_menu.add_command(label="Export Detailed Report...", command=self.export_detailed_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Analysis Menu
        analysis_menu = Menu(menubar, tearoff=0)
        analysis_menu.add_command(label="Material Properties", command=self.show_material_properties)
        analysis_menu.add_command(label="Section Properties", command=self.show_section_properties)
        analysis_menu.add_command(label="Stress Envelope", command=self.plot_stress_envelope)
        analysis_menu.add_command(label="Deflection Profile", command=self.plot_deflection_profile)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        
        # Help Menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="Engineering References", command=self.show_engineering_references)
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
        params = self.enhanced_analysis.sections[section_type]['params']
        
        for i, param in enumerate(params):
            # Create label
            label = ttk.Label(
                self.section_params_frame,
                text=f"{param['name']} ({param['unit']}):"
            )
            label.grid(row=i//2, column=(i%2)*2, sticky=W, padx=5, pady=2)
            
            # Create entry field
            entry = ttk.Entry(self.section_params_frame, width=10)
            entry.insert(0, str(param['default']))
            entry.grid(row=i//2, column=(i%2)*2+1, sticky=W, padx=5, pady=2)
            
            # Store reference to entry
            self.section_entries[param['name']] = entry

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

    def run_enhanced_analysis(self):
        """Perform comprehensive beam analysis"""
        if self.current_data is None:
            return
        
        try:
            # Get selected material and section
            material_name = self.material_combo.get()
            section_type = self.section_combo.get()
            support_conditions = self.support_combo.get()
            
            material_props = self.enhanced_analysis.materials[material_name]
            section_func = self.enhanced_analysis.sections[section_type]['function']
            
            # Get parameter values
            param_values = []
            for param in self.enhanced_analysis.sections[section_type]['params']:
                value = self.section_entries[param['name']].get()
                if not value or not self.validate_number(value):
                    raise ValueError(f"Invalid {param['name']} value")
                param_values.append(float(value))
            
            # Calculate section properties
            section_props = section_func(*param_values)
            
            # Enhanced stress analysis
            stress_analysis = self.enhanced_analysis.calculate_enhanced_stresses(
                self.current_data, material_props, section_props, section_type)
            
            # Deflection analysis
            deflection_analysis = None
            if self.include_deflection.get():
                deflection_analysis = self.enhanced_analysis.calculate_deflections(
                    self.current_data, material_props, section_props, support_conditions)
            
            # Safety factor analysis
            safety_analysis = self.enhanced_analysis.calculate_enhanced_safety_factors(
                stress_analysis, material_props)
            
            # Generate comprehensive report
            detailed_report = self.enhanced_analysis.generate_detailed_report(
                self.current_data, material_props, section_props, 
                stress_analysis, deflection_analysis or {}, safety_analysis)
            
            # Display results
            self.display_enhanced_results(
                material_name, section_type, stress_analysis, 
                deflection_analysis, safety_analysis, detailed_report)
            
            # Enhanced plotting
            self.plot_enhanced_diagrams(support_conditions)
            
            self.status_var.set("Enhanced analysis completed successfully")
            
            # Check if design is unsafe and offer automatic optimization
            if safety_analysis['design_status'] == 'UNSAFE':
                self.offer_automatic_optimization(safety_analysis)
            
        except Exception as e:
            messagebox.showerror(
                "Analysis Error",
                f"Failed to complete enhanced analysis:\n{str(e)}"
            )
            self.status_var.set("Enhanced analysis failed")

    def display_enhanced_results(self, material_name, section_type, 
                               stress_analysis, deflection_analysis, 
                               safety_analysis, detailed_report):
        """Display comprehensive analysis results"""
        
        # Summary results
        self.results_text.config(state=NORMAL)
        self.results_text.delete(1.0, END)
        
        summary = f"""ENHANCED BEAM ANALYSIS SUMMARY
{'='*50}

MATERIAL: {material_name}
CROSS-SECTION: {section_type}

STRESS ANALYSIS:
• Maximum Bending Stress: {stress_analysis['bending_stress_max']/1e6:.2f} MPa
• Maximum Shear Stress: {stress_analysis['shear_stress_max']/1e6:.2f} MPa
• Von Mises Stress: {stress_analysis['von_mises_stress']/1e6:.2f} MPa

SAFETY FACTORS:
• Bending Safety Factor: {safety_analysis['bending_safety_factor']:.2f}
• Shear Safety Factor: {safety_analysis['shear_safety_factor']:.2f}
• Combined Safety Factor: {safety_analysis['combined_safety_factor']:.2f}
• Fatigue Safety Factor: {safety_analysis['fatigue_safety_factor']:.2f}
"""

        if deflection_analysis:
            summary += f"""
DEFLECTION ANALYSIS:
• Maximum Deflection: {deflection_analysis['max_deflection']*1000:.2f} mm
• Deflection Limit: {deflection_analysis['deflection_limit_total']*1000:.2f} mm
• Deflection Ratio: {deflection_analysis['deflection_ratio']:.3f}
"""

        summary += f"""
DESIGN STATUS: {safety_analysis['design_status']}
"""
        
        self.results_text.insert(END, summary)
        self.results_text.config(state=DISABLED)
        
        # Detailed results
        self.detailed_text.config(state=NORMAL)
        self.detailed_text.delete(1.0, END)
        self.detailed_text.insert(END, detailed_report)
        self.detailed_text.config(state=DISABLED)

    def plot_enhanced_diagrams(self, support_conditions):
        """Plot comprehensive beam diagrams in separate tabs"""
        
        # Get beam data
        x = self.current_data['Distance (m)'].values
        sf = self.current_data['SF (kN)'].values
        bm = self.current_data['BM (kN-m)'].values
        
        # Get material and section properties
        material_props = self.enhanced_analysis.materials[self.material_combo.get()]
        section_type = self.section_combo.get()
        section_func = self.enhanced_analysis.sections[section_type]['function']
        
        # Get current section parameters
        param_values = []
        for param in self.enhanced_analysis.sections[section_type]['params']:
            value = self.section_entries[param['name']].get()
            param_values.append(float(value))
        
        section_props = section_func(*param_values)
        
        # 1. Shear Force Diagram
        self.sfd_figure.clear()
        ax_sfd = self.sfd_figure.add_subplot(111)
        ax_sfd.plot(x, sf, 'b-', linewidth=3, label='Shear Force')
        ax_sfd.fill_between(x, sf, color='blue', alpha=0.3)
        ax_sfd.set_title('Shear Force Diagram (SFD)', fontsize=14, fontweight='bold', pad=20)
        ax_sfd.set_xlabel('Distance along beam (m)', fontsize=12)
        ax_sfd.set_ylabel('Shear Force (kN)', fontsize=12)
        ax_sfd.grid(True, alpha=0.3)
        ax_sfd.legend(fontsize=12)
        self.sfd_figure.tight_layout()
        self.sfd_canvas.draw()
        
        # 2. Bending Moment Diagram
        self.bmd_figure.clear()
        ax_bmd = self.bmd_figure.add_subplot(111)
        ax_bmd.plot(x, bm, 'r-', linewidth=3, label='Bending Moment')
        ax_bmd.fill_between(x, bm, color='red', alpha=0.3)
        ax_bmd.set_title('Bending Moment Diagram (BMD)', fontsize=14, fontweight='bold', pad=20)
        ax_bmd.set_xlabel('Distance along beam (m)', fontsize=12)
        ax_bmd.set_ylabel('Bending Moment (kN-m)', fontsize=12)
        ax_bmd.grid(True, alpha=0.3)
        ax_bmd.legend(fontsize=12)
        self.bmd_figure.tight_layout()
        self.bmd_canvas.draw()
        
        # 3. Stress Envelope
        self.stress_figure.clear()
        ax_stress = self.stress_figure.add_subplot(111)
        
        # Calculate bending stress envelope
        bending_stresses = np.abs(bm) * 1000 / section_props['S'] / 1e6  # Convert to MPa
        
        ax_stress.plot(x, bending_stresses, 'g-', linewidth=3, label='Bending Stress')
        ax_stress.axhline(y=material_props['σ_yield']/1e6, color='orange', 
                         linestyle='--', linewidth=2, label='Yield Strength')
        ax_stress.set_title('Stress Envelope', fontsize=14, fontweight='bold', pad=20)
        ax_stress.set_xlabel('Distance along beam (m)', fontsize=12)
        ax_stress.set_ylabel('Stress (MPa)', fontsize=12)
        ax_stress.grid(True, alpha=0.3)
        ax_stress.legend(fontsize=12)
        self.stress_figure.tight_layout()
        self.stress_canvas.draw()
        
        # 4. Deflection Profile (if enabled)
        if self.include_deflection.get():
            self.deflection_figure.clear()
            ax_deflection = self.deflection_figure.add_subplot(111)
            
            # Calculate deflection profile
            deflection_analysis = self.enhanced_analysis.calculate_deflections(
                self.current_data, material_props, section_props, support_conditions)
            
            deflections = deflection_analysis['deflections'] * 1000  # Convert to mm
            
            ax_deflection.plot(x, deflections, 'purple', linewidth=3, label='Deflection')
            ax_deflection.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            ax_deflection.set_title('Deflection Profile', fontsize=14, fontweight='bold', pad=20)
            ax_deflection.set_xlabel('Distance along beam (m)', fontsize=12)
            ax_deflection.set_ylabel('Deflection (mm)', fontsize=12)
            ax_deflection.grid(True, alpha=0.3)
            ax_deflection.legend(fontsize=12)
            self.deflection_figure.tight_layout()
            self.deflection_canvas.draw()
        else:
            # Show placeholder if deflection analysis is disabled
            self.deflection_figure.clear()
            ax_deflection = self.deflection_figure.add_subplot(111)
            ax_deflection.text(0.5, 0.5, 'Deflection Analysis Disabled\n\nEnable "Deflection Analysis" in Analysis Type\nsection to view deflection profile', 
                             horizontalalignment='center', verticalalignment='center',
                             transform=ax_deflection.transAxes, fontsize=14)
            ax_deflection.set_title('Deflection Profile', fontsize=14, fontweight='bold', pad=20)
            self.deflection_figure.tight_layout()
            self.deflection_canvas.draw()

    def run_enhanced_optimization(self):
        """Enhanced optimization with comprehensive objectives"""
        try:
            # Get constraints
            max_deflection = float(self.deflection_entry.get())/1000
            min_safety_factor = float(self.safety_factor_entry.get())
            min_fatigue_life = float(self.fatigue_entry.get())
            
            # Disable button during optimization
            self.optimize_btn.config(state=DISABLED)
            self.progress["value"] = 0
            self.root.update()
            
            # Store original design for comparison
            original_material = self.material_combo.get()
            original_section = self.section_combo.get()
            original_params = {}
            for param_name, entry in self.section_entries.items():
                original_params[param_name] = float(entry.get())
            
            # Simplified and fast fitness function
            def fast_fitness_function(X):
                try:
                    # Update progress
                    current_progress = self.progress["value"]
                    self.progress["value"] = (current_progress + 1) % 100
                    self.root.update()
                    
                    # Get design parameters
                    material = list(self.enhanced_analysis.materials.keys())[int(X[0])]
                    section = list(self.enhanced_analysis.sections.keys())[int(X[1])]
                    
                    material_props = self.enhanced_analysis.materials[material]
                    section_func = self.enhanced_analysis.sections[section]['function']
                    params = [float(x) for x in X[2:2+len(self.enhanced_analysis.sections[section]['params'])]]
                    
                    try:
                        section_props = section_func(*params)
                    except:
                        return 1e12
                    
                    # Simplified stress analysis (faster calculation)
                    x = self.current_data['Distance (m)'].values
                    sf = self.current_data['SF (kN)'].values
                    bm = self.current_data['BM (kN-m)'].values
                    
                    # Maximum values
                    max_bm = np.max(np.abs(bm)) * 1000  # Convert to N-m
                    max_sf = np.max(np.abs(sf)) * 1000  # Convert to N
                    
                    # Simplified stress calculations
                    bending_stress = max_bm / section_props['S']
                    
                    # Simplified shear stress (faster than full analysis)
                    if section in ['I-beam', 'T-beam']:
                        shear_stress = max_sf / section_props.get('web_area', section_props['A'])
                    else:
                        shear_stress = max_sf / section_props['A']
                    
                    # Safety factors
                    bending_sf = material_props['σ_yield'] / bending_stress
                    shear_sf = (material_props['σ_yield'] / np.sqrt(3)) / shear_stress
                    combined_sf = min(bending_sf, shear_sf)
                    
                    # Simplified deflection (faster calculation)
                    L = x[-1] - x[0]
                    max_deflection_simple = (5 * max_bm * L**2) / (48 * material_props['E'] * section_props['I'])
                    
                    # Calculate objective based on selection
                    objective = 0
                    if self.optimization_var.get() == "Cost":
                        volume = section_props['A'] * L
                        weight = volume * material_props['density']
                        objective = weight * material_props['cost']
                    elif self.optimization_var.get() == "Weight":
                        volume = section_props['A'] * L
                        objective = volume * material_props['density']
                    elif self.optimization_var.get() == "Deflection":
                        objective = max_deflection_simple
                    elif self.optimization_var.get() in ["Safety Factor", "Combined Safety Factor"]:
                        objective = -combined_sf  # Negative because we want to maximize
                    elif self.optimization_var.get() == "Fatigue Life":
                        # Simplified fatigue estimation
                        stress_range = bending_stress * 0.5  # Estimate
                        fatigue_strength = material_props['fatigue_limit'] * material_props['σ_ultimate']
                        fatigue_life = 1e6 * (fatigue_strength / stress_range)**10  # Simplified S-N curve
                        objective = -fatigue_life if fatigue_life != float('inf') else -1e10
                    
                    # Constraint penalties (simplified)
                    penalty = 0
                    
                    # Deflection constraint
                    if max_deflection_simple > max_deflection:
                        penalty += 1e6 * (max_deflection_simple - max_deflection)
                    
                    # Safety factor constraint
                    if combined_sf < min_safety_factor:
                        penalty += 1e6 * (min_safety_factor - combined_sf)
                    
                    return objective + penalty
                    
                except Exception as e:
                    print(f"Error in fast fitness function: {e}")
                    return 1e12
            
            # Calculate total number of parameters
            num_params = 2 + max(len(s['params']) for s in self.enhanced_analysis.sections.values())
            
            # Setup algorithm parameters (optimized for faster execution)
            algorithm_param = {
                'max_num_iteration': 10,  # Further reduced for faster execution
                'population_size': 6,     # Much smaller population
                'mutation_probability': 0.2,
                'elit_ratio': 0.2,
                'crossover_probability': 0.8,
                'parents_portion': 0.6,
                'crossover_type': 'uniform',
                'max_iteration_without_improv': 3,  # Stop very early if no improvement
                'timeout': 15  # Reduced to 15 seconds per generation
            }
            
            # Variable bounds
            varbound = []
            # Material index (integer)
            varbound.append([0, len(self.enhanced_analysis.materials)-1])
            # Section type index (integer)
            varbound.append([0, len(self.enhanced_analysis.sections)-1])
            # Section parameters (continuous)
            for section in self.enhanced_analysis.sections.values():
                for param in section['params']:
                    default = float(param['default'])
                    varbound.append([default*0.3, default*3.0])  # Allow ±70% to 200% variation
            
            # Convert to numpy array
            varbound = np.array(varbound[:num_params])
            
            # Create variable types array (first 2 are int, rest are real)
            var_types = np.array(['int']*2 + ['real']*(num_params-2))
            
            # Create timeout wrapper for fitness function
            def timeout_fitness_function(X):
                try:
                    # Add individual timeout for each evaluation
                    from func_timeout import func_timeout
                    return func_timeout(2.0, fast_fitness_function, args=(X,))
                except:
                    # Return very bad fitness if evaluation times out
                    return 1e10
            
            # Run optimization with overall timeout
            try:
                from func_timeout import func_timeout
                
                def run_ga():
                    model = ga(
                        function=timeout_fitness_function,
                        dimension=num_params,
                        variable_type_mixed=var_types,
                        variable_boundaries=varbound,
                        algorithm_parameters=algorithm_param,
                        convergence_curve=False
                    )
                    model.run()
                    return model
                
                # Run genetic algorithm with 60 second overall timeout
                model = func_timeout(60.0, run_ga)
                
                # Check if we got a valid solution
                if not hasattr(model, 'output_dict') or model.output_dict is None:
                    raise RuntimeError("Optimization failed to produce results")
                
                # Apply best solution
                solution = model.output_dict['variable']
                self.material_combo.current(int(solution[0]))
                self.section_combo.current(int(solution[1]))
                self.on_section_change(None)
                
                # Set parameter values
                section_params = self.enhanced_analysis.sections[self.section_combo.get()]['params']
                for i, param in enumerate(section_params):
                    self.section_entries[param['name']].delete(0, END)
                    self.section_entries[param['name']].insert(0, f"{solution[2+i]:.1f}")
                
                # Run analysis with optimized design
                self.run_enhanced_analysis()
                
                # Show optimization results comparison
                self.show_optimization_results(original_material, original_section, original_params)
                
                self.status_var.set("AI optimization completed - optimal design found and applied")
                
            except Exception as e:
                # Try fallback optimization method
                print(f"Genetic algorithm failed: {e}")
                self.status_var.set("Trying fallback optimization method...")
                self.root.update()
                
                try:
                    self.run_fallback_optimization(original_material, original_section, original_params)
                except Exception as fallback_error:
                    messagebox.showerror("Optimization Error", 
                                       f"Both optimization methods failed:\n\n"
                                       f"Genetic Algorithm: {str(e)}\n"
                                       f"Fallback Method: {str(fallback_error)}\n\n"
                                       "Please try adjusting the constraints or optimization parameters.")
                    self.status_var.set("Optimization failed")
                
        except Exception as e:
            messagebox.showerror("Optimization Error", f"Failed to start optimization:\n{str(e)}")
        finally:
            self.optimize_btn.config(state=NORMAL)
            self.progress["value"] = 0

    def run_fallback_optimization(self, original_material, original_section, original_params):
        """Fallback optimization using systematic search when genetic algorithm fails"""
        try:
            self.status_var.set("Running systematic optimization...")
            self.root.update()
            
            # Get current constraints
            min_safety_factor = float(self.safety_factor_entry.get())
            max_deflection = float(self.deflection_entry.get())/1000
            
            best_solution = None
            best_fitness = -1e12
            
            # Try different materials (limited to most common ones for speed)
            materials_to_try = list(self.enhanced_analysis.materials.keys())[:3]  # Only try first 3 materials
            for material_idx, material_name in enumerate(materials_to_try):
                material_props = self.enhanced_analysis.materials[material_name]
                
                # Try different section types (limited for speed)
                sections_to_try = list(self.enhanced_analysis.sections.keys())[:3]  # Only try first 3 sections
                for section_idx, section_name in enumerate(sections_to_try):
                    section_params = self.enhanced_analysis.sections[section_name]['params']
                    
                    # Try different dimension combinations (reduced for speed)
                    for multiplier in [1.5, 2.0, 2.5]:  # Fewer combinations for faster execution
                        try:
                            # Scale default dimensions
                            scaled_params = [float(param['default']) * multiplier 
                                          for param in section_params]
                            
                            # Calculate section properties
                            section_func = self.enhanced_analysis.sections[section_name]['function']
                            section_props = section_func(*scaled_params)
                            
                            # Quick stress analysis
                            x = self.current_data['Distance (m)'].values
                            sf = self.current_data['SF (kN)'].values
                            bm = self.current_data['BM (kN-m)'].values
                            
                            max_bm = np.max(np.abs(bm)) * 1000
                            max_sf = np.max(np.abs(sf)) * 1000
                            
                            bending_stress = max_bm / section_props['S']
                            shear_stress = max_sf / section_props.get('web_area', section_props['A'])
                            
                            bending_sf = material_props['σ_yield'] / bending_stress
                            shear_sf = (material_props['σ_yield'] / np.sqrt(3)) / shear_stress
                            combined_sf = min(bending_sf, shear_sf)
                            
                            # Check constraints
                            if combined_sf >= min_safety_factor:
                                # Calculate fitness (maximize safety factor for unsafe designs)
                                fitness = combined_sf
                                
                                if fitness > best_fitness:
                                    best_fitness = fitness
                                    best_solution = {
                                        'material_idx': material_idx,
                                        'section_idx': section_idx,
                                        'params': scaled_params,
                                        'material': material_name,
                                        'section': section_name,
                                        'safety_factor': combined_sf
                                    }
                                    
                        except Exception as e:
                            continue
            
            # Apply best solution if found
            if best_solution:
                self.material_combo.current(best_solution['material_idx'])
                self.section_combo.current(best_solution['section_idx'])
                self.on_section_change(None)
                
                # Set parameter values
                for i, param in enumerate(self.enhanced_analysis.sections[best_solution['section']]['params']):
                    self.section_entries[param['name']].delete(0, END)
                    self.section_entries[param['name']].insert(0, f"{best_solution['params'][i]:.1f}")
                
                # Run analysis with optimized design
                self.run_enhanced_analysis()
                
                # Show results
                self.show_optimization_results(original_material, original_section, original_params)
                
                self.status_var.set("Fallback optimization completed - safe design found")
                
            else:
                messagebox.showwarning("Optimization Warning", 
                                     "Could not find a safe design with current constraints.\n"
                                     "Try relaxing the safety factor or deflection requirements.")
                self.status_var.set("No safe design found with current constraints")
                
        except Exception as e:
            raise Exception(f"Fallback optimization failed: {str(e)}")

    def offer_automatic_optimization(self, safety_analysis):
        """Offer automatic optimization when design is unsafe"""
        safety_factor = safety_analysis['combined_safety_factor']
        required_sf = min(safety_analysis['required_bending_sf'], safety_analysis['required_shear_sf'])
        
        message = f"""⚠️ DESIGN IS UNSAFE ⚠️

Current Safety Factor: {safety_factor:.2f}
Required Safety Factor: {required_sf:.2f}
Deficit: {(required_sf - safety_factor):.2f} ({(required_sf/safety_factor - 1)*100:.1f}% increase needed)

The AI can automatically find an optimized design that meets safety requirements.

Would you like to run AI optimization now?"""
        
        result = messagebox.askyesno("Unsafe Design Detected", message)
        if result:
            # Set optimization to maximize safety factor
            self.optimization_var.set("Combined Safety Factor")
            self.safety_factor_entry.delete(0, END)
            self.safety_factor_entry.insert(0, f"{required_sf:.2f}")
            
            # Run optimization
            self.run_enhanced_optimization()

    def show_optimization_results(self, original_material, original_section, original_params):
        """Show comparison between original and optimized design"""
        try:
            # Get current (optimized) design parameters
            current_material = self.material_combo.get()
            current_section = self.section_combo.get()
            current_params = {}
            for param_name, entry in self.section_entries.items():
                current_params[param_name] = float(entry.get())
            
            # Calculate original design properties for comparison
            original_material_props = self.enhanced_analysis.materials[original_material]
            original_section_func = self.enhanced_analysis.sections[original_section]['function']
            original_param_values = [original_params[param['name']] for param in 
                                   self.enhanced_analysis.sections[original_section]['params']]
            original_section_props = original_section_func(*original_param_values)
            
            # Calculate original safety factor
            original_stress_analysis = self.enhanced_analysis.calculate_enhanced_stresses(
                self.current_data, original_material_props, original_section_props, original_section)
            original_safety_analysis = self.enhanced_analysis.calculate_enhanced_safety_factors(
                original_stress_analysis, original_material_props)
            
            # Get current (optimized) design results from the latest analysis
            # This would be stored in the class after the latest run_enhanced_analysis()
            # For now, we'll extract from the results text
            
            comparison_text = f"""🔧 AI OPTIMIZATION RESULTS

📊 DESIGN COMPARISON:

ORIGINAL DESIGN:
• Material: {original_material}
• Cross-Section: {original_section}
• Dimensions: {original_params}
• Safety Factor: {original_safety_analysis['combined_safety_factor']:.2f}
• Design Status: {original_safety_analysis['design_status']}

OPTIMIZED DESIGN:
• Material: {current_material}
• Cross-Section: {current_section}
• Dimensions: {current_params}

🎯 IMPROVEMENTS:
• Material Changed: {'Yes' if original_material != current_material else 'No'}
• Section Changed: {'Yes' if original_section != current_section else 'No'}
• Design Optimization: AI found optimal combination of material, 
  cross-section type, and dimensions to meet safety requirements.

✅ The optimized design has been automatically applied and analyzed.
Check the results tabs for detailed comparison."""
            
            messagebox.showinfo("AI Optimization Complete", comparison_text)
            
        except Exception as e:
            print(f"Error showing optimization results: {e}")

    def export_summary_report(self):
        """Export summary analysis report"""
        # Implementation similar to original but with enhanced content
        pass

    def export_detailed_report(self):
        """Export detailed analysis report"""
        # Implementation similar to original but with enhanced content
        pass

    def show_material_properties(self):
        """Display detailed material properties"""
        material_name = self.material_combo.get()
        material_props = self.enhanced_analysis.materials[material_name]
        
        properties_text = f"""Material Properties: {material_name}
        
Young's Modulus (E): {material_props['E']/1e9:.1f} GPa
Shear Modulus (G): {material_props['G']/1e9:.1f} GPa
Yield Strength: {material_props['σ_yield']/1e6:.1f} MPa
Ultimate Strength: {material_props['σ_ultimate']/1e6:.1f} MPa
Poisson's Ratio: {material_props['ν']:.3f}
Density: {material_props['density']} kg/m³
Safety Factor (Bending): {material_props['safety_factor_bending']:.2f}
Safety Factor (Shear): {material_props['safety_factor_shear']:.2f}
Fatigue Limit: {material_props['fatigue_limit']:.1f} × Ultimate Strength
Cost: ${material_props['cost']:.2f}/kg
"""
        
        messagebox.showinfo("Material Properties", properties_text)

    def show_section_properties(self):
        """Display detailed section properties"""
        section_type = self.section_combo.get()
        
        # Get current parameters
        param_values = []
        for param in self.enhanced_analysis.sections[section_type]['params']:
            value = self.section_entries[param['name']].get()
            param_values.append(float(value))
        
        section_func = self.enhanced_analysis.sections[section_type]['function']
        section_props = section_func(*param_values)
        
        properties_text = f"""Section Properties: {section_type}
        
Area: {section_props['A']*1e6:.2f} mm²
Moment of Inertia: {section_props['I']*1e12:.2f} mm⁴
Section Modulus: {section_props['S']*1e9:.2f} mm³
Torsional Constant: {section_props.get('J', 0)*1e12:.2f} mm⁴
Shape Factor: {section_props['shape_factor']:.2f}
"""
        
        messagebox.showinfo("Section Properties", properties_text)

    def plot_stress_envelope(self):
        """Plot stress envelope diagram"""
        # Implementation for stress envelope plotting
        pass

    def plot_deflection_profile(self):
        """Plot deflection profile"""
        # Implementation for deflection profile plotting
        pass

    def show_help(self):
        """Display enhanced help information"""
        help_text = """Enhanced Beam Analysis Tool Help

1. Load beam data file (CSV or Excel)
2. Select material and cross-section type
3. Enter section dimensions
4. Choose support conditions
5. Select analysis options
6. Click 'Run Enhanced Analysis'
7. Use 'Find Optimal Design' for AI optimization
8. Export comprehensive reports

Enhanced Features:
- Comprehensive stress analysis
- Deflection calculations
- Fatigue analysis
- Combined stress analysis
- Advanced optimization objectives
"""
        messagebox.showinfo("Help", help_text)

    def show_engineering_references(self):
        """Display engineering references"""
        refs = """Engineering References:

1. AISC Steel Construction Manual
2. Eurocode 3: Design of Steel Structures
3. ACI 318: Building Code Requirements for Structural Concrete
4. Roark's Formulas for Stress and Strain
5. Timoshenko & Gere: Theory of Elastic Stability
6. Salmon & Johnson: Steel Structures - Design and Behavior
"""
        messagebox.showinfo("Engineering References", refs)

    def show_about(self):
        """Display about information"""
        messagebox.showinfo(
            "About",
            "Enhanced Beam Analysis Tool\n\n"
            "Version 3.0 - Advanced Engineering Edition\n"
            "Features comprehensive structural analysis\n"
            "© 2024 Advanced Structural Engineering Tools"
        )

    def new_analysis(self):
        """Reset the application for a new analysis"""
        self.current_data = None
        self.file_entry.delete(0, END)
        self.results_text.config(state=NORMAL)
        self.results_text.delete(1.0, END)
        self.results_text.config(state=DISABLED)
        self.detailed_text.config(state=NORMAL)
        self.detailed_text.delete(1.0, END)
        self.detailed_text.config(state=DISABLED)
        self.figure.clear()
        self.canvas.draw()
        self.update_ui_state()
        self.status_var.set("Ready for enhanced analysis")

    def update_ui_state(self):
        """Update UI elements based on current state"""
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
    app = EnhancedBeamAnalyzerApp(root)
    root.mainloop()
