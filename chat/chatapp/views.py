from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import UserProfile, Message
from django.db import models

# Home Page
@login_required
def home(request):
    return HttpResponse("Hi, welcome to the main page of the chatting app.")

# User Signup
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
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

# User Signin
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

# User Profile Setup
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
    return render(request, 'chatapp/chat.html', {'users': users})

@login_required
def specific_chat(request, username):
    other_user = get_object_or_404(User, username=username)
    messages = Message.objects.filter(
        (models.Q(sender=request.user, receiver=other_user) | 
         models.Q(sender=other_user, receiver=request.user))
    ).order_by('timestamp')
    
    # Mark messages as read
    unread_messages = messages.filter(is_read=False, receiver=request.user)
    unread_messages.update(is_read=True)
    
    users = User.objects.exclude(id=request.user.id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content.strip():
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content
            )
        return redirect('specific_chat', username=username)
    
    return render(request, 'chatapp/specific_chat.html', {
        'other_user': other_user,
        'messages': messages,
        'users': users
    })

@login_required
def search_users(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    return render(request, 'chatapp/search_results.html', {'users': users, 'query': query})
# Logout User
def logout_view(request):
    logout(request)
    return redirect('signin')
