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

from .models import (
    User, Address, Contact, Education, ProfessionalExperience,
    Publications, Projects, Patents, Award, AnnualMembershipFee, ViewRequests,
)
from .serializer import (
    UserSerializer, AddressSerializer, ContactSerializer, EducationSerializer,
    ProfessionalExperienceSerializer, PublicationsSerializer, ProjectsSerializer,
    PatentsSerializer, AwardSerializer, AnualMembershipFeeSerializer,
)


@permission_classes([AllowAny])
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data, partial = True)

        if serializer.is_valid():
            password = serializer.validated_data.get('password')
            if password:
                hashed_password = make_password(password)
                serializer.validated_data['password'] = hashed_password
            user = serializer.save()
            token = Token.objects.create(user=user)

            return Response(
                {
                    "token" : token.key,
                    "user" : serializer.data,
                    "message" : "User created successfully",
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

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


class UserFetch(APIView):
    serializer_class = UserSerializer

    def get(self, request, user_id=None):
 
        fields_to_return = ["id", "username", "full_name", "nationality"]

        if user_id:
            user = get_object_or_404(User, id=user_id)
            # Serialize only the allowed fields
            user_data = {field: getattr(user, field, None) for field in fields_to_return}
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            users = User.objects.filter(verified=True)
            users_data = [
                {field: getattr(user, field, None) for field in fields_to_return} 
                for user in users
            ]
            return Response(users_data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
            """
            Create a request to view a user's full information.
            Only verified users can make this request.
            """

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

            view_request = ViewRequests.objects.create(
                issuer=requesting_user,
                requested_user=user_to_view
            )

            return Response(
                {"message": f"Request to view {user_to_view.username}'s full information has been sent."},
                status=status.HTTP_201_CREATED
            )

class AdminUserView(APIView):
    permission_classes = [IsAuthenticated , IsAdminUser] 
    serializer_class = UserSerializer

    def get(self, request, user_id=None, status_filter=None):
        """
        Fetch users with different filters:
        - Fetch all users (admin only).
        - Fetch only verified users (admin only).
        - Fetch only unverified users (admin only).
        """

        if user_id:
            user = get_object_or_404(User, id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif status_filter:
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
    

    def delete(self, request, request_id):
        """
        Admin approves the request to view a user's full information.
        Once approved, send an email to the requesting user and delete the request.
        """
     
        view_request = get_object_or_404(ViewRequests, id=request_id)
        requested_user = view_request.requested_user

        full_info = {
            'full_name': requested_user.full_name,
            'sex': requested_user.sex,
            'date_of_birth': requested_user.date_of_birth,
            'nationality': requested_user.nationality,
            'address': requested_user.address,
            'contact': requested_user.contact,
            'education': requested_user.educational,
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
            {"message": "Request granted and email sent to the requester."},
            status=status.HTTP_200_OK
        )
    
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


class PatentsViewSet(viewsets.ModelViewSet):
    queryset = Patents.objects.all()
    serializer_class = PatentsSerializer
    permission_classes = [IsOwnerOrAdmin]


class AwardViewSet(viewsets.ModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    permission_classes = [IsOwnerOrAdmin]

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

