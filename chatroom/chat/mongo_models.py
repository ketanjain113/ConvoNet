from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, ReferenceField, CASCADE


class RoomDoc(Document):
    name = StringField(required=True, max_length=1000, unique=True)

    meta = {
        "collection": "rooms"
    }


class MessageDoc(Document):
    value = StringField(required=True, max_length=1000000)  # encrypted
    date = DateTimeField(default=datetime.utcnow)
    user = StringField(required=True, max_length=1000000)
    room = ReferenceField(RoomDoc, reverse_delete_rule=CASCADE)
    media_url = StringField()
    media_type = StringField()  # image, video, file

    meta = {
        "collection": "messages",
        "indexes": [
            "room",
            "-date"
        ]
    }


class TypingDoc(Document):
    user = StringField(required=True, max_length=1000)
    room = ReferenceField(RoomDoc, required=True)
    expires_at = DateTimeField(required=True)

    meta = {
        "collection": "typing",
        "indexes": [
            {"fields": ["room", "user"], "unique": True},
            "expires_at"
        ]
    }


class UserProfileDoc(Document):
    username = StringField(required=True, unique=True, max_length=150)
    gender = StringField(choices=("male", "female"))
    avatar_url = StringField()

    meta = {
        "collection": "user_profiles",
        "indexes": [
            {"fields": ["username"], "unique": True}
        ]
    }


class DirectMessageDoc(Document):
    sender = StringField(required=True, max_length=150)
    recipient = StringField(required=True, max_length=150)
    value = StringField(required=True, max_length=1000000)  # encrypted
    date = DateTimeField(default=datetime.utcnow)
    media_url = StringField()
    media_type = StringField()
    unread = StringField(default='1')  # '1' unread, '0' read

    meta = {
        "collection": "direct_messages",
        "indexes": [
            ("sender", "recipient"),
            "-date",
            "unread"
        ]
    }


class FriendDoc(Document):
    owner = StringField(required=True, max_length=150)
    friend = StringField(required=True, max_length=150)

    meta = {
        "collection": "friends",
        "indexes": [
            {"fields": ["owner", "friend"], "unique": True},
            "owner"
        ]
    }


