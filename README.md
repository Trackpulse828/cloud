#  Problem 1 — Cloud Security & Threat Detection

---

## 🔥 Pipeline Overview

This project demonstrates an automated CI/CD pipeline using modern DevOps tools.

---

## 🛠️ Tools Used
- Jenkins  
- Docker  
- GitHub Actions  

---

## ⚙️ Pipeline Flow

```text
Code pushed to GitHub 
        ↓
GitHub Actions → Runs tests & builds Docker images
        ↓
Jenkins → Pulls code & deploys using Docker Compose
