app_name = "tarification_granules"
app_title = "Tarification Granules"
app_publisher = "Mohamed kachtit"
app_description = "gestion des tarifs de granules par zone et remise"
app_email = "mokachtit@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "tarification_granules",
# 		"logo": "/assets/tarification_granules/logo.png",
# 		"title": "Tarification Granules",
# 		"route": "/tarification_granules",
# 		"has_permission": "tarification_granules.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tarification_granules/css/tarification_granules.css"
# app_include_js = "/assets/tarification_granules/js/tarification_granules.js"

# include js, css files in header of web template
# web_include_css = "/assets/tarification_granules/css/tarification_granules.css"
# web_include_js = "/assets/tarification_granules/js/tarification_granules.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tarification_granules/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "tarification_granules/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "tarification_granules.utils.jinja_methods",
# 	"filters": "tarification_granules.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "tarification_granules.install.before_install"
after_install = "tarification_granules.setup.install.after_install"

# Fixtures
# --------

# fixtures = [
#     {
#         "dt": "Workspace",
#         "filters": [["module", "=", "Tarification Granules"]]
#     }
# ]

# Uninstallation
# ------------

# before_uninstall = "tarification_granules.uninstall.before_uninstall"
# after_uninstall = "tarification_granules.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "tarification_granules.utils.before_app_install"
# after_app_install = "tarification_granules.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "tarification_granules.utils.before_app_uninstall"
# after_app_uninstall = "tarification_granules.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tarification_granules.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Order": {
        "before_validate": "tarification_granules.controllers.pricing_hooks.apply_pricing",
    },
    "Sales Invoice": {
        "before_validate": "tarification_granules.controllers.pricing_hooks.apply_pricing",
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"tarification_granules.tasks.all"
# 	],
# 	"daily": [
# 		"tarification_granules.tasks.daily"
# 	],
# 	"hourly": [
# 		"tarification_granules.tasks.hourly"
# 	],
# 	"weekly": [
# 		"tarification_granules.tasks.weekly"
# 	],
# 	"monthly": [
# 		"tarification_granules.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "tarification_granules.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tarification_granules.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "tarification_granules.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["tarification_granules.utils.before_request"]
# after_request = ["tarification_granules.utils.after_request"]

# Job Events
# ----------
# before_job = ["tarification_granules.utils.before_job"]
# after_job = ["tarification_granules.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"tarification_granules.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
