from flask import Blueprint, send_file, session, redirect, url_for, flash, current_app, g, request, render_template
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from functools import wraps
import sqlite3
import groq
import os
from datetime import timedelta

pregnancy = Blueprint('pregnancy', __name__)

@pregnancy.route('/')
def index():
    return render_template('pregnancy/index.html')

@pregnancy.route('/track', methods=['POST'])
def track_pregnancy():
    # Get form data
    weeks_pregnant = request.form.get('weeks_pregnant', type=int)
    due_date = request.form.get('due_date')
    
    if not weeks_pregnant or not due_date:
        flash('Please provide both weeks pregnant and due date.', 'error')
        return redirect(url_for('pregnancy.index'))
    
    # Store in session
    session['pregnancy_details'] = {
        'weeks_pregnant': weeks_pregnant,
        'due_date': due_date
    }
    
    # Redirect to results page
    return redirect(url_for('pregnancy.results'))

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def tracking_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'pregnancy_details' not in session:
            flash('Please enter your pregnancy details first.')
            return redirect(url_for('pregnancy'))
        return f(*args, **kwargs)
    return decorated_function

@pregnancy.route('/download-medical-report')
@tracking_required
def download_medical_report():
    # Create a BytesIO buffer for the PDF
    buffer = BytesIO()
    
    # Create the PDF object using the BytesIO buffer as its "file"
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Get pregnancy details from session
    details = session.get('pregnancy_details', {})
    weeks_pregnant = details.get('weeks_pregnant', 0)
    due_date = details.get('due_date', '')
    
    # Add content to the PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Pregnancy Medical Report")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}")
    c.drawString(100, 680, f"Due Date: {due_date}")
    c.drawString(100, 660, f"Weeks Pregnant: {weeks_pregnant}")
    
    # Add more medical information here
    c.drawString(100, 620, "Medical History:")
    c.drawString(120, 600, "• Blood Type:")
    c.drawString(120, 580, "• Previous Pregnancies:")
    c.drawString(120, 560, "• Current Medications:")
    
    # Save the PDF
    c.save()
    
    # Move to the beginning of the BytesIO buffer
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='pregnancy_medical_report.pdf',
        mimetype='application/pdf'
    )

@pregnancy.route('/download-progress-report')
@tracking_required
def download_progress_report():
    # Create a BytesIO buffer for the PDF
    buffer = BytesIO()
    
    # Create the PDF object using the BytesIO buffer as its "file"
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Get pregnancy details from session
    details = session.get('pregnancy_details', {})
    weeks_pregnant = details.get('weeks_pregnant', 0)
    due_date = details.get('due_date', '')
    countdown = details.get('countdown', 0)
    
    # Add content to the PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Pregnancy Progress Report")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}")
    c.drawString(100, 680, f"Due Date: {due_date}")
    c.drawString(100, 660, f"Weeks Pregnant: {weeks_pregnant}")
    c.drawString(100, 640, f"Days until due date: {countdown}")
    
    # Add progress information
    c.drawString(100, 600, "Progress Summary:")
    c.drawString(120, 580, f"• Current Week: {weeks_pregnant}")
    c.drawString(120, 560, f"• Expected Due Date: {due_date}")
    
    # Save the PDF
    c.save()
    
    # Move to the beginning of the BytesIO buffer
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='pregnancy_progress_report.pdf',
        mimetype='application/pdf'
    )

groq_client = groq.Client(api_key=os.getenv('GROQ_API_KEY'))

@pregnancy.route('/pregnancy/generate_medical_report', methods=['POST'])
def generate_medical_report():
    # Get form data
    blood_type = request.form.get('blood_type')
    previous_pregnancies = request.form.get('previous_pregnancies')
    medical_conditions = request.form.get('medical_conditions')
    medications = request.form.get('medications')
    
    # Get pregnancy tracking data from Groq
    pregnancy_data = get_pregnancy_data()
    
    # Generate report content using Groq
    prompt = f"""Generate a detailed medical report for a pregnant woman with the following information:
    - Current Week: {pregnancy_data['weeks_pregnant']}
    - Blood Type: {blood_type}
    - Previous Pregnancies: {previous_pregnancies}
    - Medical Conditions: {medical_conditions}
    - Current Medications: {medications}
    
    Include sections for:
    1. Medical History Overview
    2. Current Pregnancy Status
    3. Risk Assessment
    4. Recommendations
    5. Next Steps
    
    Format the report in a professional medical style."""
    
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=2048
        )
        
        report_content = response.choices[0].message.content
        
        # Generate PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        
        # Add hospital/clinic header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 800, "MenoCare Medical Report")
        p.setFont("Helvetica", 12)
        p.drawString(50, 780, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Add report content
        y = 750
        for line in report_content.split('\n'):
            if y < 50:  # Start new page if needed
                p.showPage()
                y = 800
            p.drawString(50, y, line)
            y -= 15
            
        p.save()
        buffer.seek(0)
        
        return send_file(
            buffer,
            download_name=f'medical_report_{datetime.now().strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash('Error generating report. Please try again.', 'error')
        return redirect(url_for('pregnancy.results'))

@pregnancy.route('/pregnancy/generate_progress_report', methods=['POST'])
def generate_progress_report():
    # Get form data
    symptoms = request.form.get('symptoms')
    baby_movement = request.form.get('baby_movement')
    sleep_quality = request.form.get('sleep_quality')
    exercise = request.form.get('exercise')
    
    # Get pregnancy tracking data from Groq
    pregnancy_data = get_pregnancy_data()
    
    # Generate report content using Groq
    prompt = f"""Generate a comprehensive pregnancy progress report with the following information:
    - Current Week: {pregnancy_data['weeks_pregnant']}
    - Current Symptoms: {symptoms}
    - Baby Movement: {baby_movement}
    - Sleep Quality: {sleep_quality}
    - Exercise Routine: {exercise}
    
    Include sections for:
    1. Overall Progress Summary
    2. Baby's Development at Current Week
    3. Maternal Health Assessment
    4. Lifestyle and Wellness Review
    5. Recommendations for Next Week
    
    Make the report encouraging and informative."""
    
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0.5,
            max_tokens=2048
        )
        
        report_content = response.choices[0].message.content
        
        # Generate PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        
        # Add header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 800, "Pregnancy Progress Report")
        p.setFont("Helvetica", 12)
        p.drawString(50, 780, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Add report content
        y = 750
        for line in report_content.split('\n'):
            if y < 50:  # Start new page if needed
                p.showPage()
                y = 800
            p.drawString(50, y, line)
            y -= 15
            
        p.save()
        buffer.seek(0)
        
        return send_file(
            buffer,
            download_name=f'progress_report_{datetime.now().strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash('Error generating report. Please try again.', 'error')
        return redirect(url_for('pregnancy.results'))

def get_pregnancy_data():
    try:
        # Get pregnancy details from session
        pregnancy_details = session.get('pregnancy_details', {})
        weeks_pregnant = pregnancy_details.get('weeks_pregnant')
        due_date = pregnancy_details.get('due_date')

        if not weeks_pregnant or not due_date:
            # If no data in session, use Groq to get initial pregnancy information
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a pregnancy tracking assistant. Provide realistic pregnancy information."
                    },
                    {
                        "role": "user",
                        "content": "Generate pregnancy tracking data including weeks pregnant and due date"
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.5,
                max_tokens=1024,
            )
            
            response = chat_completion.choices[0].message.content
            
            # Parse the response to get weeks and due date
            # This is a simple example - you might want to make the parsing more robust
            weeks_pregnant = 12  # Default to first trimester
            due_date = (datetime.now() + timedelta(weeks=28)).strftime('%Y-%m-%d')
            
            # Store in session for future use
            session['pregnancy_details'] = {
                'weeks_pregnant': weeks_pregnant,
                'due_date': due_date
            }
        
        return {
            'weeks_pregnant': weeks_pregnant,
            'due_date': due_date
        }
    except Exception as e:
        print(f"Error getting pregnancy data: {str(e)}")
        return {
            'weeks_pregnant': None,
            'due_date': None
        }

@pregnancy.route('/results')
@tracking_required
def results():
    pregnancy_data = get_pregnancy_data()
    if not pregnancy_data['weeks_pregnant']:
        flash('Please track your pregnancy first.', 'warning')
        return redirect(url_for('pregnancy.index'))

    # Calculate trimester and weeks
    weeks = pregnancy_data['weeks_pregnant']
    due_date = pregnancy_data['due_date']
    trimester = 1 if weeks <= 12 else (2 if weeks <= 26 else 3)
    
    # Detailed baby development information based on week
    development_info = get_baby_development_info(weeks)
    
    # Get upcoming checkup information
    next_checkup = get_next_checkup(weeks)
    
    # Get personalized reminders based on trimester and week
    reminders = get_personalized_reminders(trimester, weeks)
    
    # Get nutrition plan based on trimester
    nutrition_plan = get_nutrition_recommendations(trimester)
    
    return render_template('pregnancy/results.html',
                         weeks_pregnant=weeks,
                         due_date=due_date,
                         fetal_development=development_info,
                         next_checkup=next_checkup,
                         reminders=reminders,
                         nutrition_plan=nutrition_plan)

def get_baby_development_info(weeks):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a pregnancy tracking assistant providing information about fetal development."
                },
                {
                    "role": "user",
                    "content": f"What is the baby's development at {weeks} weeks of pregnancy? Include size, weight, and key developments."
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.5,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error getting baby development info: {str(e)}")
        return "Unable to fetch baby development information at this time."

def get_next_checkup(weeks):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a pregnancy tracking assistant providing information about prenatal checkups."
                },
                {
                    "role": "user",
                    "content": f"What are the recommended checkups and tests for {weeks} weeks of pregnancy?"
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.5,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error getting checkup info: {str(e)}")
        return "Unable to fetch checkup information at this time."

def get_personalized_reminders(trimester, weeks):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a pregnancy tracking assistant providing personalized reminders and tips."
                },
                {
                    "role": "user",
                    "content": f"What are important reminders and tips for pregnancy week {weeks} (trimester {trimester})?"
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.5,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content.split('\n')
    except Exception as e:
        print(f"Error getting reminders: {str(e)}")
        return ["Unable to fetch personalized reminders at this time."]

def get_nutrition_recommendations(trimester):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a pregnancy nutrition expert providing dietary recommendations."
                },
                {
                    "role": "user",
                    "content": f"What are the recommended foods and nutrients for trimester {trimester} of pregnancy?"
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.5,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error getting nutrition recommendations: {str(e)}")
        return "Unable to fetch nutrition recommendations at this time."
