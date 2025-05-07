import os
import google.generativeai as genai
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configure API Key for Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyD4jWq8Y0SgLjFSAHINNPJQB-6B0A8tgi8")
if not api_key:
    print("Error: Missing GOOGLE_API_KEY environment variable. Please set it before running the script.")
    exit(1)

genai.configure(api_key=api_key)

# Model Configuration
generation_config = {
    "temperature": 0.2,
    "max_output_tokens": 512,
    "top_p": 0.95,
    "top_k": 40,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    system_instruction="""
    Absolute Mode. Eliminate emojis, filler, hype, soft asks,
    start with asking name , age ,gender one by one and then ask about the symptoms.
    Use a professional tone, avoid slang, and be concise.

    You are an AI-powered virtual doctor designed to help patients understand their symptoms and predict possible diseases.
    Your responses should be concise yet informative, mimicking a professional doctor’s approach.
    Maintain context across conversations to avoid repeating questions.
    
    Ask one question at a time, ensuring it is relevant to the patient’s symptoms. Avoid unnecessary details and keep responses brief.
    Maintain a professional yet empathetic tone.
    
    Start by asking about the primary symptom and follow logical medical reasoning to narrow down probable conditions.
    Keep track of patient responses to avoid redundant questions and to provide meaningful insights.
    
    Always remind the patient that this is not a substitute for professional medical advice and recommend consulting a doctor.

    If the patient provides a lot of information, summarize it and ask clarifying questions to ensure understanding.
    if the information for the patient is enough provide a diagnosis and treatment plan with some medication if needed.
    dont ask too many questions at once, just ask one question and wait for the answer.
    and dont repeeat the inputs .
 """
)

chat_history = []
patient_data = ""

# Function to generate AI response
def generate_response(input_text):
    global patient_data

    conversation_context = "\n".join([f"User: {chat['User']}\nAI: {chat['AI']}" for chat in chat_history])
    prompt = f"""
    \nHere is the conversation history:
    {conversation_context}
    
    \nThe patient has provided the following information so far:
    {patient_data}
    
    \nBased on this, respond appropriately to their next input:
    User: {input_text}
    AI:
    """

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip() if response.text else "I'm sorry, I couldn't generate a response."
    except Exception as e:
        response_text = "I'm sorry, but I encountered an error processing your request. Please try again."
        print(f"Error: {e}")

    chat_history.append({"User": input_text, "AI": response_text})
    patient_data += f"{input_text}\n"
    return response_text


# Save chat report as PDF
def save_chat_report_pdf():
    if not chat_history:
        print("No chat history to save.")
        return

    file_name = f"chat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    try:
        c = canvas.Canvas(file_name, pagesize=letter)
        width, height = letter
        
        # Set margins
        left_margin = 50
        right_margin = width - 50
        text_width = right_margin - left_margin
        
        def write_wrapped_text(text, y_pos, is_bold=False):
            if is_bold:
                c.setFont("Helvetica-Bold", 12)
            else:
                c.setFont("Helvetica", 12)
                
            # Split text into words
            words = text.split()
            line = []
            current_y = y_pos
            
            for word in words:
                line.append(word)
                line_text = ' '.join(line)
                text_width = c.stringWidth(line_text, c._fontname, c._fontsize)
                
                if text_width > (right_margin - left_margin):
                    # Remove last word and print line
                    line.pop()
                    final_line = ' '.join(line)
                    c.drawString(left_margin, current_y, final_line)
                    current_y -= 20
                    
                    # Start new line with the last word
                    line = [word]
                    
                    # Check if we need a new page
                    if current_y < 50:
                        c.showPage()
                        current_y = height - 50
                        if is_bold:
                            c.setFont("Helvetica-Bold", 12)
                        else:
                            c.setFont("Helvetica", 12)
            
            # Print remaining text
            if line:
                final_line = ' '.join(line)
                c.drawString(left_margin, current_y, final_line)
                current_y -= 20
            
            return current_y

        # Title and Date
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, height - 50, "HealthNexus AI - Chat Session Report")
        c.setFont("Helvetica", 12)
        c.drawString(left_margin, height - 70, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        y_position = height - 100
        
        # Write chat content
        for chat in chat_history:
            # User message with bold header
            user_text = f"User: {chat['User']}"
            y_position = write_wrapped_text(user_text, y_position, is_bold=True)
            
            # AI response with bold header
            ai_text = f"AI: {chat['AI']}"
            y_position = write_wrapped_text(ai_text, y_position - 20)
            
            y_position -= 20  # Extra space between conversations
            
            # Check if we need a new page
            if y_position < 50:
                c.showPage()
                y_position = height - 50

        c.save()
        print(f"✅ Chat report PDF created successfully: {file_name}")
    except Exception as e:
        print(f"❌ Error creating chat report PDF: {e}")

# Save summary as PDF
def save_summary_report_pdf():
    summary = generate_summary()

    if summary == "No chat history available." or summary == "Error generating summary.":
        print("No summary to save.")
        return

    file_name = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    try:
        c = canvas.Canvas(file_name, pagesize=letter)
        width, height = letter
        
        # Set margins
        left_margin = 50
        right_margin = width - 50
        
        def write_wrapped_text(text, y_pos, is_bold=False):
            if is_bold:
                c.setFont("Helvetica-Bold", 12)
            else:
                c.setFont("Helvetica", 12)
                
            # Split text into words
            words = text.split()
            line = []
            current_y = y_pos
            
            for word in words:
                line.append(word)
                line_text = ' '.join(line)
                text_width = c.stringWidth(line_text, c._fontname, c._fontsize)
                
                if text_width > (right_margin - left_margin):
                    # Remove last word and print line
                    line.pop()
                    final_line = ' '.join(line)
                    c.drawString(left_margin, current_y, final_line)
                    current_y -= 20
                    
                    # Start new line with the last word
                    line = [word]
                    
                    # Check if we need a new page
                    if current_y < 50:
                        c.showPage()
                        current_y = height - 50
                        if is_bold:
                            c.setFont("Helvetica-Bold", 12)
                        else:
                            c.setFont("Helvetica", 12)
            
            # Print remaining text
            if line:
                final_line = ' '.join(line)
                c.drawString(left_margin, current_y, final_line)
                current_y -= 20
            
            return current_y

        # Title and Date
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, height - 50, "HealthNexus AI - Patient Summary Report")
        c.setFont("Helvetica", 12)
        c.drawString(left_margin, height - 70, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        y_position = height - 100
        
        # Process summary sections
        for line in summary.split('\n'):
            if line.strip():
                if line.startswith('**') and line.endswith('**'):
                    # Section headers (bold)
                    header = line.strip('*')
                    y_position = write_wrapped_text(header, y_position, is_bold=True)
                elif ':' in line:
                    # Key-value pairs (key in bold)
                    key, value = line.split(':', 1)
                    y_position = write_wrapped_text(f"{key}:", y_position, is_bold=True)
                    y_position = write_wrapped_text(value, y_position - 20)
                else:
                    # Regular text
                    y_position = write_wrapped_text(line, y_position)
                
                y_position -= 10  # Extra spacing between sections
                
                # Check if we need a new page
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50

        c.save()
        print(f"✅ Summary report PDF created successfully: {file_name}")
    except Exception as e:
        print(f"❌ Error creating summary report PDF: {e}")

# Generate a structured summary
def generate_summary():
    if not chat_history:
        print("No chat history available to summarize.")
        return "No chat history available."

    patient_responses = "\n".join([chat["User"] for chat in chat_history])

    try:
        summary_prompt = (
            "Based on the chat history, generate a structured medical summary for a doctor. "
            "Ensure the report is clear and well-organized with the following sections:\n\n"
            "**Patient Summary Report**\n"
            "---------------------------\n"
            "**Patient Name:** [If available]\n"
            "**Age:** [If mentioned]\n"
            "**Gender:** [If mentioned]\n"
            "**Primary Complaint:** [Main symptom(s) reported by the patient]\n"
            "**History of Present Illness:** [A brief timeline of symptoms and their progression]\n"
            "**Relevant Medical History:** [Previous conditions, surgeries, chronic illnesses]\n"
            "**Current Medications:** [If the patient mentioned any]\n"
            "**Allergies:** [Any known drug or food allergies]\n"
            "**Lifestyle Factors:** [Smoking, alcohol, diet, physical activity, etc.]\n"
            "**Possible Diagnoses:** [List potential conditions based on symptoms]\n"
            "**Recommended Next Steps:** [Suggest possible medical tests or specialist consultation]\n"
            "**Urgency Level:** [Mild / Moderate / Severe – based on symptoms]\n\n"
            "Use only relevant details from the conversation. Exclude redundant or conversational parts.\n"
            f"\nPatient's conversation history:\n{patient_responses}\n\n"
        )
        summary_response = model.generate_content(summary_prompt)
        summary_text = summary_response.text.strip() if summary_response.text else "Summary not available."
    except Exception as e:
        summary_text = "Error generating summary."
        print(f"Error: {e}")

    return summary_text


# Exit function to save reports and end the session
def exit_function():
    print("\nSaving chat report and summary...")
    save_chat_report_pdf()
    save_summary_report_pdf()
    print("Session ended.")


# Main chat loop
def chat_loop():
    print("HealthNexus AI Chatbot - Type 'exit' to end session.\n")
    while True:
        try:
            user_input = input("YOU: ").strip()
            if user_input.lower() in ["exit", "quit", "end", "thank you", "bye"]:
                exit_function()
                break

            ai_response = generate_response(user_input)
            print("HealthNexus AI:", ai_response)

        except KeyboardInterrupt:
            exit_function()
            break


if __name__ == "__main__":
    chat_loop()
