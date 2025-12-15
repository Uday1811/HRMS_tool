"""
horilla/config.py

Petabytz app configurations
"""

import importlib
import logging

from django.apps import apps
from django.conf import settings
from django.contrib.auth.context_processors import PermWrapper

from horilla.horilla_apps import SIDEBARS

logger = logging.getLogger(__name__)


def get_apps_in_base_dir():
    return SIDEBARS


def import_method(accessibility):
    module_path, method_name = accessibility.rsplit(".", 1)
    module = __import__(module_path, fromlist=[method_name])
    accessibility_method = getattr(module, method_name)
    return accessibility_method


ALL_MENUS = {}


def sidebar(request):
    base_dir_apps = get_apps_in_base_dir()

    if not request.user.is_anonymous:
        request.MENUS = []
        MENUS = request.MENUS

        # Check if user is a regular employee using Employee model lookup
        from employee.models import Employee
        
        try:
            employee_obj = Employee.objects.get(employee_user_id=request.user)
            # Employee is someone who has an Employee record but is not superuser or staff
            is_employee = not request.user.is_superuser and not request.user.is_staff
        except Employee.DoesNotExist:
            is_employee = False

        if is_employee:
            # Employee simplified sidebar
            employee_menus = [
                {
                    "menu": "Me",
                    "app": "employee_profile",
                    "img_src": "images/ui/employee.png",
                    "submenu": [],
                    "redirect": "/employee/employee-profile/"
                },
                {
                    "menu": "My Team",
                    "app": "my_team",
                    "img_src": "images/ui/employees.svg",
                    "submenu": [],
                    "redirect": "/employee/employee-view/"
                },
                {
                    "menu": "Leaves",
                    "app": "leaves",
                    "img_src": "images/ui/leave.svg",
                    "submenu": [],
                    "redirect": "/employee/leaves-dashboard/"
                },
                {
                    "menu": "Finance",
                    "app": "finance",
                    "img_src": "images/ui/wallet-outline.svg",
                    "submenu": [],
                    "redirect": "/employee/finance-dashboard/"
                },
                {
                    "menu": "Employee Handbook",
                    "app": "handbook",
                    "img_src": "images/ui/document.png",
                    "submenu": [],
                    "redirect": "/employee/handbook-dashboard/"
                },
                {
                    "menu": "Policy",
                    "app": "policy",
                    "img_src": "images/ui/legal.png",
                    "submenu": [],
                    "redirect": "/employee/policy-dashboard/"
                }
            ]
            MENUS.extend(employee_menus)
        else:
            # Admin/Staff full sidebar
            for app in base_dir_apps:
                if apps.is_installed(app):
                    try:
                        sidebar = importlib.import_module(app + ".sidebar")

                    except Exception as e:
                        logger.error(e)
                        continue

                    if sidebar:
                        accessibility = None
                        if getattr(sidebar, "ACCESSIBILITY", None):
                            accessibility = import_method(sidebar.ACCESSIBILITY)

                        if not accessibility or accessibility(
                            request,
                            sidebar.MENU,
                            PermWrapper(request.user),
                        ):
                            MENU = {}
                            MENU["menu"] = sidebar.MENU
                            MENU["app"] = app
                            MENU["img_src"] = sidebar.IMG_SRC
                            MENU["submenu"] = []
                            MENUS.append(MENU)
                            for submenu in sidebar.SUBMENUS:

                                accessibility = None

                                if submenu.get("accessibility"):
                                    accessibility = import_method(submenu["accessibility"])
                                redirect: str = submenu["redirect"]
                                redirect = redirect.split("?")
                                submenu["redirect"] = redirect[0]

                                if not accessibility or accessibility(
                                    request,
                                    submenu,
                                    PermWrapper(request.user),
                                ):
                                    MENU["submenu"].append(submenu)
        ALL_MENUS[request.session.session_key] = MENUS


def get_MENUS(request):
    ALL_MENUS[request.session.session_key] = []
    sidebar(request)
    return {"sidebar": ALL_MENUS.get(request.session.session_key)}
