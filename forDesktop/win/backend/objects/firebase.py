"""Firebase Realtime Database 설정.

Firebase 콘솔 -> 프로젝트 설정에서 웹 앱을 추가하고 발급받은 값을 입력하세요.
"""

FIREBASE_CONFIG = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "prj-004-calendar.firebaseapp.com",
    "databaseURL": "https://prj-004-calendar-default-rtdb.firebaseio.com",
    "projectId": "prj-004-calendar",
    "storageBucket": "prj-004-calendar.appspot.com",
    "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
    "appId": "YOUR_APP_ID",
}


def get_firebase_config() -> dict[str, str]:
    return dict(FIREBASE_CONFIG)
