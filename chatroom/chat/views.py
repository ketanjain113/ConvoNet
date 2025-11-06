from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from chatroom.chat.mongo_models import RoomDoc, MessageDoc, TypingDoc, UserProfileDoc, DirectMessageDoc, FriendDoc
from datetime import datetime, timedelta
from django.core.files.storage import default_storage
import gridfs
from mongoengine import get_db
from bson import ObjectId
from django.conf import settings
from chatroom.chat.crypto import encrypt_text, decrypt_text

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Ensure profile exists. Use a deterministic avatar URL seeded by username
            # so the avatar doesn't change per request.
            if not UserProfileDoc.objects(username=user.username).first():
                avatar_base = 'https://avatar.iran.liara.run/public/boy'
                avatar_url = f"{avatar_base}?username={user.username}"
                UserProfileDoc(username=user.username, gender='male', avatar_url=avatar_url).save()
            return redirect('dashboard')
        return render(request, 'login.html', {"error": "Invalid credentials"})
    return render(request, 'login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        gender = request.POST.get('gender')
        if not username or not password:
            return render(request, 'register.html', {"error": "Username and password required"})
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {"error": "Username already taken"})
        user = User.objects.create_user(username=username, password=password)
    # Create profile and avatar. Persist a deterministic avatar URL that
    # includes the username so the external avatar generator returns a
    # stable image for each user.
    avatar_base = 'https://avatar.iran.liara.run/public/boy' if gender == 'male' else 'https://avatar.iran.liara.run/public/girl'
    avatar_url = f"{avatar_base}?username={username}"
    UserProfileDoc(username=username, gender=gender, avatar_url=avatar_url).save()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    # Simple personalized space: list distinct rooms user has posted in by name
    distinct_refs = (MessageDoc.objects(user=request.user.username)
                     .only('room')
                     .order_by('-date')
                     .distinct('room'))

    # Normalize to ObjectId list regardless of whether distinct returns DBRefs, ObjectIds, or RoomDoc instances
    norm_ids = []
    for ref in distinct_refs:
        try:
            norm_ids.append(ref.id)
        except AttributeError:
            norm_ids.append(ref)

    # Fetch room docs and map by id string
    fetched = RoomDoc.objects(id__in=norm_ids)
    room_docs = {str(r.id): r for r in fetched}

    # Preserve ordering from distinct result
    room_names = []
    for ref in distinct_refs:
        key = str(getattr(ref, 'id', ref))
        doc = room_docs.get(key)
        if doc:
            room_names.append(doc.name)
    # Friends with avatars and unread counts
    friend_usernames = [f.friend for f in FriendDoc.objects(owner=request.user.username)]
    profiles = {p.username: p for p in UserProfileDoc.objects(username__in=friend_usernames)}
    unread_map = {}
    for fu in friend_usernames:
        unread_map[fu] = DirectMessageDoc.objects(sender=fu, recipient=request.user.username, unread='1').count()
    friends = []
    for fu in friend_usernames:
        prof = profiles.get(fu)
        friends.append({
            'username': fu,
            'avatar_url': prof.avatar_url if prof else None,
            'unread': unread_map.get(fu, 0)
        })
    # Get current user's avatar
    my_avatar = None
    my_profile = UserProfileDoc.objects(username=request.user.username).first()
    if my_profile:
        my_avatar = my_profile.avatar_url
    return render(request, 'dashboard.html', {"rooms": room_names, "friends": friends, "my_avatar": my_avatar})


@login_required
def add_friend(request):
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)
    username = request.POST.get('username', '').strip()
    if not username or username == request.user.username:
        return HttpResponse('Invalid username', status=400)
    # Ensure user exists in Django auth
    if not User.objects.filter(username=username).exists():
        return HttpResponse('User not found', status=404)
    FriendDoc.objects(owner=request.user.username, friend=username).update_one(upsert=True, set__friend=username)
    return HttpResponse('OK')

@login_required
def room(request, room):
    room_doc = RoomDoc.objects.get(name=room)
    return render(request, 'room.html', {
        'username': request.user.username,
        'room': room,
        'room_details': room_doc
    })

@login_required
def checkview(request):
    room = request.POST['room_name']
    if not RoomDoc.objects(name=room).first():
        RoomDoc(name=room).save()
    return redirect('/' + room + '/')

@login_required
def send(request):
    message = request.POST['message']
    room_name = request.POST['room_id']

    room_doc = RoomDoc.objects.get(name=room_name)
    MessageDoc(value=encrypt_text(message), user=request.user.username, room=room_doc).save()
    return HttpResponse('Message sent successfully')


@login_required
def send_media(request):
    # multipart/form-data: file, room_id
    room_name = request.POST.get('room_id')
    file = request.FILES.get('file')
    if not file or not room_name:
        return HttpResponse('Bad request', status=400)
    room_doc = RoomDoc.objects.get(name=room_name)

    # Priority: S3 (if configured) -> GridFS (if enabled) -> local storage
    url = None
    if getattr(settings, 'USE_S3', False):
        filename = default_storage.save(file.name, file)
        try:
            url = default_storage.url(filename)
        except Exception:
            url = settings.MEDIA_URL + filename
    elif getattr(settings, 'USE_GRIDFS', True):
        # Save to GridFS
        db = get_db()
        fs = gridfs.GridFS(db)
        file_id = fs.put(file.read(), filename=file.name, content_type=(file.content_type or 'application/octet-stream'))
        url = f'/mediafs/{str(file_id)}/'
    else:
        filename = default_storage.save(file.name, file)
        try:
            url = default_storage.url(filename)
        except Exception:
            url = settings.MEDIA_URL + filename
    content_type = (file.content_type or '').lower()
    if content_type.startswith('image/'):
        media_type = 'image'
    elif content_type.startswith('video/'):
        media_type = 'video'
    else:
        media_type = 'file'
    MessageDoc(value='', user=request.user.username, room=room_doc, media_url=url, media_type=media_type).save()
    return JsonResponse({"ok": True, "url": url, "type": media_type})


def mediafs_view(request, file_id):
    """Serve files stored in GridFS at /mediafs/<file_id>/.

    This view reads the file from GridFS and returns it with the stored
    content-type. It's safe for images/videos because we set Content-Disposition
    to inline. For other types the browser will download.
    """
    try:
        db = get_db()
        fs = gridfs.GridFS(db)
        grid_out = fs.get(ObjectId(file_id))
    except Exception:
        return HttpResponse('Not found', status=404)

    data = grid_out.read()
    content_type = getattr(grid_out, 'content_type', None) or 'application/octet-stream'
    resp = HttpResponse(data, content_type=content_type)
    # Inline rendering for images/videos; force download for unknown types
    if content_type.startswith('image/') or content_type.startswith('video/'):
        resp['Content-Disposition'] = f'inline; filename="{grid_out.filename}"'
    else:
        resp['Content-Disposition'] = f'attachment; filename="{grid_out.filename}"'
    return resp


# --- Direct Messages ---
@login_required
def dm_inbox(request):
    # Get distinct conversation partners (either direction)
    partners = set(DirectMessageDoc.objects(sender=request.user.username).distinct('recipient'))
    partners.update(DirectMessageDoc.objects(recipient=request.user.username).distinct('sender'))
    # Unread counts per partner
    unread = {}
    for p in partners:
        unread[p] = DirectMessageDoc.objects(sender=p, recipient=request.user.username, unread='1').count()
    # Get avatars
    profiles = {p.username: p.avatar_url for p in UserProfileDoc.objects(username__in=list(partners))}
    partners_avatars = {}
    for p in partners:
        partners_avatars[p] = profiles.get(p)
    return render(request, 'dm_inbox.html', {
        "partners": sorted(list(partners)),
        "unread": unread,
        "partners_avatars": partners_avatars,
    })


@login_required
def dm_thread(request, username):
    # Mark incoming as read
    DirectMessageDoc.objects(sender=username, recipient=request.user.username, unread='1').update(set__unread='0')
    msgs = (DirectMessageDoc.objects(
        __raw__={
            "$or": [
                {"sender": request.user.username, "recipient": username},
                {"sender": username, "recipient": request.user.username},
            ]
        }
    ).order_by('date'))
    payload = []
    for m in msgs:
        payload.append({
            "id": str(m.id),
            "user": m.sender,
            "value": decrypt_text(m.value),
            "date": m.date.isoformat(),
            "media_url": m.media_url,
            "media_type": m.media_type,
        })
    return JsonResponse({"messages": payload})


@login_required
def dm_chat(request, username):
    # Page shell for a direct conversation; messages are fetched by AJAX from dm_thread
    from chatroom.chat.mongo_models import UserProfileDoc
    me_avatar = None
    peer_avatar = None
    try:
        me_profile = UserProfileDoc.objects.get(username=request.user.username)
        me_avatar = me_profile.avatar_url
    except Exception:
        pass
    try:
        peer_profile = UserProfileDoc.objects.get(username=username)
        peer_avatar = peer_profile.avatar_url
    except Exception:
        pass
    return render(request, 'dm.html', {
        "me": request.user.username,
        "peer": username,
        "me_avatar": me_avatar,
        "peer_avatar": peer_avatar,
    })


@login_required
def dm_send(request):
    # POST: to, message or file
    to_user = request.POST.get('to')
    message = request.POST.get('message', '')
    file = request.FILES.get('file')
    media_url = None
    media_type = None
    if file:
        filename = default_storage.save(file.name, file)
        try:
            media_url = default_storage.url(filename)
        except Exception:
            media_url = settings.MEDIA_URL + filename
        content_type = (file.content_type or '').lower()
        if content_type.startswith('image/'):
            media_type = 'image'
        elif content_type.startswith('video/'):
            media_type = 'video'
        else:
            media_type = 'file'
    DirectMessageDoc(
        sender=request.user.username,
        recipient=to_user,
        value=encrypt_text(message),
        media_url=media_url,
        media_type=media_type,
        unread='1'
    ).save()
    return HttpResponse('OK')


@login_required
def dm_unread_count(request):
    count = DirectMessageDoc.objects(recipient=request.user.username, unread='1').count()
    return JsonResponse({"unread": count})

@login_required
def getMessages(request, room):
    room_doc = RoomDoc.objects.get(name=room)
    messages = MessageDoc.objects(room=room_doc).order_by('date')
    payload = []
    usernames = set()
    for m in messages:
        usernames.add(m.user)
        payload.append({
            "id": str(m.id),
            "value": decrypt_text(m.value),
            "date": m.date.isoformat(),
            "user": m.user,
            "room": str(room_doc.id),
            "media_url": m.media_url,
            "media_type": m.media_type,
        })
    # Build avatar map
    profiles = UserProfileDoc.objects(username__in=list(usernames))
    avatar_map = {p.username: p.avatar_url for p in profiles}
    return JsonResponse({"messages": payload, "avatars": avatar_map})


@login_required
def set_typing(request):
    # POST: room_id (room name), is_typing: '1' or '0'
    room_name = request.POST.get('room_id')
    is_typing = request.POST.get('is_typing') == '1'
    room_doc = RoomDoc.objects.get(name=room_name)
    if is_typing:
        TypingDoc.objects(user=request.user.username, room=room_doc).update_one(
            set__expires_at=datetime.utcnow() + timedelta(seconds=3), upsert=True
        )
    else:
        TypingDoc.objects(user=request.user.username, room=room_doc).delete()
    return HttpResponse('OK')


@login_required
def get_typing(request, room):
    room_doc = RoomDoc.objects.get(name=room)
    # Clean expired
    TypingDoc.objects(room=room_doc, expires_at__lt=datetime.utcnow()).delete()
    users = [t.user for t in TypingDoc.objects(room=room_doc)]

    return JsonResponse({"typing": users})
