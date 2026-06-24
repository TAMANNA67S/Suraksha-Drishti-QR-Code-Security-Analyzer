# Suraksha Drishti

This project contains the requested folder structure for the application.
Suraksha Drishti — QR Code Security AnalyzerSuraksha Drishti is an advanced AI-powered cybersecurity tool designed to detect malicious QR codes and analyze the safety of URLs embedded within them. In an era where "Quishing" (QR Phishing) attacks are on the rise, this system provides a robust layer of defense by scanning, extracting, and evaluating QR codes for potential security threats.
🚀 Key FeaturesIntelligent QR Decoding: Automatically detects and extracts embedded URLs from uploaded images using computer vision.
Multi-Layered Security Analysis: Evaluates URLs based on structure, length, suspicious keywords, and domain credibility.
Phishing & Threat Detection: Identifies shortened URLs, IP-based links, and non-HTTPS connections.
Risk Scoring Engine: Computes a comprehensive risk score to help users understand the severity of the threat.
Interactive Dashboard: A seamless, user-friendly interface powered by Streamlit for instant security assessments.Detailed Reporting: Generates actionable security insights and recommendations based on the analysis.
Tech Stack
Frontend Streamlit
Backend Python QR Processing OpenCV, Pyzbar Data Analysis Pandas, NumPy Security LogicScikit-Learn / Heuristic Analysis Database SQLiteVersion ControlGit 
⚙️ Installation & Setup
Follow these steps to set up the project on your local machine:Clone the repository:
Bash git clone https://github.com/your-username/suraksha-drishti.git
cd suraksha-drishti

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
Install dependencies:Bashpip install -r requirements.txt

3. **Run the application:**
   ```bash
   streamlit run app.py
🛡️ How It WorksUpload: Users upload a QR code image to the platform.Decode: The backend uses Pyzbar and OpenCV to extract the embedded 
URI.Analyze: The system runs a series of heuristic checks (e.g., URL length, suspicious keyword matching, and blacklist verification).
Result: The Dashboard displays the final Risk Score, threat classification (Safe/Suspicious/Malicious), and security recommendations.

Contributions are welcome! If you find a bug or want to add a feature, please feel free to open an Issue or submit a Pull Request.👤 CreditsDeveloper:Tamanna Samal Project Context: gpcssi2026 Contact: samaltamanna485@gmail.com
