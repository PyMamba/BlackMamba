# Controllers should be placed here

HOME, GET_STARTED, DOCUMENTATION, DOWNLOAD, BLOG, CONTACT = range(6)

template_args = {
    'menu': True,
    'menu_options': [
        {'path': '/', 'label': 'Home', 'active': False, 'available': True},
        {
            'path': 'gettingstart', 'label': 'Get started',
            'active': False, 'available': True
        },
        {
            'path': 'docs', 'label': 'Documentation',
            'active': False, 'available': True
        },
        {
            'path': 'download', 'label': 'Download',
            'active': False, 'available': True
        },
        {'path': 'blog', 'label': 'Blog', 'active': False, 'available': True},
        {
            'path': 'contact', 'label': 'Contact',
            'active': True, 'available': True
        },
    ]
}


def toggle_menu(menu_entry):
    """
    Toggle all the active state menus that are not the given menu entry to
    inactive and set the given one as active

    :param menu_entry: the menu entry to active
    :type menu_entry: dict
    """

    menu = template_args['menu_options'][menu_entry]
    if menu['available'] is False:
        return

    for item in template_args['menu_options']:
        if item['active']:
            if item == menu:
                continue

            item['active'] = False

    menu['active'] = True
