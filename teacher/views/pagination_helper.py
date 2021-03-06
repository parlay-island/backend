from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

BODY = 'body'
TIMES_ANSWERED = 'times_answered'
TIMES_CORRECT = 'times_correct'
TIMES_CHOSEN = 'times_chosen'
TAGS = 'tags'
ANSWER = 'answer'
TAG = 'tag'


class BadRequestException(Exception):
    pass


def get_paginated_results(results, num_items_per_page, page_number=1):
    paginator = Paginator(results, num_items_per_page)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page.object_list


