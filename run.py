#!/usr/bin/env python3
"""
EduSphere - Complete Learning Platform
Launch script for the application
"""

import os
import sys
from app import app, init_db

def check_database():
    """Check if database exists and initialize if needed"""
    if not os.path.exists('edusphere.db'):
        print("Database not found. Initializing...")
        init_db()
        print("Database initialized successfully!")
        
        # Populate sample data
        try:
            from populate_data import populate_sample_data
            populate_sample_data()
            print("Sample data populated successfully!")
        except Exception as e:
            print(f"Warning: Could not populate sample data: {e}")
    else:
        print("Database found. Starting application...")

def main():
    """Main function to run the application"""
    print("=" * 50)
    print("🚀 EduSphere - Complete Learning Platform")
    print("=" * 50)
    
    # Check and initialize database
    check_database()
    
    print("\n🎯 Demo Credentials:")
    print("   👨‍💼 Admin: admin@EduSphere.com / admin123")
    print("   👨‍🏫 Faculty: teacher1@EduSphere.com / teacher123") 
    print("   🎓 Student: student1@EduSphere.com / student123")
    
    print("\n📚 Features Available:")
    print("• Role-Based Authentication (Student/Faculty/Admin)")
    print("• Personalized Dashboards")
    print("• Interactive FLUX Classroom")
    print("• Comprehensive Test Series")
    print("• Real-time Analytics")
    
    print(f"\n🌐 Starting server...")
    print(f"📍 Access the application at: http://localhost:5000")
    print(f"🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for using EduSphere!")
        sys.exit(0)

if __name__ == '__main__':
    main()
