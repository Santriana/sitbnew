from import_export import resources
from .models import User, Province, District
from import_export.fields import Field
from import_export.widgets import DateWidget
from import_export.widgets import ForeignKeyWidget

class UserResource(resources.ModelResource):
        name = Field(attribute='name', column_name='Name')
        email = Field(attribute='email', column_name='Email')
        password = Field(attribute='password', column_name='Password')
        code_fasyankes = Field(attribute='code_fasyankes', column_name='Kode Fasyankes')
        sitb_rs_id = Field(attribute='sitb_rs_id', column_name='RS ID')
        sitb_rs_pass = Field(attribute='sitb_rs_pass', column_name='RS PASSWORD')
        province = Field(attribute='province', column_name='Province', widget=ForeignKeyWidget(Province, field='id'))
        district = Field(attribute='district', column_name='District', widget=ForeignKeyWidget(District, field='id'))
        organization_id = Field(attribute='organization_id', column_name='Organization ID')
        client_id = Field(attribute='client_id', column_name='CLIENT ID')
        client_secret = Field(attribute='client_secret', column_name='ClIENT SECRET')
        is_active = Field(attribute='is_active', column_name='IS ACTIVE')
        is_staff = Field(attribute='is_staff', column_name='IS STAFF')
        date_joined = Field(attribute='date_joined', column_name='DATE JOINED', widget=DateWidget('%Y-%m-%d'))
        
        class Meta:
            model = User
            skip_unchanged = True
            report_skipped = True
            import_id_fields = ('email',)
            fields = (
                'id',
                'name',
                'email',
                'password',
                'code_fasyankes',
                'sitb_rs_id',
                'sitb_rs_pass',
                'province',
                'district',
                'organization_id',
                'client_id',
                'client_secret',
                'is_active',
                'is_staff',
                'date_joined',
            )