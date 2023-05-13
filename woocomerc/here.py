from woocommerce import API

wcapi = API(
    url="https://medical-exam.ir",
    consumer_key="ck_d90ea6be7f2881cbd8f23d51b6be390a6300b9ea",
    consumer_secret="cs_537364de74126923605ea3e1169b9e74b8d2527e",
    wp_api=True,
    version="wc/v3",
    query_string_auth=True  # Force Basic Authentication as query string true and using under HTTPS
)
data: dict = wcapi.get('orders').json()


for i in data:
    print(i["id"])
    print(i['billing']['email'])