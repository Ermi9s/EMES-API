from django.urls import include, path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'addresses', AddressViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'educations', EducationViewSet)
router.register(r'professional_experiences', ProfessionalExperienceViewSet)
router.register(r'publications', PublicationsViewSet)
router.register(r'projects', ProjectsViewSet)
router.register(r'patents', PatentsViewSet)
router.register(r'awards', AwardViewSet)
router.register(r'annual_membership_fees', AnualMembershipFeeViewSet)


urlpatterns = [
    path('register/' , register , name='register'),
    path('login/', login , name='login'),

    path('users/', UserFetch.as_view(), name='user_list'),
    path('users/<int:user_id>/', UserFetch.as_view(), name='user_detail'),
    path('user/<int:user_id>/', UserFetch.as_view(), name='user_fetch'),
    path('user/update/<str:action>/', UserRegistrationUpdates.as_view(), name='user_update'),

    path('admin/users/', AdminUserView.as_view(), name='admin_user_list'),
    path('admin/users/<int:user_id>/', AdminUserView.as_view(), name='admin_user_detail'),
    path('admin/users/status/<str:status_filter>/', AdminUserView.as_view(), name='admin_user_by_status'),
    path('admin/user/manage/<str:action>/<int:user_id>/', UserManagementView.as_view(), name='user_management'),
    path('admin/approve-request/<int:request_id>/', AdminUserView.as_view(), name='approve_request'),

    path('/', include(router.urls)),
]
