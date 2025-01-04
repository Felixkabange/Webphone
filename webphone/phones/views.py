from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.twiml.voice_response import VoiceResponse, Dial
import json
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
# from twilio.twiml.voice_response import VoiceResponse

# Twilio credentials
ACCOUNT_SID = 'AC2ce3c58925a4c038aeb62c3f34717fbf'
AUTH_TOKEN = '1fb23e9bce999fead2fd2bffbaacff0a'
API_SID = 'SKebd2a3534ad060f39332f718a0bc2666'
API_SECRET = 'faGhQO2OwFBnXKfEJuUL00OIUwGHsHBN'
TWIML_APP_SID = 'APc1a28f6163bf72093c132914704e240f'

# Function-based view for making a call
@csrf_exempt
def make_call(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            phone_number = data.get('phone_number', '').strip()
            print(f"Received phone number: {phone_number}")  # Debugging line

            if not phone_number:
                return JsonResponse({"error": "Phone number is missing."}, status=400)

            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            call = client.calls.create(
                url="http://demo.twilio.com/docs/voice.xml",
                to=phone_number,
                from_="+18447556189"
            )
            return JsonResponse({"status": "Call initiated", "sid": call.sid})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, 'phones/dialpad.html')

def voice_response(request):
    """Handle the voice response when the call is answered."""
    response = VoiceResponse()
    
    # Create a Dial verb
    dial = Dial(
        answer_on_bridge=True,  # This prevents the call from being connected before the browser is ready
        caller_id="+18447556189"  # Your Twilio number
    )
    
    # Add the browser client to the dial verb
    dial.client('browser')  # This connects to the browser's audio stream
    
    # Add the dial verb to the response
    response.append(dial)
    
    return HttpResponse(str(response), content_type='text/xml')


@csrf_exempt
def hangup_call(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            call_sid = data.get('call_sid')
            
            if not call_sid:
                return JsonResponse({"error": "Call SID is missing."}, status=400)

            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            call = client.calls(call_sid).update(status='completed')
            
            return JsonResponse({"status": "Call ended", "sid": call.sid})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def call_status(request):
    if request.method == 'POST':
        call_sid = request.POST.get('CallSid')
        call_status = request.POST.get('CallStatus')
        # You can log the status or update a database entry here
        print(f"Call SID: {call_sid}, Status: {call_status}")
        return JsonResponse({"status": "Callback received"})
    return JsonResponse({"error": "Invalid request"}, status=400)

def get_call_status(request, sid):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    try:
        call = client.calls(sid).fetch()
        return JsonResponse({"sid": call.sid, "status": call.status})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def get_twilio_token(request):
    try:
        client_identity = 'browser_user'  # or fetch it from the request
        
        # Create access token
        token = AccessToken(ACCOUNT_SID, API_SID, API_SECRET)
        
        # Assign an identity to the token
        token.identity = client_identity
        
        # Create a Voice grant
        voice_grant = VoiceGrant(
            outgoing_application_sid='APc1a28f6163bf72093c132914704e240f',
            incoming_allow=True  # Allow incoming calls
        )
        token.add_grant(voice_grant)
        
        # Return the token in a valid JSON format
        return JsonResponse({'token': token.to_jwt()})  # No decode needed
    
    except Exception as e:
        print(f"Error generating Twilio token: {e}")
        return JsonResponse({'error': str(e)}, status=500)




# @csrf_exempt
# def receive_call(request):
#     if request.method == 'POST':
#         response = VoiceResponse()
#         response.say("Thank you for calling. Please leave a message after the beep.")
#         response.record(timeout=10, transcribe=True)
#         response.hangup()
#         return JsonResponse({"twiml": str(response)}, safe=False)
#     return JsonResponse({"error": "Invalid method"}, status=400)
