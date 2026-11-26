# product_name = "500 Words Sound Book for Kids"

# audience = "Parents with children aged 2–6"

# benefits = "Vocabulary development, word recognition, early learning"

# price = "$29.99"

# prompt = f"""
# You are an expert ecommerce copywriter.

# Write a product description for {product_name}.

# Target audience: {audience}

# Main benefits: {benefits}

# Price: {price}

# Use simple English and a persuasive,
# trustworthy writing style.
# """

# print(prompt)

products = [
    {
        "name": "Talking Flash Card Tablet",
        "audience": "Parents with children aged 2–6",
        "benefits": "Vocabulary development, early learning, reduced screen time",
        "price": "$49.99"
    },
    {
        "name": "500 Words Sound Book",
        "audience": "Parents with children aged 2–6",
        "benefits": "Vocabulary development, word recognition, early learning",
        "price": "$29.99"
    },
    {
    
                "name": "Alphabet Learning Board",
                "audience": "Parents with children aged 3–6",
                "benefits": "Alphabet recognition, letter identification, early learning",
                "price": "$24.99"
    }
]

system_prompt = """
You are a professional ecommerce copywriter for Toddler Think.

Always use friendly, simple, trustworthy language.

Never invent product features or make unsupported claims.

Focus on the real benefits of each product.

Write for parents and caregivers.

"""
print(system_prompt)

for product in products:

    prompt = f"""
    You are an expert ecommerce copywriter.

    Write a product description for {product["name"]}.

    Target audience: {product["audience"]}

    Main benefits: {product["benefits"]}

    Price: {product["price"]}

    Use simple English and a persuasive,
    trustworthy writing style.
    Use the supplied product price exactly. Do not change or invent prices.
Return the response using this JSON structure:
    {{
        "title": "",

        "introduction": "",

        "benefits" : ["", "", ""],

        "price": "",

        "call_to_action": ""
    }}
    Return valid JSON only.

    Use double quotes for JSON keys and string values.
    Generate exactly three distinct benefits, not merely fill three empty spaces.
    Include no Markdown code fences or explanations outside the JSON.
    """
    
    print(prompt)