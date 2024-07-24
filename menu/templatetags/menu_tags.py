from django import template
from menu.models import Menu, MenuItem
from django.urls import reverse

register = template.Library()

@register.inclusion_tag('menu/draw_menu.html', takes_context=True)
def draw_menu(context, menu_name):
    request = context['request']
    try:
        menu = Menu.objects.get(name=menu_name)
    except Menu.DoesNotExist:
        return {'menu': [], 'current_url': request.path}

    menu_items = MenuItem.objects.filter(menu=menu).select_related('parent')

    def build_tree(items, parent=None):
        tree = []
        for item in items:
            if item.parent == parent:
                children = build_tree(items, item)
                tree.append({'item': item, 'children': children})
        return tree

    menu_tree = build_tree(menu_items)
    current_url = request.path

    def mark_active(items):
        for node in items:
            node['active'] = node['item'].url == current_url or node['item'].named_url == current_url
            if node['active']:
                for ancestor in items:
                    if ancestor['item'] == node['item'].parent:
                        ancestor['active'] = True
            mark_active(node['children'])

    mark_active(menu_tree)

    return {'menu': menu_tree, 'current_url': current_url}
