from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import UserProfile, Message, Group, GroupMessage
from django.db import models
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from datetime import datetime
from django.utils import timezone


@login_required
def home(request):
    return render(request, 'chatapp/home.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        # Creating User
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Account has been created successfully')
        return redirect('signin')

    return render(request, 'chatapp/signup.html')


def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('chat') if UserProfile.objects.filter(user=user).exists() else redirect('userprofile')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('signin')

    return render(request, 'chatapp/signin.html')

@login_required
def userprofile_view(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        profilephoto = request.FILES.get('profilephoto')

        user = request.user
        user.first_name = firstname
        user.last_name = lastname
        user.save()

        userprofile, created = UserProfile.objects.get_or_create(user=user)
        if profilephoto:
            userprofile.profile_Photo = profilephoto
            userprofile.save()

        return redirect('chat')

    return render(request, 'chatapp/userprofile.html')

@login_required
def chat_view(request):
    users = User.objects.exclude(id=request.user.id)
    user_groups = request.user.joined_groups.all()
    return render(request, 'chatapp/chat.html', {'users': users, 'user_groups': user_groups})

@login_required
def specific_chat(request, username):
    other_user = get_object_or_404(User, username=username)
    messages_list = Message.objects.filter(
        (models.Q(sender=request.user, receiver=other_user) | 
         models.Q(sender=other_user, receiver=request.user))
    ).order_by('timestamp')
    
    # Mark messages as read
    unread_messages = messages_list.filter(is_read=False, receiver=request.user)
    unread_messages.update(is_read=True)
    
    users = User.objects.exclude(id=request.user.id)
    user_groups = request.user.joined_groups.all()
    

    today = timezone.now()
    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check for AJAX request
            content = request.POST.get('content', '').strip()
            if content:
                # Create the message
                new_message = Message.objects.create(
                    sender=request.user,
                    receiver=other_user,
                    content=content,
                    timestamp=timezone.now()  # Use timezone.now() here as well
                )
                
                # Prepare JSON response
                return JsonResponse({
                    'status': 'success',
                    'message': {
                        'content': new_message.content,
                        'time': new_message.timestamp.strftime('%I:%M %p'),  # Format time as "12:30 PM"
                        'timestamp': new_message.timestamp.isoformat()  # ISO format for timestamp
                    }
                })
            else:
                return JsonResponse({'status': 'error', 'error': 'Message cannot be empty'}, status=400)
        
        # If not an AJAX request, fall back to normal POST handling
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content,
                timestamp=timezone.now()  # Use timezone.now() here too
            )
        return redirect('specific_chat', username=username)
    
    return render(request, 'chatapp/specific_chat.html', {
        'other_user': other_user,
        'new_messages': messages_list,
        'users': users,
        'user_groups': user_groups,
        'today': today  # Django timezone object will work with the date filter
    })

@login_required
def search_users(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    return render(request, 'chatapp/search_results.html', {'users': users, 'query': query})

@login_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('name')
        description = request.POST.get('description')
        member_ids = request.POST.getlist('members')
        
        if not group_name:
            messages.error(request, 'Group name is required')
            return redirect('create_group')
            
        group = Group.objects.create(
            name=group_name,
            description=description,
            creator=request.user
        )
        
        # Add creator as a member
        group.members.add(request.user)
        
        # Add selected members
        for member_id in member_ids:
            try:
                user = User.objects.get(id=member_id)
                group.members.add(user)
            except User.DoesNotExist:
                pass
                
        messages.success(request, f'Group "{group_name}" created successfully')
        return redirect('group_chat', group_id=group.id)
        
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chatapp/create_group.html', {'users': users})

@login_required
def group_chat(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    # Check if user is a member of the group
    if not group.members.filter(id=request.user.id).exists():
        messages.error(request, 'You are not a member of this group')
        return redirect('chat')
    
    messages_list = GroupMessage.objects.filter(group=group).order_by('timestamp')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content.strip():
            GroupMessage.objects.create(
                sender=request.user,
                group=group,
                content=content
            )
        return redirect('group_chat', group_id=group_id)
    
    users = User.objects.exclude(id=request.user.id)
    user_groups = request.user.joined_groups.all()
    
    return render(request, 'chatapp/group_chat.html', {
        'group': group,
        'chat_messages': messages_list,
        'users': users,
        'user_groups': user_groups
    })

@login_required
def manage_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    # Only creator can manage the group
    if group.creator != request.user:
        messages.error(request, 'Only the group creator can manage the group')
        return redirect('group_chat', group_id=group_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update':
            group_name = request.POST.get('name')
            description = request.POST.get('description')
            
            if group_name:
                group.name = group_name
                group.description = description
                group.save()
                messages.success(request, 'Group updated successfully')
            
        elif action == 'add_members':
            member_ids = request.POST.getlist('members')
            for member_id in member_ids:
                try:
                    user = User.objects.get(id=member_id)
                    group.members.add(user)
                except User.DoesNotExist:
                    pass
            messages.success(request, 'Members added successfully')
            
        elif action == 'remove_member':
            member_id = request.POST.get('member_id')
            try:
                user = User.objects.get(id=member_id)
                if user != request.user:  # Prevent creator from removing themselves
                    group.members.remove(user)
                    messages.success(request, f'{user.username} removed from the group')
            except User.DoesNotExist:
                pass
                
        elif action == 'delete_group':
            group_name = group.name
            group.delete()
            messages.success(request, f'Group "{group_name}" deleted successfully')
            return redirect('chat')
            
        return redirect('manage_group', group_id=group_id)
    
    # Get non-member users for adding to group
    non_members = User.objects.exclude(
        models.Q(id__in=group.members.all().values_list('id', flat=True)) | 
        models.Q(id=request.user.id)
    )
    
    return render(request, 'chatapp/manage_group.html', {
        'group': group,
        'non_members': non_members
    })

@login_required
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.members.add(request.user)
    messages.success(request, f'You have joined the group "{group.name}"')
    return redirect('group_chat', group_id=group_id)

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    # Prevent creator from leaving their own group
    if group.creator == request.user:
        messages.error(request, 'As the creator, you cannot leave the group. You can delete it instead.')
    else:
        group.members.remove(request.user)
        messages.success(request, f'You have left the group "{group.name}"')
    
    return redirect('chat')



@login_required
def check_new_messages(request, username):
    other_user = get_object_or_404(User, username=username)
    
    # Get the timestamp of the last seen message from the request
    last_timestamp = request.GET.get('last_timestamp')
    
    # Create base query for messages between these users
    base_query = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | 
        Q(sender=other_user, receiver=request.user)
    )
    
    # If we have a last timestamp, only get messages after that
    if last_timestamp:
        try:
            from django.utils import timezone
            from dateutil import parser
            
            # Parse the ISO timestamp
            last_seen = parser.parse(last_timestamp)
            # Make sure it's timezone aware if your Django settings use timezone
            if timezone.is_naive(last_seen):
                last_seen = timezone.make_aware(last_seen)
                
            # Get only new messages
            new_messages = base_query.filter(timestamp__gt=last_seen).order_by('timestamp')
        except Exception as e:
            # If parsing fails, default to all recent messages
            new_messages = base_query.order_by('-timestamp')[:20]
    else:
        # Without a timestamp, just get recent messages
        new_messages = base_query.order_by('-timestamp')[:20]
    
    messages_data = []
    for message in new_messages:
        # Only include messages from the other user
        if message.sender != request.user:
            messages_data.append({
                'id': message.id,
                'content': message.content,
                'time': message.timestamp.strftime('%I:%M %p'),
                'timestamp': message.timestamp.isoformat(),
                'sender': message.sender.username
            })
    
    return JsonResponse({'status': 'success', 'new_messages': messages_data})

# Logout User
@login_required
def logout_view(request):
    logout(request)
    return redirect('chat')