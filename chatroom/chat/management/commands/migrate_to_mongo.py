from django.core.management.base import BaseCommand

from chatroom.chat.models import Room as SqlRoom, Message as SqlMessage
from chatroom.chat.mongo_models import RoomDoc, MessageDoc


class Command(BaseCommand):
    help = "Migrate chat data from SQLite (Django models) to MongoDB (MongoEngine)"

    def handle(self, *args, **options):
        room_id_map = {}

        self.stdout.write(self.style.NOTICE("Migrating rooms..."))
        for r in SqlRoom.objects.all():
            rd = RoomDoc.objects(name=r.name).first()
            if not rd:
                rd = RoomDoc(name=r.name)
                rd.save()
            room_id_map[r.id] = rd
        self.stdout.write(self.style.SUCCESS(f"Rooms migrated: {len(room_id_map)}"))

        self.stdout.write(self.style.NOTICE("Migrating messages..."))
        migrated = 0
        for m in SqlMessage.objects.all():
            # Convert stored room id (string) to actual room doc if possible
            room_doc = None
            if m.room:
                try:
                    rid = int(m.room)
                    room_doc = room_id_map.get(rid)
                except ValueError:
                    # If it is not an int, try match by room name
                    room_doc = RoomDoc.objects(name=m.room).first()

            MessageDoc(
                value=m.value,
                date=m.date,
                user=m.user,
                room=room_doc
            ).save()
            migrated += 1
        self.stdout.write(self.style.SUCCESS(f"Messages migrated: {migrated}"))

        self.stdout.write(self.style.SUCCESS("Migration to MongoDB complete."))



