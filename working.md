# 🚀 Web Scraping Python Script  
![Build](https://img.shields.io/badge/status-in%20progress-yellow) 
![Python](https://img.shields.io/badge/built%20with-Python-orange)  
![License](https://img.shields.io/badge/license-MIT-green)  

This script extracts **blogs/articles from any WordPress-powered website** into an **XML file**, just by providing the blog link(s).  
It can handle multiple links at once and works with different WordPress setups (API-enabled sites, HTML parsing fallback, or Selenium/Playwright automation if needed).  

---

## ✨ Features  

- 🔗 Extracts blog data from **any WordPress blog**.  
- 📂 Saves extracted data into **XML format**.  
- 🌍 Supports **multiple blog URLs** at once.  
- 🔎 Uses different approaches:  
  - REST API (if available)  
  - BeautifulSoup (HTML parsing)  
  - Selenium/Playwright (when JavaScript rendering is needed)  
- 🛡️ Error handling for blocked APIs or incorrect URLs.  

## ⚙️ Prerequisites  

Before running this script, make sure you have:  

- ✅ **Python 3.9+** (latest recommended)  
- ✅ Installed required dependencies from `requirements.txt`  
- ✅ (Optional) Browser driver (managed automatically by `webdriver-manager`)  


## 📦 Installation  

Follow these steps to set up the project locally:  

### 1. Clone the Repository  

```bash
git clone https://github.com/hpx07/Web-Scraping-Python-Script.git
cd Web-Scraping-Python-Script
