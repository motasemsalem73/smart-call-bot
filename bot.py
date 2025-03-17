import os
import speech_recognition as sr
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from elevenlabs import play, stream, generate
from firebase_admin import credentials, firestore, initialize_app

# ✅ تحميل مفاتيح API من المتغيرات البيئية
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# ✅ إعداد Firebase
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS_JSON")
cred = credentials.Certificate(firebase_credentials)
initialize_app(cred)
db = firestore.client()

# ✅ إعداد المايكروفون والتعرف على الصوت
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# ✅ إعداد Mistral AI للردود الذكية
mistral_client = MistralClient(api_key=MISTRAL_API_KEY)

# ✅ دالة الاستماع وتحويل الصوت إلى نص
def listen():
    with microphone as source:
        print("🎤 تحدث الآن...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="ar-EG")
        print(f"👂 سمعت: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ لم أفهم الصوت، حاول مرة أخرى.")
        return None
    except sr.RequestError as e:
        print(f"⚠️ خطأ في خدمة التعرف على الصوت: {e}")
        return None

# ✅ دالة الحصول على رد الذكاء الاصطناعي
def get_ai_response(user_input):
    messages = [ChatMessage(role="user", content=user_input)]
    response = mistral_client.chat(model="mistral-tiny", messages=messages)
    return response.choices[0].message.content

# ✅ دالة التحدث بالصوت الفوري
def speak(text):
    print(f"🗣️ الرد: {text}")
    audio_stream = generate(text=text, voice="newscaster", stream=True, api_key=ELEVENLABS_API_KEY)
    stream(audio_stream)

# ✅ تشغيل البوت
if __name__ == "__main__":
    while True:
        user_input = listen()
        if user_input:
            response = get_ai_response(user_input)
            speak(response)
