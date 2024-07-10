import requests
from django.shortcuts import render, redirect
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

FASTAPI_URL = "http://localhost:8000"

logging.basicConfig(level=logging.INFO)

def home(request):
    return render(request, "frontend/home.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        logging.info(f"Attempting to log in user: {username}")
        
        response = requests.post(f"{FASTAPI_URL}/token/", json={
            "username": username,
            "password": password
        })
        logging.info(f"Login response status code: {response.status_code}")
        logging.info(f"Login response: {response.json()}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            request.session['token'] = token  # Store the token in the session
            request.session['password'] = password  # Store the password in the session
            request.session['username'] = username  # Store the username in the session
            return redirect('profile')
        else:
            error_message = response.json().get("detail", "Login failed")
            return render(request, "frontend/login.html", {"error": error_message})

    return render(request, "frontend/login.html")

def profile(request):
    token = request.session.get('token')
    if not token:
        return redirect('login')
    
    headers = {'Authorization': f'Bearer {token}'}
    logging.info(f"Fetching profile for token: {token}")
    
    response = requests.get(f"{FASTAPI_URL}/users/me/", headers=headers)
    logging.info(f"Profile response status code: {response.status_code}")
    logging.info(f"Profile response: {response.json()}")
    
    if response.status_code == 200:
        user_data = response.json()
        return render(request, "frontend/profile.html", {"user": user_data})
    else:
        return render(request, "frontend/profile.html", {"error": response.json().get("detail", "Unknown error")})

def register_with_anope(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        email = request.POST.get("email")
        
        if password1 != password2:
            return render(request, "frontend/register_with_anope.html", {"error": "Passwords do not match."})
        
        logging.info(f"Registering user with Anope: {username}")
        
        # Register user with Anope
        register_response = requests.post(f"{FASTAPI_URL}/register_with_anope/", json={
            "username": username,
            "password": password1,
            "email": email
        })
        logging.info(f"Anope register response status code: {register_response.status_code}")
        logging.info(f"Anope register response: {register_response.json()}")
        
        if register_response.status_code != 200:
            error_message = register_response.json().get("detail", "Registration failed")
            return render(request, "frontend/register_with_anope.html", {"error": error_message})
        
        # Authenticate user and get token
        token_response = requests.post(f"{FASTAPI_URL}/token/", json={
            "username": username,
            "password": password1
        })
        logging.info(f"Token response status code: {token_response.status_code}")
        logging.info(f"Token response: {token_response.json()}")
        
        if token_response.status_code == 200:
            token = token_response.json().get("access_token")
            request.session['token'] = token  # Store the token in the session
            request.session['password'] = password1  # Store the password in the session
            request.session['username'] = username  # Store the username in the session
            success_message = register_response.json().get("message", "Registration successful")
            return render(request, "frontend/register_with_anope.html", {"success": success_message})
        else:
            error_message = token_response.json().get("detail", "Token generation failed")
            return render(request, "frontend/register_with_anope.html", {"error": error_message})

    return render(request, "frontend/register_with_anope.html")

def chat_view(request):
    token = request.session.get('token')
    password = request.session.get('password')
    username = request.session.get('username')
    if not token or not password or not username:
        return redirect('login')
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{FASTAPI_URL}/users/me/", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        logging.info(f"User data: {user_data}")
        return render(request, "frontend/chat.html", {"username": username, "token": token, "password": password})
    else:
        return render(request, "frontend/chat.html", {"error": "Unable to fetch user data."})

def logout_view(request):
    if request.method == "POST":
        request.session.flush()  # Clear the session
        return redirect('home')

@csrf_exempt
def kiwiirc_config(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    username = request.user.username
    password = request.session.get('password')
    
    config = {
        
	"windowTitle": "Kiwi IRC - The web IRC client",
	"startupScreen": "customServer",
	"kiwiServer": "https://webchat.t-chat.fr/webirc/kiwiirc/",
	"restricted": false,
	"theme": "default",
	"themes": [
		{ "name": "Default", "url": "static/themes/default.css" }
	],
	"startupOptions" : {
		"server": "irc.tchatzone.fr",
		"port": 6697,
		"tls": true,
		"channel": "",
		"nick": ""
	},
	"embedly": {
		"key": ""
	},
	"plugins": []
}

    return JsonResponse(config)