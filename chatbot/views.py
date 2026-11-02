from django.shortcuts import render
from django.http import JsonResponse
from .nlp_engine import get_troubleshooting_response

def chat_home(request):
    if request.method == 'POST':
        user_query = request.POST.get('message')
        
        # Retrieve active wizard state from Django session
        active_wizard = request.session.get('active_wizard', None)
        
        # Get response and updated wizard state from our engine
        response_text, new_wizard_state = get_troubleshooting_response(user_query, active_wizard)
        
        # Save the new wizard state back to the Django session
        request.session['active_wizard'] = new_wizard_state
        
        return JsonResponse({'response': response_text})
        
    return render(request, 'chatbot/chat.html')

# Optional alias so references to chat_view won't break either
chat_view = chat_home