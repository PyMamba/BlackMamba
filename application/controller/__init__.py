# Controllers should be placed here

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
            'active': False, 'available': False
        },
        {'path': 'blog', 'label': 'Blog', 'active': False, 'available': True},
        {
            'path': 'contact', 'label': 'Contact',
            'active': True, 'available': True
        },
    ]
}
