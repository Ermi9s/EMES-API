from django.db import models
from django.contrib.auth.models import AbstractUser

# Address Model
class Address(models.Model):
    residential = models.CharField(max_length=255)
    employer = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.residential}, {self.city}, {self.country}"


# Contact Model
class Contact(models.Model):
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.email


# Education Model
class Education(models.Model):
    highest_degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    university = models.CharField(max_length=255)
    graduation_year = models.CharField(max_length=4)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    degree_file = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.highest_degree} in {self.field_of_study}"


# Professional Experience Model
class ProfessionalExperience(models.Model):
    organization = models.CharField(max_length=255)
    position = models.CharField(max_length=100)
    key_responsibilities = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.position} at {self.organization}"


# Publications Model
class Publications(models.Model):
    title = models.CharField(max_length=255)
    journal = models.CharField(max_length=255)
    date = models.DateTimeField()

    def __str__(self):
        return self.title


# Projects Model
class Projects(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title


# Patents Model
class Patents(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()

    def __str__(self):
        return self.title


# Award Model
class Award(models.Model):
    title = models.CharField(max_length=255)
    awarding_body = models.CharField(max_length=255)
    year = models.CharField(max_length=4)

    def __str__(self):
        return self.title


# Annual Membership Fee Model
class AnnualMembershipFee(models.Model):
    receipt = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.receipt


# User Model
class User(AbstractUser):
    sex = models.CharField(max_length=20,blank=True, null=True)
    date_of_birth = models.DateTimeField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    education = models.ForeignKey(Education, on_delete=models.SET_NULL, null=True, blank=True)
    professional_experience = models.ForeignKey(ProfessionalExperience, on_delete=models.SET_NULL, null=True, blank=True)
    projects = models.ForeignKey(Projects, on_delete=models.SET_NULL, null=True, blank=True)
    awards = models.ForeignKey(Award, on_delete=models.SET_NULL, null=True, blank=True)
    publications = models.ForeignKey(Publications, on_delete=models.SET_NULL, null=True, blank=True)
    patents = models.ForeignKey(Patents, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(AnnualMembershipFee, on_delete=models.SET_NULL, null=True, blank=True)

    #is user is inistitution
    services_or_productions = models.JSONField(default=tuple, null=True , blank=True)
    is_organization = models.BooleanField(default=False)
    
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username



# View Requests Model
class ViewRequests(models.Model):
    issuer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_requests')
    requested_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    

    def __str__(self):
        return f"{self.issuer} -> {self.requested_user}"

