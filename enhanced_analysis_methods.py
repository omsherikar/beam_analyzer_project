"""
Enhanced Beam Analysis Methods
Provides more accurate and detailed structural analysis capabilities
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
import math

class EnhancedBeamAnalysis:
    def __init__(self):
        self.materials = self._create_enhanced_material_database()
        self.sections = self._create_enhanced_section_database()
    
    def _create_enhanced_material_database(self) -> Dict:
        """Enhanced material database with comprehensive properties"""
        return {
            'A36 Steel': {
                'E': 200e9,              # Young's modulus (Pa)
                'G': 79.3e9,             # Shear modulus (Pa)
                'σ_yield': 250e6,        # Yield strength (Pa)
                'σ_ultimate': 400e6,     # Ultimate strength (Pa)
                'ν': 0.26,               # Poisson's ratio
                'density': 7850,         # kg/m³
                'safety_factor_bending': 1.67,
                'safety_factor_shear': 1.5,
                'fatigue_limit': 0.4,    # As fraction of ultimate strength
                'cost': 0.5,             # $/kg
                'color': '#FF6B6B'
            },
            'Aluminum 6061-T6': {
                'E': 68.9e9,
                'G': 25.8e9,
                'σ_yield': 276e6,
                'σ_ultimate': 310e6,
                'ν': 0.33,
                'density': 2700,
                'safety_factor_bending': 1.95,
                'safety_factor_shear': 1.8,
                'fatigue_limit': 0.4,
                'cost': 2.0,
                'color': '#4ECDC4'
            },
            'Concrete C30': {
                'E': 30e9,
                'G': 12.5e9,
                'σ_yield': 30e6,         # Compressive strength
                'σ_ultimate': 37.5e6,
                'ν': 0.2,
                'density': 2400,
                'safety_factor_bending': 2.0,
                'safety_factor_shear': 2.5,
                'fatigue_limit': 0.3,
                'cost': 0.1,
                'color': '#C5CBE3'
            },
            'Titanium Grade 5': {
                'E': 113.8e9,
                'G': 42.8e9,
                'σ_yield': 880e6,
                'σ_ultimate': 950e6,
                'ν': 0.33,
                'density': 4430,
                'safety_factor_bending': 1.7,
                'safety_factor_shear': 1.6,
                'fatigue_limit': 0.5,
                'cost': 15.0,
                'color': '#1abc9c'
            }
        }
    
    def _create_enhanced_section_database(self) -> Dict:
        """Enhanced cross-section database with detailed calculations"""
        return {
            'Rectangular': {
                'function': self._calc_rectangular_section,
                'params': [
                    {'name': 'Width', 'unit': 'mm', 'default': 100, 'min': 1},
                    {'name': 'Height', 'unit': 'mm', 'default': 200, 'min': 1}
                ]
            },
            'I-beam': {
                'function': self._calc_I_section,
                'params': [
                    {'name': 'Flange Width', 'unit': 'mm', 'default': 150, 'min': 1},
                    {'name': 'Height', 'unit': 'mm', 'default': 300, 'min': 1},
                    {'name': 'Flange Thickness', 'unit': 'mm', 'default': 15, 'min': 1},
                    {'name': 'Web Thickness', 'unit': 'mm', 'default': 10, 'min': 1}
                ]
            },
            'Circular': {
                'function': self._calc_circular_section,
                'params': [
                    {'name': 'Diameter', 'unit': 'mm', 'default': 150, 'min': 1}
                ]
            },
            'Hollow Circular': {
                'function': self._calc_hollow_circular_section,
                'params': [
                    {'name': 'Outer Diameter', 'unit': 'mm', 'default': 150, 'min': 1},
                    {'name': 'Wall Thickness', 'unit': 'mm', 'default': 10, 'min': 1}
                ]
            },
            'T-beam': {
                'function': self._calc_T_section,
                'params': [
                    {'name': 'Flange Width', 'unit': 'mm', 'default': 200, 'min': 1},
                    {'name': 'Flange Thickness', 'unit': 'mm', 'default': 20, 'min': 1},
                    {'name': 'Web Height', 'unit': 'mm', 'default': 180, 'min': 1},
                    {'name': 'Web Thickness', 'unit': 'mm', 'default': 12, 'min': 1}
                ]
            }
        }
    
    def _calc_rectangular_section(self, width: float, height: float) -> Dict:
        """Calculate properties for rectangular section"""
        w, h = width/1000, height/1000  # Convert to meters
        
        return {
            'A': w * h,                          # Area (m²)
            'I': (w * h**3) / 12,               # Moment of inertia (m⁴)
            'S': (w * h**2) / 6,                # Section modulus (m³)
            'J': w * h**3 * (1 - 0.63*h/w) / 3, # Torsional constant (m⁴)
            'Q_max': (w * h**2) / 8,            # First moment of area (m³)
            'web_area': w * h,                   # For shear calculations
            'shape_factor': 1.5                  # Shape factor for shear
        }
    
    def _calc_I_section(self, bf: float, h: float, tf: float, tw: float) -> Dict:
        """Calculate properties for I-beam section"""
        bf, h, tf, tw = bf/1000, h/1000, tf/1000, tw/1000  # Convert to meters
        
        # Area
        A = 2 * bf * tf + (h - 2*tf) * tw
        
        # Moment of inertia about strong axis
        I = (bf * h**3 - (bf - tw) * (h - 2*tf)**3) / 12
        
        # Section modulus
        S = 2 * I / h
        
        # Torsional constant (approximate)
        J = (2 * bf * tf**3 + (h - 2*tf) * tw**3) / 3
        
        # First moment of area (for shear stress)
        Q_max = bf * tf * (h/2 - tf/2) + tw * (h/2 - tf)**2 / 2
        
        return {
            'A': A,
            'I': I,
            'S': S,
            'J': J,
            'Q_max': Q_max,
            'web_area': (h - 2*tf) * tw,
            'shape_factor': 1.2
        }
    
    def _calc_circular_section(self, d: float) -> Dict:
        """Calculate properties for circular section"""
        d = d/1000  # Convert to meters
        r = d/2
        
        return {
            'A': np.pi * r**2,
            'I': np.pi * d**4 / 64,
            'S': np.pi * d**3 / 32,
            'J': np.pi * d**4 / 32,  # Polar moment of inertia
            'Q_max': 2 * r**3 / 3,
            'web_area': np.pi * r**2,
            'shape_factor': 4/3
        }
    
    def _calc_hollow_circular_section(self, do: float, t: float) -> Dict:
        """Calculate properties for hollow circular section"""
        do, t = do/1000, t/1000  # Convert to meters
        di = do - 2*t
        ro, ri = do/2, di/2
        
        return {
            'A': np.pi * (ro**2 - ri**2),
            'I': np.pi * (do**4 - di**4) / 64,
            'S': np.pi * (do**4 - di**4) / (32 * do),
            'J': np.pi * (do**4 - di**4) / 32,
            'Q_max': 2 * (ro**3 - ri**3) / 3,
            'web_area': np.pi * (ro**2 - ri**2),
            'shape_factor': 4/3
        }
    
    def _calc_T_section(self, bf: float, tf: float, hw: float, tw: float) -> Dict:
        """Calculate properties for T-beam section"""
        bf, tf, hw, tw = bf/1000, tf/1000, hw/1000, tw/1000  # Convert to meters
        
        # Area
        A = bf * tf + hw * tw
        
        # Centroid calculation
        y_bar = (bf * tf * (tf/2) + hw * tw * (tf + hw/2)) / A
        
        # Moment of inertia about centroid
        I = (bf * tf**3 / 12 + bf * tf * (y_bar - tf/2)**2 +
             tw * hw**3 / 12 + hw * tw * (tf + hw/2 - y_bar)**2)
        
        # Section modulus
        S_top = I / (tf + hw - y_bar)
        S_bottom = I / y_bar
        
        return {
            'A': A,
            'I': I,
            'S': min(S_top, S_bottom),  # Use the smaller value
            'S_top': S_top,
            'S_bottom': S_bottom,
            'J': (bf * tf**3 + hw * tw**3) / 3,  # Approximate
            'Q_max': bf * tf * (y_bar - tf/2),
            'web_area': hw * tw,
            'shape_factor': 1.3,
            'centroid': y_bar
        }
    
    def calculate_enhanced_stresses(self, beam_data: pd.DataFrame, 
                                  material_props: Dict, section_props: Dict,
                                  section_type: str) -> Dict:
        """Calculate comprehensive stress analysis"""
        
        # Extract beam data
        x = beam_data['Distance (m)'].values
        sf = beam_data['SF (kN)'].values
        bm = beam_data['BM (kN-m)'].values
        
        # Convert to base units (N, N-m)
        sf_n = sf * 1000
        bm_nm = bm * 1000
        
        # Maximum values
        max_bm = np.max(np.abs(bm_nm))
        max_sf = np.max(np.abs(sf_n))
        
        # Bending stress (σ = M/S)
        bending_stress_max = max_bm / section_props['S']
        
        # Shear stress (τ = VQ/It for I-beams, τ = 4V/3A for rectangular)
        if section_type in ['I-beam', 'T-beam']:
            shear_stress_max = (max_sf * section_props['Q_max']) / (
                section_props['I'] * section_props.get('web_thickness', 0.01))
        else:
            shear_stress_max = (max_sf * section_props['shape_factor']) / section_props['A']
        
        # Principal stresses (for combined loading)
        principal_stresses = self._calculate_principal_stresses(
            bending_stress_max, shear_stress_max)
        
        # Von Mises equivalent stress
        von_mises_stress = np.sqrt(bending_stress_max**2 + 3*shear_stress_max**2)
        
        # Stress concentrations (simplified)
        stress_concentration_bending = 1.0  # Can be enhanced based on geometry
        stress_concentration_shear = 1.0
        
        # Fatigue analysis
        fatigue_analysis = self._fatigue_analysis(
            beam_data, material_props, section_props)
        
        return {
            'bending_stress_max': bending_stress_max,
            'shear_stress_max': shear_stress_max,
            'von_mises_stress': von_mises_stress,
            'principal_stresses': principal_stresses,
            'stress_concentration_bending': stress_concentration_bending,
            'stress_concentration_shear': stress_concentration_shear,
            'fatigue_analysis': fatigue_analysis,
            'max_bending_moment': max_bm,
            'max_shear_force': max_sf
        }
    
    def _calculate_principal_stresses(self, σx: float, τxy: float) -> Dict:
        """Calculate principal stresses"""
        σ1 = σx/2 + np.sqrt((σx/2)**2 + τxy**2)
        σ2 = σx/2 - np.sqrt((σx/2)**2 + τxy**2)
        τmax = np.sqrt((σx/2)**2 + τxy**2)
        
        return {
            'σ1': σ1,
            'σ2': σ2,
            'τmax': τmax,
            'angle': np.arctan(2*τxy/σx) * 180/np.pi / 2
        }
    
    def _fatigue_analysis(self, beam_data: pd.DataFrame, 
                         material_props: Dict, section_props: Dict) -> Dict:
        """Perform fatigue analysis"""
        
        # Extract stress ranges
        bm = beam_data['BM (kN-m)'].values * 1000  # Convert to N-m
        sf = beam_data['SF (kN)'].values * 1000    # Convert to N
        
        # Calculate stress ranges
        bending_stresses = bm / section_props['S']
        shear_stresses = sf / section_props['A'] * section_props['shape_factor']
        
        # Find stress ranges
        σ_range = np.max(bending_stresses) - np.min(bending_stresses)
        τ_range = np.max(shear_stresses) - np.min(shear_stresses)
        
        # Modified Goodman criterion for combined stresses
        σ_mean = (np.max(bending_stresses) + np.min(bending_stresses)) / 2
        τ_mean = (np.max(shear_stresses) + np.min(shear_stresses)) / 2
        
        # Fatigue strength
        σ_fatigue = material_props['fatigue_limit'] * material_props['σ_ultimate']
        
        # Safety factor for fatigue
        fatigue_sf = σ_fatigue / np.sqrt(σ_range**2 + 3*τ_range**2)
        
        return {
            'stress_range_bending': σ_range,
            'stress_range_shear': τ_range,
            'mean_stress_bending': σ_mean,
            'mean_stress_shear': τ_mean,
            'fatigue_strength': σ_fatigue,
            'fatigue_safety_factor': fatigue_sf,
            'cycles_to_failure': self._estimate_fatigue_life(σ_range, material_props)
        }
    
    def _estimate_fatigue_life(self, stress_range: float, material_props: Dict) -> float:
        """Estimate fatigue life using simplified S-N curve"""
        σ_fatigue = material_props['fatigue_limit'] * material_props['σ_ultimate']
        
        # Simplified Basquin equation: σ = σ_fatigue * (N/N0)^(-1/b)
        # Where b ≈ 0.1 for steel, N0 = 10^6 cycles
        b = 0.1
        N0 = 1e6
        
        if stress_range <= σ_fatigue:
            return float('inf')  # Infinite life
        else:
            return N0 * (σ_fatigue / stress_range)**(1/b)
    
    def calculate_deflections(self, beam_data: pd.DataFrame, 
                            material_props: Dict, section_props: Dict,
                            support_conditions: str = 'simply_supported') -> Dict:
        """Calculate beam deflections using numerical integration"""
        
        x = beam_data['Distance (m)'].values
        bm = beam_data['BM (kN-m)'].values * 1000  # Convert to N-m
        L = x[-1] - x[0]
        
        # Curvature: κ = M/(EI)
        curvature = bm / (material_props['E'] * section_props['I'])
        
        # Numerical integration for deflection
        deflections = np.zeros_like(x)
        
        # For simply supported beam with point loads
        if support_conditions == 'simply_supported':
            # Use superposition of standard cases
            deflections = self._simply_supported_deflection(x, bm, material_props, section_props)
        
        # Maximum deflection
        max_deflection = np.max(np.abs(deflections))
        max_deflection_location = x[np.argmax(np.abs(deflections))]
        
        # Deflection limits (typically L/250 for live loads, L/300 for total)
        deflection_limit_live = L / 250
        deflection_limit_total = L / 300
        
        return {
            'deflections': deflections,
            'max_deflection': max_deflection,
            'max_deflection_location': max_deflection_location,
            'deflection_limit_live': deflection_limit_live,
            'deflection_limit_total': deflection_limit_total,
            'deflection_ratio': max_deflection / deflection_limit_total
        }
    
    def _simply_supported_deflection(self, x: np.ndarray, bm: np.ndarray,
                                   material_props: Dict, section_props: Dict) -> np.ndarray:
        """Calculate deflection for simply supported beam"""
        
        L = x[-1] - x[0]
        EI = material_props['E'] * section_props['I']
        
        # Use moment-area method for deflection calculation
        # For distributed moment, deflection at point x:
        # v(x) = (1/EI) * ∫∫M(x)dx dx
        
        deflections = np.zeros_like(x)
        
        # Simplified calculation using Simpson's rule
        for i, xi in enumerate(x):
            # Calculate deflection at point xi
            integral = 0
            for j in range(i):
                # Trapezoidal rule for double integration
                if j > 0:
                    h = x[j] - x[j-1]
                    integral += h * (bm[j-1] + bm[j]) / 2
            
            # Second integration
            second_integral = 0
            for k in range(i):
                if k > 0:
                    h = x[k] - x[k-1]
                    second_integral += h * (integral if k == i-1 else 0)
            
            deflections[i] = second_integral / EI
        
        return deflections
    
    def calculate_enhanced_safety_factors(self, stress_analysis: Dict, 
                                        material_props: Dict) -> Dict:
        """Calculate comprehensive safety factors"""
        
        # Bending safety factor
        bending_sf = material_props['σ_yield'] / stress_analysis['bending_stress_max']
        
        # Shear safety factor
        shear_sf = (material_props['σ_yield'] / np.sqrt(3)) / stress_analysis['shear_stress_max']
        
        # Von Mises safety factor
        von_mises_sf = material_props['σ_yield'] / stress_analysis['von_mises_stress']
        
        # Fatigue safety factor
        fatigue_sf = stress_analysis['fatigue_analysis']['fatigue_safety_factor']
        
        # Combined safety factor (conservative approach)
        combined_sf = min(bending_sf, shear_sf, von_mises_sf, fatigue_sf)
        
        # Required safety factors
        required_sf_bending = material_props['safety_factor_bending']
        required_sf_shear = material_props['safety_factor_shear']
        
        return {
            'bending_safety_factor': bending_sf,
            'shear_safety_factor': shear_sf,
            'von_mises_safety_factor': von_mises_sf,
            'fatigue_safety_factor': fatigue_sf,
            'combined_safety_factor': combined_sf,
            'required_bending_sf': required_sf_bending,
            'required_shear_sf': required_sf_shear,
            'design_status': 'SAFE' if combined_sf >= min(required_sf_bending, required_sf_shear) else 'UNSAFE'
        }
    
    def generate_detailed_report(self, beam_data: pd.DataFrame, 
                               material_props: Dict, section_props: Dict,
                               stress_analysis: Dict, deflection_analysis: Dict,
                               safety_analysis: Dict) -> str:
        """Generate comprehensive analysis report"""
        
        report = f"""
COMPREHENSIVE BEAM ANALYSIS REPORT
{'='*60}

MATERIAL PROPERTIES:
- Material: {material_props.get('name', 'Unknown')}
- Young's Modulus: {material_props['E']/1e9:.1f} GPa
- Shear Modulus: {material_props['G']/1e9:.1f} GPa
- Yield Strength: {material_props['σ_yield']/1e6:.1f} MPa
- Ultimate Strength: {material_props['σ_ultimate']/1e6:.1f} MPa
- Density: {material_props['density']} kg/m³

SECTION PROPERTIES:
- Area: {section_props['A']*1e6:.2f} mm²
- Moment of Inertia: {section_props['I']*1e12:.2f} mm⁴
- Section Modulus: {section_props['S']*1e9:.2f} mm³
- Torsional Constant: {section_props.get('J', 0)*1e12:.2f} mm⁴

STRESS ANALYSIS:
- Maximum Bending Stress: {stress_analysis['bending_stress_max']/1e6:.2f} MPa
- Maximum Shear Stress: {stress_analysis['shear_stress_max']/1e6:.2f} MPa
- Von Mises Stress: {stress_analysis['von_mises_stress']/1e6:.2f} MPa
- Principal Stress σ1: {stress_analysis['principal_stresses']['σ1']/1e6:.2f} MPa
- Principal Stress σ2: {stress_analysis['principal_stresses']['σ2']/1e6:.2f} MPa

DEFLECTION ANALYSIS:
- Maximum Deflection: {deflection_analysis['max_deflection']*1000:.2f} mm
- Deflection Limit (L/300): {deflection_analysis['deflection_limit_total']*1000:.2f} mm
- Deflection Ratio: {deflection_analysis['deflection_ratio']:.3f}

SAFETY FACTORS:
- Bending Safety Factor: {safety_analysis['bending_safety_factor']:.2f} (Required: {safety_analysis['required_bending_sf']:.2f})
- Shear Safety Factor: {safety_analysis['shear_safety_factor']:.2f} (Required: {safety_analysis['required_shear_sf']:.2f})
- Von Mises Safety Factor: {safety_analysis['von_mises_safety_factor']:.2f}
- Fatigue Safety Factor: {safety_analysis['fatigue_safety_factor']:.2f}
- Combined Safety Factor: {safety_analysis['combined_safety_factor']:.2f}

FATIGUE ANALYSIS:
- Stress Range: {stress_analysis['fatigue_analysis']['stress_range_bending']/1e6:.2f} MPa
- Estimated Fatigue Life: {stress_analysis['fatigue_analysis']['cycles_to_failure']:.0e} cycles

DESIGN STATUS: {safety_analysis['design_status']}
"""
        return report
