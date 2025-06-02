# 🎙️ Kaizen Voice Recorder

This is a lightweight, voice-based feedback capture tool built for logistic teams. It allows associates to record short success stories using only their voice—no logins, no typing. Just tap, speak, and send.

## 🔧 Purpose

Capture Lean improvements, team wins, and moments of operational excellence from the floor—without disrupting the flow of work.

Perfect for:
- 📦 Delivery Stations
- 🚛 Driver feedback
- 🧠 Voice of Associate programs
- 💡 Kaizen and Continuous Improvement
- 📈 Operational coaching

## 🛠 Features

- 🎤 One-tap voice recording
- ⚡ Instant submission to backend via API Gateway + Lambda
- 🔐 Backend handles transcription, analysis, and DynamoDB storage
- 🧠 Auto-categorization via Amazon Bedrock + Claude
- 📊 Dashboarding via Amazon QuickSight

## 🖥️ Frontend (HTML + JavaScript)

A simple, responsive web page with:

- Large, mobile-friendly Record button
- Instructional text prompting name, shift, and what went well
- Clean UX feedback (Recording… Sending… Done!)

Hosted via **AWS Amplify**  
🔗 [App URL](https://main.d229qfoesysdjr.amplifyapp.com/)

## 🧩 Architecture

| Component     | Technology |
|---------------|------------|
| Voice Input   | Web browser + MediaRecorder API |
| API Layer     | Amazon API Gateway |
| Processing    | AWS Lambda |
| Storage       | Amazon S3 (raw audio) + DynamoDB |
| Transcription | Amazon Transcribe |
| Categorization| Amazon Bedrock (Claude v3) |
| Analytics     | Amazon QuickSight (Embedded Dashboard) |

## ✅ Usage Instructions

1. Open the app
2. Tap **Start Recording**
3. Say:  
   _“Hi, I’m [Your Name] from [Your Shift], and today I improved [area/task].”_
4. Tap to stop. Done!

## 📦 Deployment

### Requirements

- AWS Account (Enterprise Edition for QuickSight)
- IAM Roles with:
  - `lambda:InvokeFunction`
  - `quicksight:GetDashboardEmbedURL`
  - `quicksight:GenerateEmbedUrlForRegisteredUser`
- Hosted dashboard via QuickSight

### Optional Enhancements

- 🔐 Embed QuickSight securely in your own internal apps
- 📁 Export stories to Excel, Athena, or automated reports
- 🚦 Filter dashboards by category, shift, or transcription status

## 🧠 Behind the Scenes

- Voice story is converted to `.webm`, sent as Base64 to API Gateway
- Lambda stores the file to S3 and kicks off a transcription job
- Once completed, another Lambda:
  - Parses the transcript
  - Classifies the category (Lean, Safety, Poka-Yoke, etc.)
  - Stores metadata in DynamoDB
- Dashboards are updated live via SPICE refresh



## 🤝 Credits

Created by: Mira 
For internal Kaizen programs and voice-based improvement tracking.

---

“Everyone deserves the spotlight. This tool helps you shine.”

