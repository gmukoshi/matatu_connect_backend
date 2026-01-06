def paginate(query, page=1, per_page=10):
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return {
        "items": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }
