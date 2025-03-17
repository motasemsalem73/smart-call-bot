import os
import json
import requests  # استيراد requests لاستخدام API مباشرة
from elevenlabs import generate, play
from twilio.rest import Client
from firebase_admin import credentials, firestore, initialize_app
from pydub import AudioSegment
from pydub.playback import play

# ✅ قراءة مفاتيح API من المتغيرات البيئية
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

# ✅ إعداد Firebase
firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS_JSON"))
cred = credentials.Certificate(firebase_credentials)
initialize_app(cred)
db = firestore.client()

# ✅ استدعاء Mistral API للرد على المستخدم
def get_ai_response(user_input):
    api_url = "https://api.mistral.ai/v1/chat/completions"  # ✅ العنوان الصحيح لـ API
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": user_input}]
    }

    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(f"❌ خطأ في Mistral API: {response.text}")
        return "عذرًا، حدث خطأ أثناء معالجة طلبك."


# ✅ تحويل النص إلى صوت باستخدام ElevenLabs
def text_to_speech(text):
    try:
        audio_data = generate(
            text=text,
            voice="UR972wNGq3zluze0LoIp",  # ✅ صوت اللهجة المصرية
            api_key=ELEVENLABS_API_KEY
        )

        # 🔹 حفظ الصوت وتشغيله
        file_path = "output.mp3"
        with open(file_path, "wb") as f:
            f.write(audio_data)

        sound = AudioSegment.from_file(file_path, format="mp3")
        play(sound)

    except Exception as e:
        print(f"❌ خطأ في تحويل النص إلى صوت: {e}")


# ✅ إجراء مكالمة باستخدام Twilio
def make_call(customer_number, text):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        call = client.calls.create(
            twiml=f'<Response><Say voice="alice">{text}</Say></Response>',
            to=customer_number,
            from_=TWILIO_PHONE
        )
        print(f"📞 تم إجراء المكالمة بنجاح! معرف المكالمة: {call.sid}")
    except Exception as e:
        print(f"❌ خطأ في إجراء المكالمة: {e}")

# ✅ تجربة البوت
if __name__ == "__main__":
    user_input = "مرحبا، ما هي خدماتك؟"  # مثال لاختبار الكود بدون إدخال يدوي
    response = get_ai_response(user_input)
    print(f"🤖 رد الذكاء الاصطناعي: {response}")

    # تشغيل الصوت
    text_to_speech(response)

    # تجربة الاتصال (أدخل رقم هاتفك المصري الصحيح)
    make_call("+201144582089", response)
