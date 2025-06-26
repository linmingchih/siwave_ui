# SIwave PI Simulation Agent

## Overview
This agent automates the workflow for Power Integrity (PI) simulation using Ansys SIwave. It helps engineers run a complete analysis flow — from loading the layout to generating simulation reports and SPICE models — through a unified UI interface.

## Goals
- Automate layout loading, stackup check, and net selection.
- Set up and run PI simulations with minimal manual input.
- Generate reports and S-parameter/SPICE models.
- Enable extension via scripting (e.g., PyAEDT).

## Key Tasks
- Load layout file (e.g., .aedb, .brd)
- Check and display stackup configuration
- Select power/ground nets
- Assign decap capacitor models
- Set simulation frequency range
- Auto-generate ports for power nets
- Launch simulation and monitor progress
- Export S-parameter results and SPICE model
- Present plots and summary data in UI

## Agent Capabilities
- Interface with PyAEDT and SIwave COM API
- Support input/output validation (e.g., missing nets, stackup errors)
- Handle job queue and compute resources if needed
- Display real-time status updates in the web UI

## Inputs
- Layout file path
- Target power/ground nets
- Frequency range (start, stop, step)
- Port configuration method (auto/manual)
- Capacitor model settings
- Output folder

## Outputs
- Simulation log
- Error/warning summary
- S-parameter file (.sNp)
- Broadband SPICE model (.cir or .lib)
- HTML report or image plots for power delivery network (PDN) analysis

## User Actions via UI
- Upload layout
- Select nets and frequencies
- Start simulation
- Download results

## Dependencies
- Python ≥ 3.8
- PyAEDT
- Ansys Electronics Desktop (SIwave) installed and licensed
- Optional: FastAPI or Streamlit for the UI frontend

## Extensibility
The agent can be extended to support:
- Multiple layout variants
- Batch simulation
- Integration with optiSLang for optimization

## License
Proprietary. Internal use only within [Your Company Name].

