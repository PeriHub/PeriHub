from shepard_client.api_client import ApiClient
from shepard_client.configuration import Configuration

from shepard_client.api.data_object_api import DataObjectApi
from shepard_client.models.data_object import DataObject


HOST = "https://shepard-api.fa-services.intra.dlr.de/shepard/api"
APIKEY = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIyYTNmODM4YS1iNjU5LTRkMTgtYmYxMy0wNTkwOTgyMWZmMzQiLCJpc3MiOiJodHRwczovL3NoZXBhcmQtYXBpLmZhLXNlcnZpY2VzLmludHJhLmRsci5kZS9zaGVwYXJkL2FwaS8iLCJuYmYiOjE2ODY2NTg1MjUsImlhdCI6MTY4NjY1ODUyNSwianRpIjoiMDlhOTUxMmQtMjZiNS00Nzg3LWIzZGItNTU3ZjJlYzljMWY2In0.jtabm2bN164QqPDskNZ2saCHB0sLm1Nwo-9gmHxoDmeB_BMJY2uMleB2wSCEdJBJcBAPMhUWV0pzK4dVBp--MUW4UbVhf6iMzo4jAEtGtHFSpjcZftPSHInR17XJecE8VF5EhI2c51_KYjlHaqoMYRt0N0P5o8YaD-T3oD6VIXqmnaY3gfnelrD6bdKi9iH1O3PGjxvc-ZFg9EATUMZs--WAJMVZfdCeAhBYEIprSbN1XL3TR0J8x0hiGyfRgWZx4I0tUn0NjMziZnCFmjP5PlCckr3of3gJRfRJ4DLMgdWEPX3Ra_fMvS08kenSVC9nXb1EpceGAwsVd4KiRShH8w"

# Set up configuration
conf = Configuration(host=HOST, api_key={"apikey": APIKEY})
conf.access_token = None
client = ApiClient(configuration=conf)

###################### Data object ######################
# Create a data object
dataobject_api = DataObjectApi(client)
dataobject_to_create = DataObject(
    name="Test",
    description="description",
    parent_id=22115,
)
created_dataobject = dataobject_api.create_data_object(
    collection_id=13513,
    data_object=dataobject_to_create,
)
print(created_dataobject)
