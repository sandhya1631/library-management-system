# Library Database Management System

A Python-based web application for managing library operations including book management, member registration, transaction tracking, and fine calculation.

## Team Members
- **Vishal Rathod**
- **Sandhya Gottimukkala**

## Project Overview
The Library Database Management System automates library operations using Flask framework and SQLite database. It provides a centralized, efficient solution for managing books, members, transactions, fines, and reservations.

## Technologies Used
- **Backend**: Python 3.x, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap 5
- **Version Control**: Git, GitHub

## Features (Planned)
- 📚 Book Management (Add, Edit, Delete, Search)
- 👥 Member Management (Registration, Profile Management)
- 🔄 Transaction Management (Issue, Return, Track)
- 💰 Automatic Fine Calculation
- 📊 Reporting Dashboard
- 🔒 Role-based Access Control

## Database Schema
The system uses a normalized relational database with 5 main tables:
- **Books**: Store book information
- **Members**: Store member information
- **Transactions**: Track book borrowing
- **Fines**: Calculate and track fines
- **Reservations**: Manage book reservations

## Installation

### Prerequisites
- Python 3.x
- pip (Python package manager)

### Setup Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/library-management-system.git
   cd library-management-system
   ```

2. Install required packages:
   ```bash
   pip install flask
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Project Structure
```
library_system/
├── app.py                  # Main Flask application
├── database_schema.sql     # Database schema
├── library.db             # SQLite database (auto-created)
├── templates/             # HTML templates
│   └── index.html        # Homepage
├── static/               # CSS, JS, images
└── README.md            # This file
```

## Current Progress
✅ Requirement Analysis  
✅ Database Design (ER Diagram)  
✅ Flask Application Setup  
✅ Database Schema Creation  
🔄 CRUD Operations (In Progress)  
⏳ Transaction Management (Planned)  
⏳ Fine Calculation (Planned)  
⏳ Reporting Features (Planned)  

## Methodology
Following the **Waterfall Model** with phases:
1. Requirement Analysis ✅
2. Design Phase ✅
3. Implementation Phase 🔄
4. Testing Phase ⏳
5. Deployment Phase ⏳

## Course Information
- **Course**: SSW-555 (Agile Methods)
- **Institution**: Stevens Institute of Technology
- **Semester**: Fall 2024

## License
This project is developed for educational purposes as part of coursework at Stevens Institute of Technology.

## Contact
For questions or collaboration:
- Vishal Rathod - [GitHub Profile]
- Sandhya Gottimukkala - [GitHub Profile]

---
*Last Updated: November 18, 2024*
