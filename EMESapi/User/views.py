from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes,action
from utils.emailbody import generate_html_email_body
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from utils.permisions import IsOwnerOrAdmin
from django.core.files.storage import default_storage
from rest_framework.exceptions import NotFound

from .models import (
    User, Address, Contact, Education, ProfessionalExperience,
    Publications, Projects, Patents, Award, AnnualMembershipFee, ViewRequests,
)
from .serializer import (
    UserSerializer, AddressSerializer, ContactSerializer, EducationSerializer,
    ProfessionalExperienceSerializer, PublicationsSerializer, ProjectsSerializer,
    PatentsSerializer, AwardSerializer, AnualMembershipFeeSerializer,
)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_admin(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username  or not password:
        return Response(
            {"message": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )


    if User.objects.filter(username=username).exists():
        return Response(
            {"message": "A user with this username already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            verified=True, 
            is_staff=True,
        )
    except Exception as e:
        return Response(
            {"message": f"Error creating user: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {"message": f"User {user.username} has been successfully registered as an admin."},
        status=status.HTTP_201_CREATED
    )


@csrf_exempt
@permission_classes([AllowAny])
@api_view(['POST'])
def register(request):
    if request.method == 'POST':

        data = request.data.copy()

        is_organization = request.query_params.get('is_organization', 'false').lower() == 'true'
        data['is_organization'] = is_organization  # Add or modify is_organization

        serializer = UserSerializer(data=data, partial=True)

        if serializer.is_valid():

            password = serializer.validated_data.get('password')
            if password:
                hashed_password = make_password(password)
                serializer.validated_data['password'] = hashed_password

        
            user = serializer.save()

        
            token = Token.objects.create(user=user)

            return Response(
                {
                    "token": token.key,
                    "user": serializer.data,
                    "message": "User created successfully",
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

@csrf_exempt
@permission_classes([AllowAny])
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        # print(password , user)
        if user is not None:
            token,_ = Token.objects.get_or_create(user=user)
            data = UserSerializer(user).data
            return Response(
                {
                    "token" : token.key,
                    "user" : data,
                    "message" : "login successful",
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "message" : "login failed",
            },
            status=status.HTTP_400_BAD_REQUEST
        )

@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationUpdates(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class =  UserSerializer

    def post(self, request, action):
        user = request.user
        if not user:
            return Response(
                {"message": "User not found with token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        actions_map = {
            "add_address": (AddressSerializer, "address"),
            "add_contact": (ContactSerializer, "contact"),
            "add_education": (EducationSerializer, "educational_background"),
            "add_professional_experience": (ProfessionalExperienceSerializer, "professional_experience"),
            "add_projects": (ProjectsSerializer, "projects"),
            "add_awards": (AwardSerializer, "awards"),
            "add_publications": (PublicationsSerializer, "publications"),
            "add_patents": (PatentsSerializer, "patents"),
            "add_payment": (AnualMembershipFeeSerializer, "payment"),
        }

        if action not in actions_map:
            return Response(
                {"message": "Invalid action"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer_class, user_field = actions_map[action]
        serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            saved_instance = serializer.save()
            setattr(user, user_field, saved_instance) 
            user.save()
            return Response(
                {"message": f"{action.replace('_', ' ').title()} added successfully"},
                status=status.HTTP_202_ACCEPTED
            )

        return Response(
            {"message": "Serializer failed", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def get_users(request, user_id=None):
    fields_to_return = ["id", "username", "full_name", "nationality" , "sex"]

    organization_filter = request.query_params.get('organization', None)

    if user_id:
        user = get_object_or_404(User, id=user_id)
        user_data = {field: getattr(user, field, None) for field in fields_to_return}
        return Response(user_data, status=status.HTTP_200_OK)
    else:
        users = User.objects.filter(verified=True, is_staff=False)

        if organization_filter:
            if organization_filter.lower() == 'true':
                users = users.filter(is_organization=True)
            elif organization_filter.lower() == 'false':
                users = users.filter(is_organization=False)
            else:
                return Response({"detail": "Invalid 'organization' filter. Use 'true' or 'false'."}, status=status.HTTP_400_BAD_REQUEST)

        users_data = [
            {field: getattr(user, field, None) for field in fields_to_return}
            for user in users
        ]

        return Response(users_data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_view_request(request, user_id):

    requesting_user = request.user
    if not requesting_user.verified:
        return Response(
            {"message": "You must be a verified user to request full information."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user_to_view = get_object_or_404(User, id=user_id)

    existing_request = ViewRequests.objects.filter(
        issuer=requesting_user, requested_user=user_to_view
    ).exists()

    if existing_request:
        return Response(
            {"message": "You have already made a request to view this user's full information."},
            status=status.HTTP_400_BAD_REQUEST
        )

    _ = ViewRequests.objects.create(
        issuer=requesting_user,
        requested_user=user_to_view
    )

    return Response(
        {"message": f"Request to view {user_to_view.username}'s full information has been sent."},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def fetch_users(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    status_filter = request.query_params.get('status', None)

    if status_filter:
        if status_filter == "verified":
            users = User.objects.filter(verified=True)
        elif status_filter == "unverified":
            users = User.objects.filter(verified=False)
        else:
            return Response(
                {"message": "Invalid status filter. Use 'verified' or 'unverified'."},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        users = User.objects.all()

    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def approve_request(request, request_id):

    view_request = get_object_or_404(ViewRequests, id=request_id)
    requested_user = view_request.requested_user

    full_info = {
        'full_name': requested_user.full_name,
        'sex': requested_user.sex,
        'date_of_birth': requested_user.date_of_birth,
        'nationality': requested_user.nationality,
        'address': requested_user.address,
        'contact': requested_user.contact,
        'education': requested_user.educational_background,
        'professional_experience': requested_user.professional_experience,
        'projects': requested_user.projects,
        'awards': requested_user.awards,
        'publications': requested_user.publications,
        'patents': requested_user.patents,
    }

    issuer_email = view_request.issuer.contact.email
    admin_email = request.user.contact.email

    html_body = generate_html_email_body(full_info)


    send_mail(
        subject="Your Requested User Information",
        message='',
        from_email=admin_email,
        recipient_list=[issuer_email],
        html_message=html_body,
    )

    view_request.delete()

    return Response(
        {"message": "Request approved and email sent to the requester."},
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def reject_request(request, request_id):
    view_request = get_object_or_404(ViewRequests, id=request_id)

    view_request.delete()

    return Response(
        {"message": "Request rejected successfully."},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_receipt(request):
    if request.method == 'POST':
        if 'receipt' not in request.FILES:
            return Response({'error': 'No receipt file provided'}, status=400)

        receipt_file = request.FILES['receipt']

        file_path = default_storage.save(f'receipt/{receipt_file.name}', receipt_file)

        receipt_url = f'{settings.MEDIA_URL}{file_path}'

        fee = AnnualMembershipFee.objects.create(
            receipt_url=receipt_url,
            status='Pending'  
        )

        serializer = AnualMembershipFeeSerializer(fee)
        return Response(serializer.data, status=201)

    return Response({'error': 'Invalid request'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_degree(request):
    if 'degree_file' not in request.FILES:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    degree_file = request.FILES['degree_file']

    file_path = default_storage.save(f'degrees/{degree_file.name}', degree_file)

    degree_file_url = f'{settings.MEDIA_URL}{file_path}'

    education = Education.objects.create(
        highest_degree=request.data.get('highest_degree', ''),
        field_of_study=request.data.get('field_of_study', ''),
        university=request.data.get('university', ''),
        graduation_year=request.data.get('graduation_year', ''),
        specialization=request.data.get('specialization', ''),
        degree_file=degree_file_url
    )

    serializer = EducationSerializer(education)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):

    user = request.user

    if 'profile_picture' in request.FILES:
        profile_picture_file = request.FILES['profile_picture']

        file_path = default_storage.save(f'profile_pictures/{profile_picture_file.name}', profile_picture_file)
        profile_picture_url = f'{settings.MEDIA_URL}{file_path}'

        user.profile_picture = profile_picture_url
        user.save()

        return Response({
            'message': 'Profile picture uploaded successfully',
            'profile_picture_url': profile_picture_url
        }, status=200)
    
    return Response({'error': 'No profile picture provided'}, status=400)   


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_pending_receipts(request):
  
    pending_fees = AnnualMembershipFee.objects.filter(status='Pending')

    serializer = AnualMembershipFeeSerializer(pending_fees, many=True)

    return Response(serializer.data, status=200)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_receipt_status(request, receipt_id):
    try:
        fee = AnnualMembershipFee.objects.get(id=receipt_id)
    except AnnualMembershipFee.DoesNotExist:
        raise NotFound('Receipt not found')

    fee.status = 'Accepted'
    fee.save()

    serializer = AnualMembershipFeeSerializer(fee)
    return Response(serializer.data, status=200)

class UserManagementView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserSerializer

    def patch(self, request, action, user_id):
        user = get_object_or_404(User, id=user_id)

        if action == "verify_user":
            if user.verified:
                return Response(
                    {"message": "User is already verified."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.verified = True
            user.save()
            return Response(
                {"message": f"User {user.username} has been verified successfully."},
                status=status.HTTP_200_OK
            )

        elif action == "make_admin":
            if user.is_admin:
                return Response(
                    {"message": "User is already an admin."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.is_staff = True
            user.save()
            return Response(
                {"message": f"User {user.username} has been promoted to admin successfully."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"message": "Invalid action. Use 'verify_user' or 'make_admin'."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
@method_decorator(csrf_exempt, name='dispatch')
class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsOwnerOrAdmin]

    def create(self, request, *args, **kwargs):
        # Validate and create an address
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsOwnerOrAdmin]

    def update(self, request, *args, **kwargs):
        # Custom logic for updating contact details
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [IsOwnerOrAdmin]

    @action(detail=False, methods=['get'])
    def highest_degree(self, request):
        # Retrieve users with the highest degree
        education = Education.objects.order_by('-graduation_year').first()
        serializer = self.get_serializer(education)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class ProfessionalExperienceViewSet(viewsets.ModelViewSet):
    queryset = ProfessionalExperience.objects.all()
    serializer_class = ProfessionalExperienceSerializer
    permission_classes = [IsOwnerOrAdmin]

    @action(detail=False, methods=['get'])
    def by_organization(self, request):
        # Filter experiences by organization name
        organization = request.query_params.get('organization', None)
        if organization:
            experiences = ProfessionalExperience.objects.filter(organization__icontains=organization)
            serializer = self.get_serializer(experiences, many=True)
            return Response(serializer.data)
        return Response({"error": "Organization parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class PublicationsViewSet(viewsets.ModelViewSet):
    queryset = Publications.objects.all()
    serializer_class = PublicationsSerializer
    permission_classes = [IsOwnerOrAdmin]

    @action(detail=False, methods=['get'])
    def by_year(self, request):
        # Filter publications by year
        year = request.query_params.get('year', None)
        if year:
            publications = Publications.objects.filter(date__year=year)
            serializer = self.get_serializer(publications, many=True)
            return Response(serializer.data)
        return Response({"error": "Year parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class ProjectsViewSet(viewsets.ModelViewSet):
    queryset = Projects.objects.all()
    serializer_class = ProjectsSerializer
    permission_classes = [IsOwnerOrAdmin]

    @action(detail=False, methods=['get'])
    def active_projects(self, request):
        # Return projects that are still active
        active_projects = Projects.objects.filter(end__isnull=True)
        serializer = self.get_serializer(active_projects, many=True)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class PatentsViewSet(viewsets.ModelViewSet):
    queryset = Patents.objects.all()
    serializer_class = PatentsSerializer
    permission_classes = [IsOwnerOrAdmin]

@method_decorator(csrf_exempt, name='dispatch')
class AwardViewSet(viewsets.ModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    permission_classes = [IsOwnerOrAdmin]
@method_decorator(csrf_exempt, name='dispatch')
class AnualMembershipFeeViewSet(viewsets.ModelViewSet):
    queryset = AnnualMembershipFee.objects.all()
    serializer_class = AnualMembershipFeeSerializer
    permission_classes = [IsOwnerOrAdmin]

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        # Update the status of the membership fee
        fee = self.get_object()
        new_status = request.data.get('status', None)
        if new_status:
            fee.status = new_status
            fee.save()
            return Response({"message": "Status updated successfully."})
        return Response({"error": "Status field is required."}, status=status.HTTP_400_BAD_REQUEST)

