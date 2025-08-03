# Court Data Fetcher & Mini-Dashboard

##  Project Status: COMPLETE 

A fully functional web application for fetching case details from Delhi High Court with modern UI, automatic CAPTCHA solving, and robust error handling.


##  Target Court
**Delhi High Court** (https://delhihighcourt.nic.in/app/case-number)

**Why Delhi High Court was chosen:**
- Reliable public access with consistent HTML structure
- Well-documented case search functionality  
- Comprehensive case information available
- Manageable CAPTCHA implementation for automation
- Active judicial database with real-time updates

##  Demo Video
**[Court Data Fetcher - Live Demonstration](https://youtu.be/oKhKe3wMFig)**

*5-minute demonstration showcasing:*
- Real-time case search from Delhi High Court
- Modern web interface with form validation
- Database integration and error handling
- PDF document download capabilities
- Professional UI/UX design
- End-to-end functionality demonstration

##  Features Implemented

### Core Functionality 
- **Case Search**: Search by case type, number, and filing year
- **Data Extraction**: Parties' names, filing dates, hearing dates, case status
- **PDF Downloads**: Direct access to court documents and orders
- **Search Logging**: All queries stored in SQLite database with timestamps
- **Error Handling**: User-friendly validation and error messages

### Technical Features 
- **Modern UI**: Responsive design with smooth animations and loading states
- **Form Validation**: Client and server-side input validation
- **Database Integration**: SQLite with proper schema and indexing
- **Demo Mode**: Simulated data for testing and demonstration
- **Security**: Input sanitization, rate limiting, environment variables
- **Automatic CAPTCHA Solving**: OCR-based numeric CAPTCHA resolution using Tesseract

### Advanced Capabilities 
- **Real Website Integration**: Live connection to Delhi High Court portal
- **Session Management**: Proper browser automation with Selenium WebDriver
- **Image Processing**: CAPTCHA enhancement for better OCR accuracy
- **Fallback Mechanisms**: Manual CAPTCHA solving when automatic fails
- **Comprehensive Logging**: Detailed debugging and monitoring

##  Installation & Setup

### Prerequisites
- Python 3.8+
- Chrome browser
- Git
- Tesseract OCR (for automatic CAPTCHA solving)

### Quick Start
