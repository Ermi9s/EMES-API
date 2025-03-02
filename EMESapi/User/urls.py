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
    path('admin/register/', register_admin, name='register_admin'),

    path('register/' , register , name='register'),
    path('login/', login , name='login'),

    path('users/', get_users, name='get_users'),
    path('users/<int:user_id>/', get_users, name='get_user_details'),
    path('users/<int:user_id>/view-request/', create_view_request, name='create_view_request'),
    path('user/update/<str:action>/', UserRegistrationUpdates.as_view(), name='user_update'),


    path('admin/users/', fetch_users, name='fetch_users'), 
    path('admin/users/<int:user_id>/', fetch_users, name='fetch_user_by_id'), 
    path('admin/requests/<int:request_id>/approve/', approve_request, name='approve_request'),
    path('admin/requests/<int:request_id>/reject/', reject_request, name='reject_request'),

    path('admin/user/manage/<str:action>/<int:user_id>/', UserManagementView.as_view(), name='user_management'),

    path('', include(router.urls)),

    path('upload-receipt/', upload_receipt, name='upload_receipt'),
    path('upload-degree/', upload_degree, name='upload_degree'),
    path('upload-profile-picture/', upload_profile_picture, name='upload_profile_picture'),
]
