from django.contrib import admin

# Register your models here.
from .models import (
    Address,
    Contact,
    Education,
    ProfessionalExperience,
    Publications,
    Projects,
    Patents,
    Award,
    AnnualMembershipFee,
    User,
    ViewRequests,
)

admin.site.register(Address)
admin.site.register(Contact)
admin.site.register(Education)
admin.site.register(ProfessionalExperience)
admin.site.register(Publications)
admin.site.register(Projects)
admin.site.register(Patents)
admin.site.register(Award)
admin.site.register(AnnualMembershipFee)
admin.site.register(User)
admin.site.register(ViewRequests)
