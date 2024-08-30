from starlette_admin.contrib.sqlmodel import ModelView

from src.models import Site


class SiteView(ModelView):
    fields = [
        Site.id,
        Site.user_id,
        Site.name,
        Site.description,
        Site.created_on,
        Site.updated_on,
    ]
    exclude_fields_from_list = [Site.description]
    exclude_fields_from_create = [Site.id, Site.created_on, Site.updated_on]
    exclude_fields_from_edit = [Site.id, Site.created_on, Site.updated_on]
    sortable_fields = [Site.name, Site.created_on, Site.updated_on]
    searchable_fields = [Site.id, Site.name]
    fields_default_sort = [Site.name, (Site.created_on, True)]
