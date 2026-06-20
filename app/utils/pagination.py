def paginate(page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    limit = page_size
    return offset, limit