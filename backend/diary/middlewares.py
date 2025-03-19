from django.utils import timezone

from .models import Profile


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = Profile.objects.get_or_create(user=request.user)[0]
            if profile.timezone:
                timezone.activate(profile.timezone)
            else:
                timezone.deactivate()
        else:
            timezone.deactivate()

        return self.get_response(request)
