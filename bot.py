import openai
from elevenlabs import generate, play
from twilio.rest import Client
import firebase_admin
from firebase_admin import credentials, firestore
import os

# قراءة مفاتيح API من المتغيرات البيئية
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")

# إعداد Firebase
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# استدعاء GPT-4
def get_ai_response(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": user_input}]
    )
    return response["choices"][0]["message"]["content"]

# تحويل النص إلى صوت
def text_to_speech(text):
    audio = generate(text=text, voice="Adam", api_key=elevenlabs_api_key)
    play(audio)

# إجراء مكالمة باستخدام Twilio
def make_call(customer_number, text):
    client = Client(twilio_sid, twilio_token)
    call = client.calls.create(
        twiml=f'<Response><Say voice="alice">{text}</Say></Response>',
        to=customer_number,
        from_=twilio_phone
    )
    print(f"تم إجراء المكالمة بنجاح! معرف المكالمة: {call.sid}")

# تجربة البوت
if __name__ == "__main__":
    user_input = input("أدخل سؤالك: ")
    response = get_ai_response(user_input)
    text_to_speech(response)
    make_call("+201234567890", response)
