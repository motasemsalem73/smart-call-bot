import os
import openai
from elevenlabs import generate
from twilio.rest import Client
from firebase_admin import credentials, firestore, initialize_app
from pydub import AudioSegment
from pydub.playback import play

# ✅ قراءة مفاتيح API من المتغيرات البيئية
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

# ✅ إعداد Firebase
import json

firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS_JSON"))
cred = credentials.Certificate(firebase_credentials)

initialize_app(cred)
db = firestore.client()

# ✅ دالة استدعاء GPT-4 للرد على المستخدم
def get_ai_response(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": user_input}],
        api_key=OPENAI_API_KEY
    )
    return response["choices"][0]["message"]["content"]

# ✅ دالة تحويل النص إلى صوت باستخدام ElevenLabs (تم تعديلها بالكامل)
def text_to_speech(text):
    try:
        audio_data = generate(
            text=text,
            voice="UR972wNGq3zluze0LoIp",  # ✅ ID الصوت المصري من موقع ElevenLabs
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


# ✅ دالة إجراء مكالمة باستخدام Twilio
def make_call(customer_number, text):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    call = client.calls.create(
        twiml=f'<Response><Say voice="alice">{text}</Say></Response>',
        to=customer_number,
        from_=TWILIO_PHONE
    )
    print(f"📞 تم إجراء المكالمة بنجاح! معرف المكالمة: {call.sid}")

# ✅ تجربة البوت
if __name__ == "__main__":
    user_input = input("أدخل سؤالك: ")
    response = get_ai_response(user_input)
    print(f"🤖 رد الذكاء الاصطناعي: {response}")
    
    # تشغيل الصوت
    text_to_speech(response)
    
    # تجربة الاتصال (أدخل رقم هاتفك المصري الصحيح)
    make_call("+201062606098", response)
