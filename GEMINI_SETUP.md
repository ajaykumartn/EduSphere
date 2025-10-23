# Gemini AI Setup Guide

## Getting Your Gemini API Key

1. **Visit Google AI Studio**
   - Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account

2. **Create API Key**
   - Click "Create API Key"
   - Select your project or create a new one
   - Copy the generated API key

3. **Configure EduSphere**
   - Open the `.env` file in the project root
   - Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. **Install Dependencies**
   ```bash
   pip install google-generativeai python-dotenv
   ```

## AI Chat Features

### For Students
- **Study Tips**: Get personalized study advice
- **Exam Strategies**: Learn effective exam techniques
- **Subject Help**: Ask questions about specific topics
- **Motivation**: Receive encouragement and stress management tips
- **Course Guidance**: Get recommendations for course selection

### For Faculty
- **Teaching Methods**: Discover new teaching strategies
- **Student Engagement**: Learn how to better engage students
- **Curriculum Planning**: Get help with lesson planning
- **Assessment Ideas**: Find creative ways to evaluate students
- **Technology Integration**: Learn about educational technology

## Usage Examples

### Student Queries
- "How can I improve my math problem-solving speed?"
- "What's the best way to prepare for JEE Physics?"
- "I'm feeling stressed about exams, any tips?"
- "How should I plan my study schedule?"

### Faculty Queries
- "How can I make online classes more interactive?"
- "What are some effective ways to assess student understanding?"
- "How do I handle students with different learning paces?"
- "Best practices for giving constructive feedback?"

## Features

- **Role-Based Responses**: AI adapts responses based on user role (Student/Faculty)
- **Chat History**: Maintains conversation context within session
- **Real-time Responses**: Fast AI-powered assistance
- **Error Handling**: Graceful fallback when API is unavailable
- **Responsive Design**: Works on all devices

## Troubleshooting

### API Key Issues
- Ensure your API key is valid and active
- Check that you have sufficient quota
- Verify the key is correctly set in the `.env` file

### Connection Issues
- Check your internet connection
- Verify the Gemini API service is available
- Ensure firewall isn't blocking the requests

### No AI Response
- If API key is not configured, users will see a helpful error message
- The chat interface will still be visible but disabled
- All other features of EduSphere continue to work normally

## Security Notes

- Never commit your API key to version control
- Keep your `.env` file secure and private
- Consider using environment variables in production
- Monitor your API usage to avoid unexpected charges

## Cost Considerations

- Gemini API has generous free tier limits
- Monitor usage through Google Cloud Console
- Consider implementing rate limiting for production use
- Each chat message counts as one API request

---

**Note**: The AI Chat feature enhances the EduSphere experience but is optional. All core functionality works without the Gemini API.
