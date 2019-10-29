#work in progress
# https://www.vinta.com.br/blog/2015/basic-seo-django/
# https://overiq.com/django-1-11/creating-sitemaps-in-django/


'''
class MySiteSitemap(Sitemap):
    changfreq = 'always'

    def items(self):
        return Question.objects.all()

    def lastmod(self, item):
        last_answer = Answer.objects.filter(question=item)
        if last_answer:
            return sorted(last_answer)[-1].date
'''