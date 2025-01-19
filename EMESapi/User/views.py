from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (
    User, Address, Contact, Education, ProfessionalExperience,
    Publications, Projects, Patents, Award, AnualMembershipFee, ViewRequests, Institution
)
from .serializer import (
    UserSerializer, AddressSerializer, ContactSerializer, EducationSerializer,
    ProfessionalExperienceSerializer, PublicationsSerializer, ProjectsSerializer,
    PatentsSerializer, AwardSerializer, AnualMembershipFeeSerializer, ViewRequestsSerializer,
    InstitutionSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        """
        Override the create method to handle user registration.
        This includes password hashing and custom validation.
        """
        data = request.data

        # Ensure password confirmation matches (if provided)
        if data.get("password") != data.get("confirm_password"):
            return Response(
                {"error": "Passwords do not match."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Hash the password before saving
        user = serializer.save(password=make_password(data["password"]))
        return Response(
            {"message": "User created successfully.", "user": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """
        Override the update method to allow partial updates (e.g., change password or email).
        """
        user = self.get_object()
        data = request.data

        if "password" in data:
            user.set_password(data["password"])
        if "email" in data:
            user.email = data["email"]

        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "User updated successfully.", "user": serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def verify_user(self, request, pk=None):
        """
        Custom action to verify a user.
        """
        user = self.get_object()
        if user.verified:
            return Response({"message": "User is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        user.verified = True
        user.save()
        return Response({"message": "User verified successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def deactivate_user(self, request, pk=None):
        """
        Custom action to deactivate a user account.
        """
        user = self.get_object()
        if not user.is_active:
            return Response({"message": "User is already deactivated."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = False
        user.save()
        return Response({"message": "User account deactivated successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def activate_user(self, request, pk=None):
        """
        Custom action to activate a user account.
        """
        user = self.get_object()
        if user.is_active:
            return Response({"message": "User is already active."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()
        return Response({"message": "User account activated successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def verified_users(self, request):
        """
        List all verified users.
        """
        verified_users = User.objects.filter(verified=True)
        serializer = self.get_serializer(verified_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def active_users(self, request):
        """
        List all active users.
        """
        active_users = User.objects.filter(is_active=True)
        serializer = self.get_serializer(active_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def create(self, request, *args, **kwargs):
        # Validate and create an address
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

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

    @action(detail=False, methods=['get'])
    def highest_degree(self, request):
        # Retrieve users with the highest degree
        education = Education.objects.order_by('-graduation_year').first()
        serializer = self.get_serializer(education)
        return Response(serializer.data)


class ProfessionalExperienceViewSet(viewsets.ModelViewSet):
    queryset = ProfessionalExperience.objects.all()
    serializer_class = ProfessionalExperienceSerializer

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

    @action(detail=False, methods=['get'])
    def active_projects(self, request):
        # Return projects that are still active
        active_projects = Projects.objects.filter(end__isnull=True)
        serializer = self.get_serializer(active_projects, many=True)
        return Response(serializer.data)


class PatentsViewSet(viewsets.ModelViewSet):
    queryset = Patents.objects.all()
    serializer_class = PatentsSerializer


class AwardViewSet(viewsets.ModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer


class AnualMembershipFeeViewSet(viewsets.ModelViewSet):
    queryset = AnualMembershipFee.objects.all()
    serializer_class = AnualMembershipFeeSerializer

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


class ViewRequestsViewSet(viewsets.ModelViewSet):
    queryset = ViewRequests.objects.all()
    serializer_class = ViewRequestsSerializer


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer

    @action(detail=False, methods=['get'])
    def by_service(self, request):
        # Filter institutions by services or productions offered
        service = request.query_params.get('service', None)
        if service:
            institutions = Institution.objects.filter(services_or_productions__icontains=service)
            serializer = self.get_serializer(institutions, many=True)
            return Response(serializer.data)
        return Response({"error": "Service parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
