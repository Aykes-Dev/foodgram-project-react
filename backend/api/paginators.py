from rest_framework.pagination import PageNumberPagination


class PaginationForRecipe(PageNumberPagination):
    page_size_query_param = 'limit'
