from math import ceil

from flask import request, url_for


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page

    for arg_name, arg_value in request.args.to_dict().items():
        args[arg_name] = arg_value

    return url_for(request.endpoint, **args)


def url_for_search():
    args = request.view_args.copy()
    if 'page' in args:
        del args['page']
    return url_for(request.endpoint, **args)


class Pagination(object):

    def __init__(self, page, per_page, total_count, filter_text=None):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
        self.filter_text = filter_text

    @property
    def current_page(self):
        return self.page

    @property
    def amount_elements(self):
        return self.total_count

    @property
    def page_length(self):
        return self.per_page

    @property
    def num_first_el_on_page(self):
        if self.total_count > 0:
            return (self.page - 1) * self.per_page + 1
        else:
            return 0

    @property
    def num_last_el_on_page(self):
        return min(self.page * self.per_page, self.total_count)

    @property
    def filter(self):
        return self.filter_text

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (self.page - left_current - 1 < num < self.page + right_current) or \
                    num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

    def get_page_data(self, data):
        return data[(self.page - 1) * self.per_page: self.page * self.per_page]
