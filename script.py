from inference_sdk import InferenceHTTPClient

classifications = {
    "11 0 0 0 1 1 1 1 0 0 0": "apple",
    "1": "meat",
    "2": "cabbage",
    "3": "carrots",
    "4": "chicken wings",
    "5": "chili",
    "6": "coriander",
    "7": "cucumber",
    "8": "egg",
    "9": "fish",
    "10": "garlic",
    "11": "ginger",
    "12": "honey",
    "13": "lemon",
    "14": "green lemon",
    "15": "cocunut milk",
    "16": "mushroom",
    "17": "noodles",
    "18": "onion",
    "19": "orange",
    "20": "parsley",
    "21": "peanut",
    "22": "pork meat",
    "23": "potato",
    "24": "shrimp",
    "25": "rice",
    "26": "onion chives",
    "27": "chicken cubes",
    "28": "tomato",
    "29": "yogurt",
}

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com", api_key="PwEdE9z950lxfTEgfX3w"
)

result = client.run_workflow(
    workspace_name="devml",
    workflow_id="small-object-detection-sahi-2",
    images={"image": "siken.png"},
    use_cache=True,  # cache workflow definition for 15 minutes
)

predictions = result[0].get("predictions")

ingredients = [
    classifications.get(v["class"]) for v in predictions.get("predictions")
]

print(ingredients, " available")
