from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import HttpResponse
from social.exceptions import AuthCanceled


class ErrorMiddleware(SocialAuthExceptionMiddleware):

    def process_exception(self, request, exception):
        if isinstance(exception, AuthCanceled):
            return HttpResponse("I'm the Pony %s" % exception)
        return super(ErrorMiddleware, self).process_exception(request, exception)
