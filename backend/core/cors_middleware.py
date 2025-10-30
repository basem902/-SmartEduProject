"""
Custom CORS Middleware - Direct implementation to fix Render deployment
"""

class CorsMiddleware:
    """
    Custom CORS middleware that adds necessary headers directly
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = self._build_preflight_response()
            return response

        # Get response from next middleware/view
        response = self.get_response(request)
        
        # Add CORS headers to response
        self._add_cors_headers(response, request)
        
        return response

    def _build_preflight_response(self):
        """Build response for OPTIONS preflight request"""
        from django.http import HttpResponse
        response = HttpResponse()
        response.status_code = 200
        return response

    def _add_cors_headers(self, response, request):
        """Add CORS headers to response"""
        origin = request.META.get('HTTP_ORIGIN')
        
        # Allow all origins for now (we can restrict later)
        if origin:
            response['Access-Control-Allow-Origin'] = origin
        else:
            response['Access-Control-Allow-Origin'] = '*'
        
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Accept, Accept-Encoding, Authorization, Content-Type, DNT, Origin, User-Agent, X-CSRFToken, X-Requested-With'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'
        
        return response
