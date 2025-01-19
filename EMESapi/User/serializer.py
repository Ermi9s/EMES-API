from rest_framework import serializers
from .models import (
    User, Address, Contact, Education, ProfessionalExperience,
    Publications, Projects, Patents, Award, AnualMembershipFee, ViewRequests, Institution
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'full_name', 'sex', 'date_of_birth', 
            'nationality', 'is_Admin', 'address', 'contact', 
            'educational_background', 'professional_experience', 
            'projects', 'awards', 'publications', 'patents', 
            'Payment', 'verified'
        ]
        extra_kwargs = {'password': {'write_only': True}}


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'residential', 'employer', 'city', 'country']



class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'email', 'phone_number']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'id', 'highest_degree', 'field_of_study', 'university', 
            'graduation_year', 'specialization', 'degree_file'
        ]


class ProfessionalExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalExperience
        fields = [
            'id', 'organization', 'position', 'key_responsibilities', 
            'start_time', 'end_time'
        ]


class PublicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publications
        fields = ['id', 'title', 'jornal', 'date']


class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id', 'title', 'description', 'start', 'end']


class PatentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patents
        fields = ['id', 'title', 'description', 'date']

class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = ['id', 'title', 'awarding_body', 'year']


class AnualMembershipFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnualMembershipFee
        fields = ['id', 'receipt', 'status']


class ViewRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewRequests
        fields = ['id', 'issuer', 'requested_user']


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'name', 'address', 'contact', 'services_or_productions', 'payment']
