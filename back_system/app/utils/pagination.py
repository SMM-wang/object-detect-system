from app.errors import ValidationError


def parse_pagination(args):
    try:
        page = int(args.get("page", 1))
        page_size = int(args.get("pageSize", 10))
    except ValueError as exc:
        raise ValidationError("分页参数必须为整数") from exc
    if page < 1:
        raise ValidationError("page 必须大于 0")
    if page_size < 1:
        raise ValidationError("pageSize 必须大于 0")
    return page, min(page_size, 100)


def paginate_query(query, page, page_size):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, items
