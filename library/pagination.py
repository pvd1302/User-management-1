from flask.json import jsonify


def calculate_pagination(total_records, page, per_page):
    if total_records % per_page != 0:
        total_pages = (total_records // per_page) + 1
    if total_records % per_page == 0:
        total_pages = total_records // per_page
    # if page > total_pages:
    #     return jsonify('Invalid pagination parameters')
    # if page < 1:
    #     return jsonify('Invalid pagination parameters')

    next_page = page + 1
    if next_page > total_pages:
        next_page = 'null'
    prev_page = page - 1
    if prev_page == 0:
        prev_page = 'null'

    return {
        'total_pages': total_pages,
        'next_page': next_page,
        'prev_page': prev_page,
    }
