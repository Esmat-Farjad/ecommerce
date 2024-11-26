def breadcrumbs(request):
    # Check if 'breadcrumbs' exists in the request and return it
    if hasattr(request, 'breadcrumbs'):
        return {'breadcrumbs': request.breadcrumbs}
    return {'breadcrumbs': []}  # Default to an empty list if not set