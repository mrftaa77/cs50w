from django.template.defaulttags import register

@register.filter
def bid_from_maxbid(dictionary, key):
    return dictionary.get(key)


@register.filter
def bid_from_maxbids(dictionary, key):
    return dictionary.get(key).bid