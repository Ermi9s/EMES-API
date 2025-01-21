from rest_framework import serializers
from .models import (
    User, Address, Contact, Education, ProfessionalExperience,
    Publications, Projects, Patents, Award, AnnualMembershipFee, ViewRequests
)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'full_name', 'sex', 'date_of_birth', 
            'nationality', 'address', 'contact', 
            'education', 'professional_experience','services_or_productions',
            'projects', 'awards', 'publications', 'patents', 
            'payment', 'verified'
        ]
        extra_kwargs = {'password': {'write_only': True}}

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'



class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'email', 'phone_number']


class EducationSerializer(serializers.ModelSerializer):
    degree_file_url = serializers.SerializerMethodField()

    class Meta:
        model = Education
        fields = ['id', 'highest_degree', 'field_of_study', 'degree_file_url']

    def get_degree_file_url(self, obj):
        return obj.degree_file.url if obj.degree_file else None


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
    receipt_url = serializers.SerializerMethodField()
    class Meta:
        model = AnnualMembershipFee
        fields = ['id', 'receipt_url', 'status'] 

    def get_receipt_url(self, obj):
        return obj.receipt.url if obj.receipt else None


class ViewRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewRequests
        fields = ['id', 'issuer', 'requested_user']

