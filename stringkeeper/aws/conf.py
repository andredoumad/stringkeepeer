import datetime
import os

# try:
#     from .ignore2 import AWS_ACCESS_KEY_ID,  AWS_SECRET_ACCESS_KEY
# except:
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "AKIAYZ2XE524MPVCJFBQ")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "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")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "stringkeeper-django-static")


# AWS_GROUP_NAME = "CFE_eCommerce_Group"
# AWS_USERNAME = "cfe-ecommerce-user"

AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True

#if this is false -- images dont load
AWS_QUERYSTRING_AUTH = True

S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = { 
 'Expires': expires,
 'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
}

PROTECTED_DIR_NAME = 'protected'
PROTECTED_MEDIA_URL = '//%s.s3.amazonaws.com/%s/' %( AWS_STORAGE_BUCKET_NAME, PROTECTED_DIR_NAME)

AWS_DOWNLOAD_EXPIRE = 5000 #(0ptional, in milliseconds)



