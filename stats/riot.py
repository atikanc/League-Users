from django.http import HttpResponse
import environ

def read_file(request):
    env = environ.Env()
    environ.Env.read_env()
    key = env('RIOT_CONFIRM')
    return HttpResponse(key, content_type="text/plain")