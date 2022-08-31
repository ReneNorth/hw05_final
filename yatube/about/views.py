from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'
#    return render(request, 'about/author.html', name='author')


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
#    return render(request, 'about/tech.html', name='tech')
