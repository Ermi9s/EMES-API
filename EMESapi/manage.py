# #!/usr/bin/env python
# """Django's command-line utility for administrative tasks."""
# import os
# import sys


# def main():
#     """Run administrative tasks."""
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EMESapi.settings')
#     try:
#         from django.core.management import execute_from_command_line
#     except ImportError as exc:
#         raise ImportError(
#             "Couldn't import Django. Are you sure it's installed and "
#             "available on your PYTHONPATH environment variable? Did you "
#             "forget to activate a virtual environment?"
#         ) from exc
#     execute_from_command_line(sys.argv)


# if __name__ == '__main__':
#     main()

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EMESapi.settings')
    try:
        from django.core.management import execute_from_command_line
        from django.contrib.auth import get_user_model
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Check for the `create_superuser` argument
    if len(sys.argv) > 1 and sys.argv[1] == 'create_superuser':
        User = get_user_model()
        username = 'superadmin'
        email = 'admin@example.com'
        password = '1234'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"Superuser '{username}' created successfully.")
        else:
            print(f"Superuser '{username}' already exists.")
        return  # Exit after creating the superuser

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

