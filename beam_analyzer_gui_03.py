import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import tempfile
import base64
import os
from io import BytesIO

# Set page configuration with wider layout and custom theme
st.set_page_config(
    page_title="Beam Analysis Pro",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
def apply_custom_styles():
    st.markdown("""
    <style>
        /* Main container */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #2c3e50;
            color: white;
        }
        
        /* Sidebar text */
        [data-testid="stSidebar"] .stMarkdown {
            color: white;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: #3498db;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #2980b9;
            transform: translateY(-1px);
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] {
            border: 2px dashed #7f8c8d;
            border-radius: 5px;
            padding: 1rem;
        }
        
        /* Tabs */
        .stTabs [role="tablist"] {
            background-color: #ecf0f1;
            border-radius: 5px;
        }
        
        /* Cards */
        .card {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        /* Results highlight */
        .result-highlight {
            font-size: 1.1rem;
            font-weight: bold;
            color: #2c3e50;
        }
        
        /* Safe/Unsafe indicators */
        .safe {
            color: #27ae60;
        }
        
        .unsafe {
            color: #e74c3c;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'section_params' not in st.session_state:
        st.session_state.section_params = {}

# Material database
def create_material_database():
    materials = {
        'A36 Steel': {
            'E': 200e9,          # Young's modulus (Pa)
            'σ_yield': 250e6,    # Yield strength (Pa)
            'color': '#e74c3c',   # Display color
            'safety_factor': 1.5, # Recommended safety factor
            'cost': 0.5,          # Cost ($/kg)
            'density': 7850       # kg/m³
        },
        'Aluminum 6061': {
            'E': 68.9e9,
            'σ_yield': 276e6,
            'color': '#3498db',
            'safety_factor': 1.8,
            'cost': 2.0,
            'density': 2700
        },
        'Concrete': {
            'E': 30e9,
            'σ_yield': 30e6,
            'color': '#95a5a6',
            'safety_factor': 2.0,
            'cost': 0.1,
            'density': 2400
        },
        'Titanium Grade 5': {
            'E': 113.8e9,
            'σ_yield': 880e6,
            'color': '#1abc9c',
            'safety_factor': 1.7,
            'cost': 15.0,
            'density': 4430
        }
    }
    return materials

# Section database with calculation methods
def create_section_database():
    sections = {
        'Rectangular': {
            'function': 'rectangular',
            'params': [
                {'name': 'Width', 'unit': 'mm', 'default': 100, 'min': 1},
                {'name': 'Height', 'unit': 'mm', 'default': 200, 'min': 1}
            ],
            'icon': '⬜'
        },
        'I-beam': {
            'function': 'I_section',
            'params': [
                {'name': 'Width', 'unit': 'mm', 'default': 150, 'min': 1},
                {'name': 'Height', 'unit': 'mm', 'default': 300, 'min': 1},
                {'name': 'Flange Thickness', 'unit': 'mm', 'default': 15, 'min': 1},
                {'name': 'Web Thickness', 'unit': 'mm', 'default': 10, 'min': 1}
            ],
            'icon': '⏹️'
        },
        'Circular': {
            'function': 'circular',
            'params': [
                {'name': 'Diameter', 'unit': 'mm', 'default': 150, 'min': 1}
            ],
            'icon': '⭕'
        },
        'Hollow Circular': {
            'function': 'hollow_circular',
            'params': [
                {'name': 'Outer Diameter', 'unit': 'mm', 'default': 150, 'min': 1},
                {'name': 'Wall Thickness', 'unit': 'mm', 'default': 10, 'min': 1}
            ],
            'icon': '⭕'
        }
    }
    return sections

# Section property calculations
def calculate_section_properties(section_type, params):
    # Convert all parameters to float and millimeters to meters
    params = {k: float(v)/1000 for k, v in params.items()}
    
    if section_type == 'Rectangular':
        width = params['Width']
        height = params['Height']
        area = width * height
        I = (width * height**3)/12
        S = I / (height/2)
    elif section_type == 'I-beam':
        w = params['Width']
        h = params['Height']
        tf = params['Flange Thickness']
        tw = params['Web Thickness']
        area = (2 * w * tf) + ((h - 2*tf) * tw)
        I = (w * h**3)/12 - ((w-tw)*(h-2*tf)**3)/12
        S = I / (h/2)
    elif section_type == 'Circular':
        d = params['Diameter']
        area = np.pi * (d/2)**2
        I = np.pi * (d**4)/64
        S = I / (d/2)
    elif section_type == 'Hollow Circular':
        d_out = params['Outer Diameter']
        t = params['Wall Thickness']
        d_in = d_out - 2*t
        area = np.pi/4 * (d_out**2 - d_in**2)
        I = np.pi/64 * (d_out**4 - d_in**4)
        S = I / (d_out/2)
    
    return {'A': area, 'I': I, 'S': S}

# File processing with enhanced validation
def process_uploaded_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Case-insensitive column matching
        df.columns = df.columns.str.strip()
        col_mapping = {
            'distance': ['distance', 'length', 'position', 'x'],
            'shear': ['shear', 'sf', 'shear force'],
            'moment': ['moment', 'bm', 'bending moment']
        }
        
        # Find matching columns
        distance_col = None
        shear_col = None
        moment_col = None
        
        for col in df.columns:
            lower_col = col.lower()
            if any(x in lower_col for x in col_mapping['distance']):
                distance_col = col
            elif any(x in lower_col for x in col_mapping['shear']):
                shear_col = col
            elif any(x in lower_col for x in col_mapping['moment']):
                moment_col = col
        
        if not all([distance_col, shear_col, moment_col]):
            raise ValueError("Could not identify required columns in the file")
        
        # Standardize column names
        df = df.rename(columns={
            distance_col: 'Distance (m)',
            shear_col: 'SF (kN)',
            moment_col: 'BM (kN-m)'
        })
        
        # Convert to numeric and drop NA
        df['Distance (m)'] = pd.to_numeric(df['Distance (m)'], errors='coerce')
        df['SF (kN)'] = pd.to_numeric(df['SF (kN)'], errors='coerce')
        df['BM (kN-m)'] = pd.to_numeric(df['BM (kN-m)'], errors='coerce')
        df = df.dropna()
        
        if df.empty:
            raise ValueError("No valid data found after processing")
        
        return df
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

# Enhanced results display with tabs
def display_results(results):
    with st.container():
        st.subheader("📊 Analysis Results")
        
        tab1, tab2, tab3 = st.tabs(["Summary", "Detailed Results", "Visualization"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📐 Design Parameters")
                st.markdown(f"""
                - **Material:** {results['material']}
                - **Cross-Section:** {results['section_type']}
                - **Section Area:** {results['section_props']['A']*1e6:.2f} mm²
                - **Moment of Inertia:** {results['section_props']['I']*1e12:.2f} mm⁴
                """)
                
                st.markdown("### 📈 Maximum Values")
                st.markdown(f"""
                - **Bending Moment:** {results['max_bm']:.2f} kN-m
                - **Shear Force:** {results['max_sf']:.2f} kN
                """)
            
            with col2:
                st.markdown("### ⚖️ Stress Analysis")
                st.markdown(f"""
                - **Bending Stress:** {results['bending_stress']/1e6:.2f} MPa
                - **Shear Stress:** {results['shear_stress']/1e6:.2f} MPa
                """)
                
                st.markdown("### 🛡️ Safety Factors")
                st.markdown(f"""
                - **Bending:** {results['bending_sf']:.2f} (Required: {results['required_sf']:.1f})
                - **Shear:** {results['shear_sf']:.2f}
                """)
                
                # Design status with emoji
                if results['bending_sf'] >= results['required_sf']:
                    st.success("✅ **DESIGN STATUS: SAFE**")
                else:
                    st.error("❌ **DESIGN STATUS: UNSAFE**")
        
        with tab2:
            st.markdown("### 📝 Detailed Calculations")
            
            # Material properties
            with st.expander("Material Properties"):
                st.table(pd.DataFrame.from_dict(results['material_props'], orient='index'))
            
            # Section properties
            with st.expander("Section Properties"):
                section_df = pd.DataFrame({
                    'Property': ['Area', 'Moment of Inertia', 'Section Modulus'],
                    'Value': [
                        f"{results['section_props']['A']:.6f} m²",
                        f"{results['section_props']['I']:.6f} m⁴",
                        f"{results['section_props']['S']:.6f} m³"
                    ],
                    'Value (mm)': [
                        f"{results['section_props']['A']*1e6:.2f} mm²",
                        f"{results['section_props']['I']*1e12:.2f} mm⁴",
                        f"{results['section_props']['S']*1e9:.2f} mm³"
                    ]
                })
                st.table(section_df)
            
            # Stress calculations
            with st.expander("Stress Calculations"):
                st.markdown(f"""
                **Bending Stress (σ):**
                ```
                σ = M / S
                  = {results['max_bm']} kN-m / {results['section_props']['S']:.6f} m³
                  = {results['bending_stress']/1e6:.2f} MPa
                ```
                
                **Shear Stress (τ):**
                ```
                τ = V / A
                  = {results['max_sf']} kN / {results['section_props']['A']:.6f} m²
                  = {results['shear_stress']/1e6:.2f} MPa
                ```
                """)
        
        with tab3:
            st.markdown("### 📊 Beam Diagrams")
            plot_diagrams(
                results['x'],
                results['sf'],
                results['bm'],
                results['color']
            )

# Enhanced plotting with annotations
def plot_diagrams(x, sf, bm, color):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), dpi=100)
    
    # Shear Force Diagram
    ax1.plot(x, sf, color=color, linewidth=2.5, label='Shear Force')
    ax1.fill_between(x, sf, color=color, alpha=0.2)
    
    # Annotate max/min points
    max_sf_idx = np.argmax(sf)
    min_sf_idx = np.argmin(sf)
    ax1.annotate(f'Max: {sf[max_sf_idx]:.1f} kN', 
                xy=(x[max_sf_idx], sf[max_sf_idx]),
                xytext=(10, 10), textcoords='offset points',
                arrowprops=dict(arrowstyle="->"))
    ax1.annotate(f'Min: {sf[min_sf_idx]:.1f} kN', 
                xy=(x[min_sf_idx], sf[min_sf_idx]),
                xytext=(10, -20), textcoords='offset points',
                arrowprops=dict(arrowstyle="->"))
    
    ax1.set_title('Shear Force Diagram (SFD)', fontsize=14, pad=20)
    ax1.set_ylabel('Shear Force (kN)', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()
    
    # Bending Moment Diagram
    ax2.plot(x, bm, color=color, linewidth=2.5, label='Bending Moment')
    ax2.fill_between(x, bm, color=color, alpha=0.2)
    
    # Annotate max/min points
    max_bm_idx = np.argmax(bm)
    min_bm_idx = np.argmin(bm)
    ax2.annotate(f'Max: {bm[max_bm_idx]:.1f} kN-m', 
                xy=(x[max_bm_idx], bm[max_bm_idx]),
                xytext=(10, 10), textcoords='offset points',
                arrowprops=dict(arrowstyle="->"))
    ax2.annotate(f'Min: {bm[min_bm_idx]:.1f} kN-m', 
                xy=(x[min_bm_idx], bm[min_bm_idx]),
                xytext=(10, -20), textcoords='offset points',
                arrowprops=dict(arrowstyle="->"))
    
    ax2.set_title('Bending Moment Diagram (BMD)', fontsize=14, pad=20)
    ax2.set_xlabel('Distance along beam (m)', fontsize=12)
    ax2.set_ylabel('Bending Moment (kN-m)', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend()
    
    plt.tight_layout()
    st.pyplot(fig)
    return fig

# Enhanced PDF report with cover page
def create_pdf_report(results, plot_fig):
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    plot_path = os.path.join(temp_dir, "beam_diagrams.png")
    
    # Save plot image
    plot_fig.savefig(plot_path, dpi=150, bbox_inches='tight')
    
    # Create PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Cover page
    pdf.add_page()
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 40, "Beam Analysis Report", 0, 1, 'C')
    pdf.ln(20)
    
    pdf.set_font("Arial", '', 16)
    pdf.cell(0, 10, f"Material: {results['material']}", 0, 1, 'C')
    pdf.cell(0, 10, f"Cross-Section: {results['section_type']}", 0, 1, 'C')
    pdf.ln(20)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    
    # Results page
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Analysis Results Summary", 0, 1)
    pdf.ln(10)
    
    pdf.set_font("Arial", '', 12)
    
    # Design Parameters
    pdf.cell(0, 10, "Design Parameters:", 0, 1)
    pdf.cell(0, 7, f"- Material: {results['material']}", 0, 1)
    pdf.cell(0, 7, f"- Cross-Section: {results['section_type']}", 0, 1)
    pdf.ln(5)
    
    # Maximum Values
    pdf.cell(0, 10, "Maximum Values:", 0, 1)
    pdf.cell(0, 7, f"- Bending Moment: {results['max_bm']:.2f} kN-m", 0, 1)
    pdf.cell(0, 7, f"- Shear Force: {results['max_sf']:.2f} kN", 0, 1)
    pdf.ln(5)
    
    # Stress Analysis
    pdf.cell(0, 10, "Stress Analysis:", 0, 1)
    pdf.cell(0, 7, f"- Bending Stress: {results['bending_stress']/1e6:.2f} MPa", 0, 1)
    pdf.cell(0, 7, f"- Shear Stress: {results['shear_stress']/1e6:.2f} MPa", 0, 1)
    pdf.ln(5)
    
    # Safety Factors
    pdf.cell(0, 10, "Safety Factors:", 0, 1)
    pdf.cell(0, 7, f"- Bending: {results['bending_sf']:.2f} (Required: {results['required_sf']:.1f})", 0, 1)
    pdf.cell(0, 7, f"- Shear: {results['shear_sf']:.2f}", 0, 1)
    pdf.ln(10)
    
    # Design Status
    pdf.set_font("Arial", 'B', 14)
    if results['bending_sf'] >= results['required_sf']:
        pdf.set_text_color(0, 128, 0)  # Green
        pdf.cell(0, 10, "DESIGN STATUS: SAFE", 0, 1)
    else:
        pdf.set_text_color(255, 0, 0)  # Red
        pdf.cell(0, 10, "DESIGN STATUS: UNSAFE", 0, 1)
    
    # Reset text color
    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)
    
    # Add plot image
    pdf.image(plot_path, x=10, w=190)
    
    # Generate PDF bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    
    # Clean up
    try:
        os.remove(plot_path)
        os.rmdir(temp_dir)
    except:
        pass
    
    return pdf_bytes

# Main application
def main():
    # Apply custom styles
    apply_custom_styles()
    
    # Initialize session state
    initialize_session_state()
    
    # Load databases
    materials = create_material_database()
    sections = create_section_database()
    
    # Sidebar - Controls
    with st.sidebar:
        st.title("Beam Analysis Pro")
        st.markdown("""
        <div style="color: white; margin-bottom: 20px;">
            <p>Analyze beam structures with various materials and cross-sections.</p>
            <p><strong>Instructions:</strong></p>
            <ol>
                <li>Upload beam data</li>
                <li>Select material</li>
                <li>Choose cross-section</li>
                <li>Enter dimensions</li>
                <li>Run analysis</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload
        st.subheader("📁 Beam Data")
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            key="file_uploader",
            help="File should contain columns for Distance, Shear Force, and Bending Moment"
        )
        
        if uploaded_file is not None:
            st.session_state.current_data = process_uploaded_file(uploaded_file)
            if st.session_state.current_data is not None:
                st.success("File loaded successfully!")
        
        # Material selection
        st.subheader("🧱 Material Properties")
        material = st.selectbox(
            "Select Material",
            options=list(materials.keys()),
            index=0,
            key="material_select",
            help="Choose the material for your beam analysis"
        )
        
        # Display material properties
        with st.expander("Material Properties"):
            mat_props = materials[material]
            st.markdown(f"""
            - **Young's Modulus (E):** {mat_props['E']/1e9:.1f} GPa
            - **Yield Strength (σ_y):** {mat_props['σ_yield']/1e6:.1f} MPa
            - **Density:** {mat_props['density']} kg/m³
            - **Safety Factor:** {mat_props['safety_factor']}
            """)
        
        # Section selection
        st.subheader("📐 Cross-Section Properties")
        section_type = st.selectbox(
            "Select Cross-Section Type",
            options=list(sections.keys()),
            index=0,
            key="section_select",
            format_func=lambda x: f"{sections[x]['icon']} {x}",
            help="Choose the cross-section shape for your beam"
        )
        
        # Section parameters
        st.markdown("**Section Dimensions**")
        section_params = {}
        for param in sections[section_type]['params']:
            section_params[param['name']] = st.number_input(
                f"{param['name']} ({param['unit']})",
                min_value=float(param['min']),
                value=float(param['default']),
                step=1.0,
                key=f"section_param_{param['name']}"
            )
        
        # Analysis button
        if st.button("🚀 Run Analysis", use_container_width=True, type="primary"):
            if st.session_state.current_data is None:
                st.error("Please upload beam data first")
            else:
                with st.spinner("Performing analysis..."):
                    try:
                        # Get material properties
                        material_props = materials[material]
                        
                        # Calculate section properties
                        section_props = calculate_section_properties(section_type, section_params)
                        
                        # Get beam data
                        x = st.session_state.current_data['Distance (m)'].values
                        sf = st.session_state.current_data['SF (kN)'].values
                        bm = st.session_state.current_data['BM (kN-m)'].values
                        
                        # Calculate stresses (convert kN to N)
                        max_bm = np.max(np.abs(bm))
                        max_sf = np.max(np.abs(sf))
                        
                        bending_stress = (max_bm * 1000) / section_props['S']  # Pa
                        shear_stress = (max_sf * 1000) / section_props['A']    # Pa
                        
                        # Calculate safety factors
                        bending_sf = material_props['σ_yield'] / bending_stress
                        shear_sf = material_props['σ_yield'] / (shear_stress * 1.5)  # Approximate
                        
                        # Store results
                        st.session_state.results = {
                            'material': material,
                            'section_type': section_type,
                            'section_props': section_props,
                            'material_props': material_props,
                            'max_bm': max_bm,
                            'max_sf': max_sf,
                            'bending_stress': bending_stress,
                            'shear_stress': shear_stress,
                            'bending_sf': bending_sf,
                            'shear_sf': shear_sf,
                            'required_sf': material_props['safety_factor'],
                            'x': x,
                            'sf': sf,
                            'bm': bm,
                            'color': material_props['color']
                        }
                        
                        st.success("Analysis completed successfully!")
                    
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
        
        # Export button
        if st.session_state.results is not None:
            st.download_button(
                label="📤 Export Report as PDF",
                data=create_pdf_report(
                    st.session_state.results,
                    plot_diagrams(
                        st.session_state.results['x'],
                        st.session_state.results['sf'],
                        st.session_state.results['bm'],
                        st.session_state.results['color']
                    )
                ),
                file_name=f"beam_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    
    # Main content area
    st.title("Beam Analysis Pro")
    
    if st.session_state.results is not None:
        # Display results
        display_results(st.session_state.results)
    else:
        # Welcome message and instructions
        st.info("""
        ### Welcome to Beam Analysis Pro!
        
        To get started:
        1. Upload your beam data file (CSV or Excel) in the sidebar
        2. Select the material and cross-section type
        3. Enter the section dimensions
        4. Click "Run Analysis"
        
        The tool will calculate stresses and safety factors for your beam design.
        """)
        
        # Example data download
        st.markdown("### Need example data?")
        example_data = pd.DataFrame({
            'Distance (m)': np.linspace(0, 5, 51),
            'SF (kN)': 50 * np.sin(np.linspace(0, np.pi, 51)),
            'BM (kN-m)': 100 * (1 - np.cos(np.linspace(0, np.pi, 51)))
        })
        
        csv = example_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Example CSV",
            data=csv,
            file_name="beam_example_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
