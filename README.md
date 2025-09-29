# 🚴 AI-Powered Cycling Biomechanics Analyzer

A computer vision project that analyzes **cycling leg movements in real-time** using OpenCV and MediaPipe.  
It provides **live feedback on knee angles**, flags **injury risks**, and generates **CSV + PDF reports** with graphs and recommendations.  

---

## ✨ Features
- Real-time video analysis with OpenCV + MediaPipe  
- Tracks **hip–knee–ankle angles** frame by frame  
- Computes statistical metrics:
  - Median (p50)  
  - 95th percentile (p95)  
- Detects and flags:
  - **Overextension risk** (>155°)  
  - **High flexion risk** (<145°)  
- Saves raw session data in CSV  
- Generates a PDF report with:
  - Graph of knee angle over time  
  - Safe range highlights  
  - Risk summary  

---

## 🛠️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-NotDrake100/AI-Powered-Cycling.git
   cd "AI-Powered-Cycling"

2.  Create and activate a virtual environment
   On Mac/Linux:
   
   python3 -m venv venv
   source venv/bin/activate

3.  Install dependencies
    
    pip install -r requirements.txt

4.  Run the project 

    python cycle_live_dashboard.py
    
5.  Deactivate the virtual environment when done
    
    deactivate

# 🚴 AI-Powered Cycling Biomechanics

This project analyzes cycling biomechanics using AI-powered pose detection, tracking knee angles, and generating structured session reports.  

---

## 🎥 Demo Video
Example cycling session:  
![Cycling Demo](https://github.com/user-attachments/assets/94b842a2-e246-46c0-9db3-3c113edd8102)

---

## 📈 Angle Tracking Plot
Knee angle over time with percentile analysis (p50, p95):  
<img width="1000" height="400" src="https://github.com/user-attachments/assets/d6fc7571-9e0d-4412-9fc6-658d500c50ec" />

---

## 📊 Generated Session Report
Each session generates:
- Knee angles per frame  
- Percentiles (p50, p95)  
- Flexion/overextension risk  
- Stroke count and phase tracking  

[Download sample CSV](https://github.com/user-attachments/files/22597145/session_20250929_021823.csv)
[Download sample CSV](https://github.com/user-attachments/files/22597494/session_20250929_021823_report.pdf)
 
