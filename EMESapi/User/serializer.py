from rest_framework import serializers
from .models import (
    User, Address, Contact, Education, ProfessionalExperience,
    Publications, Projects, Patents, Award, AnnualMembershipFee, ViewRequests
)

class UserSerializer(serializers.ModelSerializer):
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), required=False)
    contact = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all(), required=False)
    education = serializers.PrimaryKeyRelatedField(queryset=Education.objects.all(), required=False)
    professional_experience = serializers.PrimaryKeyRelatedField(queryset=ProfessionalExperience.objects.all(), required=False)
    projects = serializers.PrimaryKeyRelatedField(queryset=Projects.objects.all(), required=False)
    awards = serializers.PrimaryKeyRelatedField(queryset=Award.objects.all(), required=False)
    publications = serializers.PrimaryKeyRelatedField(queryset=Publications.objects.all(), required=False)
    patents = serializers.PrimaryKeyRelatedField(queryset=Patents.objects.all(), required=False)
    payment = serializers.PrimaryKeyRelatedField(queryset=AnnualMembershipFee.objects.all(), required=False)

    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'sex', 'date_of_birth', 'nationality',
            'profile_picture', 'address', 'contact', 'education', 'professional_experience',
            'projects', 'awards', 'publications', 'patents', 'payment', 'verified','is_organization' 
        ]
        read_only_fields = ['id', 'username']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
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
        fields = ['id', 'title', 'journal', 'date']


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


class AnnualMembershipFeeSerializer(serializers.ModelSerializer):
    receipt_url = serializers.SerializerMethodField()
    class Meta:
        model = AnnualMembershipFee
        fields = ['id', 'receipt_url', 'status'] 

    def get_receipt_url(self, obj):
        return obj.receipt

class ViewRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewRequests
        fields = ['id', 'issuer', 'requested_user']

