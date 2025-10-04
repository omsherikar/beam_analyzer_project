# Beam Analysis Tool with AI Optimization

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

A comprehensive application for structural engineers that combines traditional beam analysis with AI-powered optimization capabilities. Available in both desktop GUI and web-based Streamlit versions.

## Table of Contents
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [File Format](#file-format)
- [Optimization](#optimization)
- [Project Structure](#project-structure)
- [Examples](#examples)
- [Limitations](#limitations)
- [License](#license)
- [Support](#support)

## Features

### 1. Beam Analysis
- Load beam data from CSV or Excel files
- Calculate shear forces and bending moments
- Visualize results with interactive diagrams
- Evaluate multiple material and cross-section options

### 2. AI-Powered Optimization
- Genetic algorithm-based design optimization
- Multiple optimization objectives:
  - Cost minimization
  - Weight reduction
  - Deflection control
  - Safety factor maximization
- Customizable constraints:
  - Maximum allowable deflection
  - Minimum required safety factor

### 3. Material Library
Preloaded with common engineering materials:
- A36 Steel
- Aluminum 6061
- Concrete
- Titanium Grade 5 (Streamlit version)

Material properties including:
- Young's Modulus
- Yield Strength
- Cost factors
- Recommended safety factors
- Density

### 4. Cross-Section Analysis
Supported cross-sections:
- Rectangular
- I-beam
- Circular
- Hollow Circular (Streamlit version)

Automatic calculation of:
- Area
- Moment of Inertia
- Section Modulus

### 5. Reporting
- Generate PDF reports with:
  - Analysis results
  - Diagrams
  - Design recommendations
- Export functionality for sharing results

## System Requirements
- **Python**: 3.7 or higher
- **OS**: Windows, macOS, or Linux
- **Recommended**:
  - 4GB RAM
  - 2GHz processor

## Installation

1. Clone or download the project:
   ```bash
   git clone <repository-url>
   cd beam_analyzer_project
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The project provides two interfaces:

### Desktop GUI Application
Run the desktop application with:
```bash
python run_gui.py
```

Features:
- Traditional desktop interface using Tkinter
- AI-powered optimization with genetic algorithms
- Interactive plotting with matplotlib
- PDF report generation

### Web-based Streamlit Application
Run the web application with:
```bash
python run_streamlit.py
```

Or directly with Streamlit:
```bash
streamlit run beam_analyzer_gui_03.py
```

Features:
- Modern web interface
- Enhanced visualization
- Better user experience
- Responsive design

### Basic Workflow

1. **Load Data**: Upload a CSV or Excel file containing beam analysis data
2. **Select Material**: Choose from the predefined material library
3. **Choose Cross-Section**: Select the beam cross-section type and enter dimensions
4. **Run Analysis**: Calculate stresses and safety factors
5. **View Results**: Review analysis results and diagrams
6. **Optimize Design** (GUI only): Use AI optimization to find the best design
7. **Export Report**: Generate PDF reports for documentation

## File Format

Your beam data file should contain three columns:

| Column Name | Description | Units |
|-------------|-------------|-------|
| Distance (m) | Position along the beam | meters |
| SF (kN) | Shear force at each point | kilonewtons |
| BM (kN-m) | Bending moment at each point | kilonewton-meters |

**Example CSV format:**
```csv
Distance (m),SF (kN),BM (kN-m)
0.0,25.0,0.0
0.5,25.0,12.5
1.0,25.0,25.0
1.5,25.0,37.5
2.0,25.0,50.0
```

## Optimization

The AI optimization feature (available in the GUI version) uses genetic algorithms to find optimal beam designs based on:

- **Objectives**: Cost, Weight, Deflection, or Safety Factor
- **Constraints**: Maximum deflection and minimum safety factor
- **Variables**: Material type, cross-section type, and dimensions

The optimization process typically takes 1-3 minutes depending on the complexity.

## Project Structure

```
beam_analyzer_project/
├── beam_analyzer_ai.py          # Desktop GUI application
├── beam_analyzer_gui_03.py      # Streamlit web application
├── run_gui.py                   # GUI launcher script
├── run_streamlit.py             # Streamlit launcher script
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── data/                        # Sample data files
│   ├── sample_beam_data.csv
│   └── simply_supported_beam.csv
├── docs/                        # Documentation (future)
├── samples/                     # Additional examples (future)
└── venv/                        # Virtual environment
```

## Examples

Sample data files are provided in the `data/` directory:

- `sample_beam_data.csv`: Example beam with varying loads
- `simply_supported_beam.csv`: Simply supported beam with point load

To test the applications:

1. Start either the GUI or Streamlit app
2. Load one of the sample files
3. Select a material (e.g., A36 Steel)
4. Choose a cross-section (e.g., Rectangular)
5. Enter reasonable dimensions (e.g., 100mm width, 200mm height)
6. Run the analysis

## Limitations

- Optimization is only available in the desktop GUI version
- Some advanced features may vary between versions
- Large datasets may require more processing time
- Genetic algorithm optimization may take several minutes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions:
1. Check the documentation
2. Review sample data files
3. Test with provided examples
4. Create an issue for bugs or feature requests
