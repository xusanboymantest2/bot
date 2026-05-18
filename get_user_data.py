import asyncio
import json
import re

# We will use standard aiohttp for the network client
import aiohttp

# The real endpoint you pulled from DevTools
API_ENDPOINT = (
    "https://api.aistudy.uz/api/StudyAILms/Certificate/GetGeneratedCertificate"
)

# Headers cloned exactly from your operational fetch request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Priority": "u=4",
    "Referer": "https://omp.aistudy.uz/",
}
urls= [
  "https://omp.aistudy.uz/certificate?id=1b07719b-b6d0-4860-8b5c-26d2d816f6ca",
  "https://omp.aistudy.uz/certificate?id=7346abb6-9261-482e-a826-273601b155a7",
  "https://omp.aistudy.uz/certificate?id=88298aa4-813a-4706-a0d5-40667b202f11",
  "https://omp.aistudy.uz/certificate?id=c46a4979-796d-4cfb-ace1-56094b6bb31a",
  "https://omp.aistudy.uz/certificate?id=f783942f-7ad5-45ef-9317-ad653d464395",
  "https://omp.aistudy.uz/certificate?id=ef80ae94-b64e-410b-86e7-426d21b6e6fc",
  "https://omp.aistudy.uz/certificate?id=cfa345c5-dec1-4123-a699-cf02adb13fa0",
  "https://omp.aistudy.uz/certificate?id=8912f7ec-e1ba-4ed6-9440-f802d50505da",
  "https://omp.aistudy.uz/certificate?id=f44b724f-a78f-449e-9726-6c5c541cb977",
  "https://omp.aistudy.uz/certificate?id=ceb3cdae-ba9d-4f88-b2be-29d050c3ce50",
  "https://omp.aistudy.uz/certificate?id=5503ad0e-5c45-4949-b1e4-72b31bab1ce4",
  "https://omp.aistudy.uz/certificate?id=0eea654f-8bf0-4ad3-8b64-e94d6e878ad0",
  "https://omp.aistudy.uz/certificate?id=3c7cbb2d-7772-4ea5-9a69-52b2474fee09",
  "https://omp.aistudy.uz/certificate?id=32a04322-c3c2-400e-aff1-c10561830d23",
  "https://omp.aistudy.uz/certificate?id=f140c11b-9bce-491e-9454-2e6c03c9735c",
  "https://omp.aistudy.uz/certificate?id=c6583b34-3bc1-4eca-a6c3-df19a6e19eac",
  "https://omp.aistudy.uz/certificate?id=e2d4e025-179e-4f59-adb4-3fa4122c1fc0",
  "https://omp.aistudy.uz/certificate?id=e266b656-cc70-480c-99ee-2af7d7611b25",
  "https://omp.aistudy.uz/certificate?id=1e400db9-5be3-4594-bf4d-dc1ce5a01a09",
  "https://omp.aistudy.uz/certificate?id=ef002e24-6eaa-45a2-8305-45ee7fe3eee9",
  "https://omp.aistudy.uz/certificate?id=ced94112-c4ea-4a96-9650-f90e28c737ff",
  "https://omp.aistudy.uz/certificate?id=88c698e2-3f25-4d50-a853-eac5765203be",
  "https://omp.aistudy.uz/certificate?id=9db13a43-c036-46be-81a2-a48cdddc06b9",
  "https://omp.aistudy.uz/certificate?id=8c6a7d98-cb07-4f64-96eb-8accaaa8b93c",
  "https://omp.aistudy.uz/certificate?id=e9f8a715-0dfe-4d49-b81c-296f31cbefa9",
  "https://omp.aistudy.uz/certificate?id=ca9ea61c-d426-4337-955e-cfbee6638372",
  "https://omp.aistudy.uz/certificate?id=08eb4aa9-6dbe-4c5b-9d9d-fd2c97cffce3",
  "https://omp.aistudy.uz/certificate?id=45dc1931-37bb-45b1-8e66-e2593653057e",
  "https://omp.aistudy.uz/certificate?id=a314660f-749c-4117-9fff-a1223d20dc08",
  "https://omp.aistudy.uz/certificate?id=fd1079c4-23c1-498e-b384-d2d0d2d3622a",
  "https://omp.aistudy.uz/certificate?id=5bf613ea-9943-4b5d-ab79-f2c8148ce72f",
  "https://omp.aistudy.uz/certificate?id=9a3d6732-339b-49b5-ad95-4621009574d9",
  "https://omp.aistudy.uz/certificate?id=9a2a5816-c9ca-4e38-ad82-b9d42f9e72e5",
  "https://omp.aistudy.uz/certificate?id=2c731a2a-e769-4d3f-87dc-aadb9b33da94",
  "https://omp.aistudy.uz/certificate?id=a40cec34-65f8-4a25-b6d0-5e23347d2b19",
  "https://omp.aistudy.uz/certificate?id=7009f6c8-8a70-4ec9-b191-e7d70a4c46e6",
  "https://omp.aistudy.uz/certificate?id=f670bfb6-8aa1-40cc-b42d-3ba3d455866d",
  "https://omp.aistudy.uz/certificate?id=cdc28410-b78d-4aef-a3ea-8e622a886665",
  "https://omp.aistudy.uz/certificate?id=2a31c217-7970-41ac-8a18-5eedf4edfd8c",
  "https://omp.aistudy.uz/certificate?id=0ae6d5b2-95b8-4494-90bc-caf991f3775a",
  "https://omp.aistudy.uz/certificate?id=a76895cc-b3be-486f-819d-4f01a14fdec8",
  "https://omp.aistudy.uz/certificate?id=801ec02f-e533-4e7c-a644-ea38d72e2ed3",
  "https://omp.aistudy.uz/certificate?id=206f296a-e0aa-46fc-b390-472618379b83",
  "https://omp.aistudy.uz/certificate?id=81542289-ea91-4fc9-bd5f-86bada8c2818",
  "https://omp.aistudy.uz/certificate?id=b711cd77-dbc3-46e4-89c7-83eb1d5923b6",
  "https://omp.aistudy.uz/certificate?id=1e5a397f-e07e-4426-9061-9bd27dda4006",
  "https://omp.aistudy.uz/certificate?id=87dc8fc4-2f75-4dc1-82c5-f58db220b90f",
  "https://omp.aistudy.uz/certificate?id=7245295c-90b0-44a3-a8e8-9d63e982bfb3",
  "https://omp.aistudy.uz/certificate?id=a12fce6c-e06b-44af-9a24-7f9b88ca8b18",
  "https://omp.aistudy.uz/certificate?id=847a53f5-a52b-450b-971a-88dac233d91b",
  "https://omp.aistudy.uz/certificate?id=4bb0743c-6cbf-4e47-94b9-3c7f8bfd1373",
  "https://omp.aistudy.uz/certificate?id=543ff9fd-fcd3-42a0-a64d-e6c2daae1a79",
  "https://omp.aistudy.uz/certificate?id=c31b8d12-650f-4e5e-8c60-4aef2108401c",
  "https://omp.aistudy.uz/certificate?id=064f24bf-9ccb-4fb7-9566-ac822bc3c8f1",
  "https://omp.aistudy.uz/certificate?id=c14e497f-3c1a-4ada-8ac1-1a267c8ae694",
  "https://omp.aistudy.uz/certificate?id=94fad3d7-9701-4a03-8882-e5cdf9b2da77",
  "https://omp.aistudy.uz/certificate?id=d357b02d-1a81-4878-a9a0-62718890edb2",
  "https://omp.aistudy.uz/certificate?id=b2290817-8259-4714-949b-a503315e0be2",
  "https://omp.aistudy.uz/certificate?id=1e3ad5b5-1056-4d01-9d9c-cca1c6e91630",
  "https://omp.aistudy.uz/certificate?id=82065017-f279-45ac-bb3c-f8596cec0543",
  "https://omp.aistudy.uz/certificate?id=e15ca9ef-5153-4184-a10c-e51eded1fbe5",
  "https://omp.aistudy.uz/certificate?id=2f848186-5398-49b0-98dd-a487102461e5",
  "https://omp.aistudy.uz/certificate?id=c8bf3f7f-a41d-4a01-8f30-5c831adfbe31",
  "https://omp.aistudy.uz/certificate?id=d52d58bd-ce3f-4a42-b690-796ea52699f9",
  "https://omp.aistudy.uz/certificate?id=da471c97-a7ca-48f5-ba46-61923401255b",
  "https://omp.aistudy.uz/certificate?id=43979b58-8b4f-44d3-8213-091a498aa85e",
  "https://omp.aistudy.uz/certificate?id=9df6fd26-a2da-44bc-8ccc-ca44699aee35",
  "https://omp.aistudy.uz/certificate?id=f0ebb428-f0ff-4e13-bfe4-759362f0acc6",
  "https://omp.aistudy.uz/certificate?id=d3ecac51-e3ca-4b64-818a-6d9dcd471bfb",
  "https://omp.aistudy.uz/certificate?id=6c82f8ea-fb87-4c8f-a47a-b432595a74f2",
  "https://omp.aistudy.uz/certificate?id=5c5dadae-c8d1-4c52-8d98-bffc202da08c",
  "https://omp.aistudy.uz/certificate?id=18ac101b-6e40-414f-cbdf-08de72e91a12",
  "https://omp.aistudy.uz/certificate?id=2a6b9ba2-0811-4593-8010-8d3c0aca40d0",
  "https://omp.aistudy.uz/certificate?id=3688237e-1f97-471c-8981-7e36a1970ddb",
  "https://omp.aistudy.uz/certificate?id=8a3fe722-04b1-42b9-9a66-047844228c90",
  "https://omp.aistudy.uz/certificate?id=ec7a282e-d6ce-4e3e-80ee-c9143ad23f75",
  "https://omp.aistudy.uz/certificate?id=fa933aff-c6df-47ab-ad3b-692c59eaa8e6",
  "https://omp.aistudy.uz/certificate?id=7fc84aba-d624-4562-ade9-3a14311bb48c",
  "https://omp.aistudy.uz/certificate?id=9a287a6a-e1ba-4a5c-b7d2-7b442179c284",
  "https://omp.aistudy.uz/certificate?id=83e8452c-1b92-41d0-b13d-db02947067bb",
  "https://omp.aistudy.uz/certificate?id=1ac2c3b0-bcd7-4a23-bd29-a1272ae974a6",
  "https://omp.aistudy.uz/certificate?id=77f8814b-4326-40bf-b892-9bd54759113a",
  "https://omp.aistudy.uz/certificate?id=62bba490-c87d-44bf-b5e7-37daf4053cc3",
  "https://omp.aistudy.uz/certificate?id=9dcf321d-0366-4607-986f-5ed9d203890b",
  "https://omp.aistudy.uz/certificate?id=fbe0eef6-f57a-49aa-9c56-86d8f376d08c",
  "https://omp.aistudy.uz/certificate?id=aae16179-0bcb-4f0a-841c-ace78d984ec1",
  "https://omp.aistudy.uz/certificate?id=1e7a5653-b36e-4ad4-802f-c86f45da2e5d",
  "https://omp.aistudy.uz/certificate?id=097bb9a0-e424-4c96-973d-06c6baf7d559",
  "https://omp.aistudy.uz/certificate?id=1c504fa4-8163-46ec-b34c-210270ee598e",
  "https://omp.aistudy.uz/certificate?id=495a874e-d1f7-470c-931a-b207725de237",
  "https://omp.aistudy.uz/certificate?id=9b444aad-ceed-4eb4-a922-1414ad9f145e",
  "https://omp.aistudy.uz/certificate?id=6d79c421-b2d0-4a5d-8d61-9d9897129908",
  "https://omp.aistudy.uz/certificate?id=055b89a3-dcb6-4b9d-8013-b190054597b8",
  "https://omp.aistudy.uz/certificate?id=6bf5a0dc-81da-4c9c-84c4-29bd92547499",
  "https://omp.aistudy.uz/certificate?id=d871d2c6-bbd0-4354-9808-3df12420c7bc",
  "https://omp.aistudy.uz/certificate?id=afe27254-2709-4239-b310-5c36c75db1e7",
  "https://omp.aistudy.uz/certificate?id=ede9f49f-549b-4df6-b797-a6a147631190",
  "https://omp.aistudy.uz/certificate?id=3e082869-0287-43a8-a67f-81eb1fe146a8",
  "https://omp.aistudy.uz/certificate?id=6166096d-ae9c-468e-86cd-ef64ad8731a6",
  "https://omp.aistudy.uz/certificate?id=05df1c6f-0053-4a6b-a7fb-d531d1754ddb",
  "https://omp.aistudy.uz/certificate?id=09e846a5-d49d-4f0c-85c4-f323d9f5a074",
  "https://omp.aistudy.uz/certificate?id=33c1fdb5-0ddd-4457-b2c8-bc2f5e2078db",
  "https://omp.aistudy.uz/certificate?id=1783b815-105e-49bd-bc25-ad4b2b99a35e",
  "https://omp.aistudy.uz/certificate?id=e28230f6-fac4-46b6-b0ba-1964e47e1a44",
  "https://omp.aistudy.uz/certificate?id=9c4fe8a9-f70e-428e-ac5e-52614f6b0295",
  "https://omp.aistudy.uz/certificate?id=7897c40f-aec2-44ab-9e6f-0eb05f07348d",
  "https://omp.aistudy.uz/certificate?id=f031b581-9c4c-4154-88f3-f8af11966fd7",
  "https://omp.aistudy.uz/certificate?id=9fe4b59f-f63b-4830-ade9-86eb7539e19f",
  "https://omp.aistudy.uz/certificate?id=dd3668a7-8ea8-43a4-84d9-38811425329a",
  "https://omp.aistudy.uz/certificate?id=471aff21-5be8-45fd-b680-cfae9098e3c2",
  "https://omp.aistudy.uz/certificate?id=820f71a7-b0a6-4db6-b010-9fae8e8cb466",
  "https://omp.aistudy.uz/certificate?id=8e425c4b-710b-45c2-8ecf-114ec886a668",
  "https://omp.aistudy.uz/certificate?id=7bd6b5da-ae5c-4fbe-9a3d-b22ff5c230fb",
  "https://omp.aistudy.uz/certificate?id=aa5ea65e-22f6-4e0c-988b-b922ccf56f54",
  "https://omp.aistudy.uz/certificate?id=1c9d9faf-f62a-4653-a5d1-dd128f3e9d0e",
  "https://omp.aistudy.uz/certificate?id=e38b21b4-70f1-423a-9566-c47c0cb5160f",
  "https://omp.aistudy.uz/certificate?id=3364c8bb-8dd8-47b3-8e73-6bd0d8f260d9",
  "https://omp.aistudy.uz/certificate?id=0f93af0f-01c1-4e33-abf8-e4519f80cb56",
  "https://omp.aistudy.uz/certificate?id=21c95398-d674-4810-bf88-7a8d36935c2f",
  "https://omp.aistudy.uz/certificate?id=76e4dee9-1054-488f-bf5f-40fb721d4069",
  "https://omp.aistudy.uz/certificate?id=1376041a-56cb-4465-b547-3d8ab41c667b",
  "https://omp.aistudy.uz/certificate?id=1994c8e0-0c04-44ec-a5fc-7f4e12c2284f",
  "https://omp.aistudy.uz/certificate?id=022d1898-d8c8-4657-88c2-91d9be08e394",
  "https://omp.aistudy.uz/certificate?id=56eb7cf6-78bf-4fbb-a1af-ff3582c72fd9",
  "https://omp.aistudy.uz/certificate?id=33d7fdb4-7783-438c-862f-e65dde6a8fa7",
  "https://omp.aistudy.uz/certificate?id=10d55952-297d-4065-bdf6-0f9988aba10f",
  "https://omp.aistudy.uz/certificate?id=f69270da-94e6-4b53-993f-f68ff9825b7e",
  "https://omp.aistudy.uz/certificate?id=f6e46161-692b-4370-8327-b236b477c52f",
  "https://omp.aistudy.uz/certificate?id=d76faea3-e094-45fc-8d0b-b7b94c3cfcf3",
  "https://omp.aistudy.uz/certificate?id=365db223-b4b0-4191-9109-b2d5d8e818dc",
  "https://omp.aistudy.uz/certificate?id=58574631-4707-4836-af3c-d59fb3ada60e",
  "https://omp.aistudy.uz/certificate?id=71dcb26c-f955-4bb8-8229-31d7ff742151",
  "https://omp.aistudy.uz/certificate?id=bbb807c8-7263-4b5b-b466-d104297e96ae",
  "https://omp.aistudy.uz/certificate?id=8fc5feb2-3144-4e3a-88c4-23f7582e9e0c",
  "https://omp.aistudy.uz/certificate?id=ea2b37cf-5144-4e0c-98ff-9e6612d7a3a2",
  "https://omp.aistudy.uz/certificate?id=a39e5216-67f5-4d95-b4b1-4a5c8e3bbcfd",
  "https://omp.aistudy.uz/certificate?id=1669897c-9eab-44f8-a895-612dc553e06f",
  "https://omp.aistudy.uz/certificate?id=6e5c9b5d-eaad-4d2e-8fe9-e9f89154a2c6",
  "https://omp.aistudy.uz/certificate?id=91909a83-b6c6-4903-9920-5ed8e04df9c5",
  "https://omp.aistudy.uz/certificate?id=b86b4693-821c-48c4-914c-7711891af316",
  "https://omp.aistudy.uz/certificate?id=f98ee7e4-f730-4c7e-8c7c-d0ce4983c26e",
  "https://omp.aistudy.uz/certificate?id=65928c71-0fd6-44bd-be58-f7332cd756a2",
  "https://omp.aistudy.uz/certificate?id=088de176-4cd7-4999-a880-65fde3474779",
  "https://omp.aistudy.uz/certificate?id=38cd1807-6be1-4210-ba87-6683f3c3578d",
  "https://omp.aistudy.uz/certificate?id=615f5cd7-d88c-4b3e-829d-9848a808c712",
  "https://omp.aistudy.uz/certificate?id=1f027c9c-474f-4e65-8dc7-ee35581eb982",
  "https://omp.aistudy.uz/certificate?id=cca89979-9bcd-43fb-b47e-45a3b56b1006",
  "https://omp.aistudy.uz/certificate?id=c4c381df-a96d-49a7-8a54-db99849d0962",
  "https://omp.aistudy.uz/certificate?id=2d64d4d6-e245-4990-9351-030f2fc74432",
  "https://omp.aistudy.uz/certificate?id=2b909821-1a21-4e40-a681-31d44ce469bc",
  "https://omp.aistudy.uz/certificate?id=962a8e13-b0d7-459c-a5aa-d3fc9ad5e98d",
  "https://omp.aistudy.uz/certificate?id=cd3345f5-17fb-4a40-b075-af7487cfa68f",
  "https://omp.aistudy.uz/certificate?id=b1e8d4d3-1113-42ee-a85e-bce1b03e31d1",
  "https://omp.aistudy.uz/certificate?id=a4d0067b-95dc-42f7-954f-c6f9f212d1d6",
  "https://omp.aistudy.uz/certificate?id=6a7e9379-e0bc-4444-9b72-70c8065766bb",
  "https://omp.aistudy.uz/certificate?id=c8ed9149-028f-4ece-8fcb-06af2ef6b7f5",
  "https://omp.aistudy.uz/certificate?id=ea7c1383-2700-4a1f-97d3-9e7897f4a8ec",
  "https://omp.aistudy.uz/certificate?id=6647c123-ce4f-4378-a90e-fd6c4d2d8b9a",
  "https://omp.aistudy.uz/certificate?id=494a8cf2-46c0-4bde-aabc-03739b84e437",
  "https://omp.aistudy.uz/certificate?id=c4bb2ebd-6efe-4f3a-88a3-afaad3795ee9",
  "https://omp.aistudy.uz/certificate?id=6de68d49-3c24-489c-89c3-c939a427404a",
  "https://omp.aistudy.uz/certificate?id=76618f4e-9e25-4785-9bfb-429c0af4ec41",
  "https://omp.aistudy.uz/certificate?id=3e648e54-05ea-4b86-adda-3098baab8455",
  "https://omp.aistudy.uz/certificate?id=6c691611-5320-41b9-b3bb-519d7482661c",
  "https://omp.aistudy.uz/certificate?id=75df6eb0-009c-4a65-903c-925d716b8e51",
  "https://omp.aistudy.uz/certificate?id=43c5ba4d-4c54-41a1-b1b8-43dc2b95c392",
  "https://omp.aistudy.uz/certificate?id=c03fddc9-22e7-4e57-9c25-81f967e1ee8f",
  "https://omp.aistudy.uz/certificate?id=412779e0-7cff-43b5-a5c0-f03ed971f57f",
  "https://omp.aistudy.uz/certificate?id=17ecca8b-0542-49e5-8dab-2ae58b93e75e",
  "https://omp.aistudy.uz/certificate?id=f5b8dd3e-d327-4b50-9138-dffab408d860",
  "https://omp.aistudy.uz/certificate?id=38c40f2f-17c3-4217-bc08-024f1f0f13d4",
  "https://omp.aistudy.uz/certificate?id=6c959b47-99b8-4639-a9b3-b5f92af443a9",
  "https://omp.aistudy.uz/certificate?id=f2046e1f-8da2-4d7f-896b-cac732cd5e7d",
  "https://omp.aistudy.uz/certificate?id=ed13c0da-3c17-4bc0-8a12-edf51c4f232a",
  "https://omp.aistudy.uz/certificate?id=ede7c99e-c919-408d-8449-54eeaf07b71a",
  "https://omp.aistudy.uz/certificate?id=de85c837-0715-455e-ab6e-d12a6064cc11",
  "https://omp.aistudy.uz/certificate?id=4e74c8c0-a24d-47f8-bc23-1c91cdc76666"
]
OUTPUT_FILE = "certificates_updated.json"


def format_fullname(user_data):
    """Combines FirstName, LastName, and SurName to reconstruct the full string."""
    first = user_data.get("FirstName", "").strip()
    last = user_data.get("LastName", "").strip()
    patronymic = user_data.get("SurName", "").strip()

    # Title-case normalization (e.g., ABDULBORIY -> Abdulboriy)
    # Fixes the backtick character standard 'o`g`li' -> 'o‘g‘li' if preferred
    full_str = f"{first} {last} {patronymic}".strip()
    return full_str.title().replace("O`G`Li", "o‘g‘li").replace("Qizi", "qizi")


def format_date(date_str):
    """Formats raw date strings from dd.mm.yyyy to dd-mm-yyyy."""
    if not date_str:
        return "Topilmadi"
    return date_str.replace(".", "-").strip()


async def fetch_certificate_from_api(session, entry_key, certificate_url):
    """Queries the internal background API directly using the certificate UUID identifier."""
    try:
        # Extract the certificate UUID from the query string
        match = re.search(r"id=([a-f0-9\-]{36})", certificate_url)
        if not match:
            return entry_key, certificate_url, "Invalid ID", "Topilmadi"

        cert_id = match.group(1)
        params = {"certificateId": cert_id}

        async with session.get(
            API_ENDPOINT, headers=HEADERS, params=params, timeout=10
        ) as response:
            if response.status != 200:
                return entry_key, certificate_url, "Topilmadi", "Topilmadi"

            payload = await response.json()

            # Ensure statusCode is valid and payload contains results
            if (
                payload.get("statusCode") == 200
                and payload.get("result") is not None
            ):
                result_node = payload["result"]

                # Unpack the secondary nested JSON string inside 'userDataJson'
                raw_user_str = result_node.get("userDataJson")
                if raw_user_str:
                    user_data = json.loads(raw_user_str)

                    fullname = format_fullname(user_data)
                    given_date = format_date(user_data.get("GivenTime", ""))

                    return entry_key, certificate_url, fullname, given_date

            return entry_key, certificate_url, "Topilmadi", "Topilmadi"

    except Exception as e:
        # Silently capture drops to keep async gather moving forward
        return entry_key, certificate_url, "Topilmadi", "Topilmadi"


async def main():
    final_data = {}

    # Standard task execution cap to stay friendly with api.aistudy.uz
    sem = asyncio.Semaphore(15)

    async def throttled_worker(session, entry_key, url):
        async with sem:
            return await fetch_certificate_from_api(session, entry_key, url)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for index, url in enumerate(urls, start=1):
            entry_key = f"id:{index}"
            tasks.append(throttled_worker(session, entry_key, url))

        print(f"Direct API fetch sequence active for {len(urls)} certificates...")
        results = await asyncio.gather(*tasks)

        for entry_key, url, fullname, date in results:
            final_data[entry_key] = {
                "certificate_url": url,
                "fullname": fullname,
                "date": date,
            }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    print(f"Finished! File saved explicitly to -> '{OUTPUT_FILE}'")


if __name__ == "__main__":
    asyncio.run(main())