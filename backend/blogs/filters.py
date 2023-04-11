from rest_framework import filters


# class CategoryFilter(filters.FilterSet):
#     name = filters.CharFilter(field_name="name", lookup_expr="iexact")
#
#     class Meta:
#         model = Category
#         fields = ["name"]


class CategoryFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        if request.query_params.get("name"):
            return ["name"]
        return super().get_search_fields(view, request)
