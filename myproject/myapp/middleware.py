# /myproject/myapp/middleware.py

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class AuthenticationMiddleware:
    """
    Middleware to handle authentication requirements for specific paths.
    Redirects unauthenticated users to the login page with a message.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Paths that require authentication
        self.auth_required_paths = [
            '/dashboard/',
            '/exercise-plan/',
            '/meal-plan/',
            '/progress/',
            '/orders/',
            '/profile/',
            '/wishlist/',
            '/support/',
            '/nutrition-plan/',
            '/my-subscriptions/',
        ]
        
    def __call__(self, request):
        # Check if the path requires authentication
        path = request.path
        requires_auth = any(path.startswith(auth_path) for auth_path in self.auth_required_paths)
        
        if requires_auth and not request.user.is_authenticated:
            # Store the current path to redirect back after login
            next_url = request.get_full_path()
            
            # Add a message to inform the user why they are being redirected
            messages.info(request, 'กรุณาเข้าสู่ระบบเพื่อเข้าถึงหน้านี้')
            
            # Redirect to login page with next parameter
            return redirect(f"{reverse('login')}?next={next_url}")
        
        # Continue processing the request
        response = self.get_response(request)
        return response