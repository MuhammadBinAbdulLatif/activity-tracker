from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
from django.shortcuts import redirect

def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return HttpResponse(
        f"""
        <!DOCTYPE html>
        <html lang="en" class="dark">
        <head>
            <meta charset="UTF-8">
            <title>uTrack - Dashboard</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-black text-zinc-100 min-h-screen flex flex-col items-center justify-center p-6">
            <div class="max-w-md w-full bg-zinc-950 border border-zinc-800 rounded-xl p-8 text-center space-y-4">
                <h1 class="text-2xl font-bold tracking-tight">Welcome, {request.user.username}!</h1>
                <p class="text-zinc-400 text-sm">You are signed in to uTrack. The core tracking modules and home dashboard are up next on our roadmap.</p>
                <form action="/accounts/logout/" method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{request.COOKIES.get('csrftoken', '')}">
                    <button type="submit" class="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-sm font-medium rounded-lg transition-colors">
                        Sign Out
                    </button>
                </form>
            </div>
        </body>
        </html>
        """
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', home_view, name='home'),
]
