import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate('./creds/firebase_key.json')
firebase_admin.initialize_app(cred)
firestore_db = firestore.client()


def get_messages():
    messages = firestore_db.collection(u'messages').order_by(
        u'sent_at',
        direction=firestore.Query.DESCENDING
        ).get()
    return messages


def save_message(bot, username, message, proxy=None):
    firestore_db.collection(u'messages').add({
        u'bot': bot,
        u'username': username,
        u'message': message,
        u'sent_at':
        datetime.datetime.now(),
        u'proxy': proxy
    })


# messsages = get_messages()
# for message in messsages:
#     print(message.to_dict())
