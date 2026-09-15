# AI Interview Platform

An AI-powered technical interview platform that connects companies with talented students through automated technical assessments.

## Features

### For Companies
- Company registration and authentication
- Post job opportunities with technical requirements
- Select programming domains (C, C++, Python, Java, JavaScript, SQL, Web Development, Algorithms)
- Set exam duration and difficulty levels
- View applicant results and HR round eligibility

### For Students
- Student registration and authentication
- Browse available job opportunities
- Take AI-evaluated technical exams
- Webcam monitoring during exams
- Real-time timer and progress tracking
- Instant results with HR round eligibility

### Technical Features
- AI-powered answer evaluation using Groq API
- Webcam monitoring for exam integrity
- Multiple programming language support
- Responsive web design
- MongoDB database for data storage
- Flask backend with secure authentication

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend**: Python, Flask
- **Database**: MongoDB
- **AI/ML**: Groq API for answer evaluation
- **Authentication**: Flask-Login with password hashing

## Prerequisites

- Python 3.8+
- MongoDB installed and running
- Groq API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-interview-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   MONGO_URI=mongodb://localhost:27017/ai_interview
   SECRET_KEY=your_secret_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Start MongoDB**
   Make sure MongoDB is running on your system:
   ```bash
   # Windows
   net start MongoDB
   
   # macOS/Linux
   mongod
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Usage

### For Companies

1. **Register a Company Account**
   - Visit the platform homepage
   - Click "For Companies" → "Sign Up"
   - Fill in company details (name, email, industry, size, description)

2. **Post a Job**
   - Login to your company dashboard
   - Click "Post New Job"
   - Fill in job details, select programming domains, set exam duration
   - Submit the job posting

3. **Monitor Applications**
   - View posted jobs in the dashboard
   - Track applicant numbers and exam results
   - Review candidates eligible for HR rounds

### For Students

1. **Register a Student Account**
   - Visit the platform homepage
   - Click "For Students" → "Sign Up"
   - Fill in personal details, education, and technical skills

2. **Browse and Apply for Jobs**
   - Login to student dashboard
   - View available job opportunities
   - Click "Take Exam" for desired positions

3. **Take Technical Exam**
   - Allow webcam access (required for monitoring)
   - Select your preferred programming domain
   - Answer technical questions within time limit
   - Submit exam for AI evaluation

4. **View Results**
   - Receive instant score out of 100
   - Check HR round eligibility (score ≥ 70%)
   - Track all exam results in dashboard

## API Integration

### Groq API Setup

1. Sign up for a Groq account at [https://groq.com](https://groq.com)
2. Generate an API key
3. Add the API key to your `.env` file

### Answer Evaluation

The platform uses Groq's LLaMA2 model to evaluate technical answers:
- Analyzes code correctness and efficiency
- Evaluates conceptual understanding
- Provides scores out of 100
- Determines HR round eligibility

## Database Schema

### Companies Collection
```javascript
{
  name: String,
  email: String,
  password: String (hashed),
  company_size: String,
  industry: String,
  description: String,
  created_at: Date
}
```

### Students Collection
```javascript
{
  name: String,
  email: String,
  password: String (hashed),
  phone: String,
  education: String,
  skills: String,
  created_at: Date
}
```

### Jobs Collection
```javascript
{
  company_id: String,
  company_name: String,
  title: String,
  description: String,
  requirements: String,
  domains: Array,
  duration: Number,
  created_at: Date,
  status: String
}
```

### Exam Results Collection
```javascript
{
  student_id: String,
  student_name: String,
  job_id: String,
  domain: String,
  answers: Object,
  score: Number,
  eligible_for_hr: Boolean,
  submitted_at: Date
}
```

### TRI Interview Collection
```javascript
{
  _id: String,
  candidate_id: String,
  company_id: String,
  scheduled_at: Date,
  interview_date: String,
  interview_time: String,
  interview_type: String,
  interviewer_name: String,
  interviewer_email: String,
  notes: String,
  status: String,
  created_at: Date
}
```

### TRI Schedules Collection
```javascript
{
  _id: String,
  candidate_id: String,
  company_id: String,
  scheduled_at: Date,
  interview_date: String,
  interview_time: String,
  interview_type: String,
  interviewer_name: String,
  interviewer_email: String,
  notes: String,
  status: String,
  created_at: Date
}
```

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- CSRF protection
- Webcam monitoring for exam integrity
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and queries, please contact the development team.

---

**Note**: This is a demonstration platform. For production use, additional security measures and scalability considerations should be implemented.
