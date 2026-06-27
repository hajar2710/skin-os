from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allows your HTML frontend to send requests to this API

@app.route('/')
def frontpage():
    return render_template('frontpage2.html') # Loads your landing page

@app.route('/question1')
def q1():
    return render_template('question1.html')

@app.route('/question2')
def q2():
    return render_template('question2.html')

@app.route('/question3_shiny')
def q3_shiny():
    return render_template('question3_shiny.html')

@app.route('/question3_irritated')
def q3_irritated():
    return render_template('question3_irritated.html')

@app.route('/question4')
def q4():
    return render_template('question4.html')

@app.route('/output')
def output_page():
    # 1. Pull quiz results from the URL parameters
    age = request.args.get('age')
    raw_feel = request.args.get('feel')
    shiny_area = request.args.get('shiny_area')
    redness = request.args.get('redness')
    concern = request.args.get('concern')

    # Fallback to prevent crashes if someone visits /output directly without a quiz
    if not age or not raw_feel or not concern:
        return "Quiz data missing. Please complete the quiz first.", 400

    # 2. Format the "Feel" variable exactly like your rule engine expects
    feel_condition = ""
    if raw_feel == "tight/dry":
        feel_condition = "tight/dry"
    elif raw_feel == "comfortable":
        feel_condition = "comfortable"
    elif raw_feel == "shiny":
        feel_condition = "shiny_all" if shiny_area == "all area" else "shiny_tzone"
    elif raw_feel == "irritated":
        feel_condition = "red_very_often" if redness == "very often" else ("red_sometimes" if redness == "sometimes" else "red_rarely")

    # 3. Match the configuration against your RULES database
    matched_rule = None
    for rule in RULES:
        if rule['age'] == age and rule['feel'] == feel_condition and rule['concern'] == concern:
            matched_rule = rule
            break

    if not matched_rule:
        return f"No skin profile matches these parameters (Age: {age}, Feel: {feel_condition}, Concern: {concern}).", 400

    # 4. Extract data items from database mapping configurations
    skin_type_data = SKIN_TYPES[matched_rule['type']]
    routine_data = ROUTINES[matched_rule['routine_id']]
    
    # Format the ingredients list to match Jinja's expected loop format
    recommended_ingredients = []
    for ing_id in matched_rule['ingredients']:
        recommended_ingredients.append({
            "name": INGREDIENTS[ing_id]["name"],
            "benefit": INGREDIENTS[ing_id]["desc"]
        })

    # Pull accurate product names out of the routine dataset
    c_name = routine_data['cleanser']
    s_name = routine_data['toner_serum']
    m_name = routine_data['moisturizer']
    sun_name = routine_data['sunscreen']

    # 5. Build the context dictionary matching your HTML layout perfectly (.brand, .name, .image)
    template_products = {
        "cleanser": {
            "brand": PRODUCTS.get(c_name, {}).get("brand", "Generic"), 
            "name": c_name, 
            "image": PRODUCTS.get(c_name, {}).get("image_url", "")
        },
        "serum": {
            "brand": PRODUCTS.get(s_name, {}).get("brand", "Generic"), 
            "name": s_name, 
            "image": PRODUCTS.get(s_name, {}).get("image_url", "")
        },
        "moisturizer": {
            "brand": PRODUCTS.get(m_name, {}).get("brand", "Generic"), 
            "name": m_name, 
            "image": PRODUCTS.get(m_name, {}).get("image_url", "")
        },
        "sunscreen": {
            "brand": PRODUCTS.get(sun_name, {}).get("brand", "Generic"), 
            "name": sun_name, 
            "image": PRODUCTS.get(sun_name, {}).get("image_url", "")
        }
    }

    # 6. Safely render out the template with all variables applied!
    return render_template(
        'output.html',
        user_skin_type=skin_type_data['name'],
        skin_type_explanation=skin_type_data['description'],
        user_skin_image_url=skin_type_data['image_url'],
        recommended_ingredients=recommended_ingredients,
        products=template_products,
        routine_explanation=routine_data['desc']
    )
# ==========================================
# 1. THE DATABASE (WITH IMAGE URLS ADDED)
# ==========================================

SKIN_TYPES = {
    "Dry": {
        "name": "Dry",
        "description": "Your skin often feels tight, parched, or even a bit flaky, especially after washing your face. It struggles to hold onto moisture, which can make it look a little dull or rough. To bring back its natural glow, this skin type loves rich, hydrating creams that lock in moisture.",
        "image_url": "/static/images/skin_dry.png" # Add your image paths here!
    },
    "Oily": {
        "name": "Oily",
        "description": "Your skin produces extra natural oils, which often leaves your face looking shiny or feeling slick by lunchtime. You might notice larger, more visible pores, and you are likely more prone to breakouts or blackheads. It thrives on lightweight, gel-based products that balance oil without clogging your skin.",
        "image_url": "/static/images/skin_oily.png"
    },
    "Combination": {
        "name": "Combination",
        "description": "Your skin is a mix of two types: you usually get oily and shiny in your \"T-Zone\" (your forehead, nose, and chin), but your cheeks stay normal or dry. It can feel like a bit of a balancing act because different areas of your face have different needs. Using lightweight hydration across your whole face works best for this type.",
        "image_url": "/static/images/skin_combination.png"
    },
    "Normal": {
        "name": "Normal",
        "description": "Your skin is naturally well-balanced, meaning it is neither too oily nor too dry. You rarely experience severe breakouts, flaking, or a tight feeling, and your pores are generally small and unnoticeable. Because your skin is already quite happy, your main goal is just to keep it clean and protected.",
        "image_url": "/static/images/skin_normal.png"
    },
    "Sensitive": {
        "name": "Sensitive",
        "description": "Your skin reacts easily to new products, weather changes, or certain ingredients, often turning red, itchy, or stinging. It has a weaker natural shield, making it easily overwhelmed or irritated. This skin type does best with super gentle, fragrance-free products that focus on calming and soothing.",
        "image_url": "/static/images/skin_sensitive.png"
    }
}

INGREDIENTS = {
    1: {"name": "Salicylic Acid (BHA)", "desc": "Dissolves deep pore clogs and treats acne."},
    2: {"name": "Glycolic Acid (AHA)", "desc": "Smooths surface texture, tiny bumps, and KP."},
    3: {"name": "Lactic Acid (AHA)", "desc": "Gently exfoliates while keeping skin hydrated."},
    4: {"name": "Vitamin C", "desc": "Fades dark spots and corrects dullness."},
    5: {"name": "Niacinamide", "desc": "Controls excess oil and blocks dark pigment transfer."},
    6: {"name": "Retinol", "desc": "Boosts collagen production and speeds up cell turnover."},
    7: {"name": "Peptides", "desc": "Plumps sagging texture by acting as skin building blocks."},
    8: {"name": "Hyaluronic Acid", "desc": "Delivers deep, plumping moisture to dehydrated skin."},
    9: {"name": "Ceramides", "desc": "Replenishes lost natural oils and protects fragile mature skin."},
    10: {"name": "Benzoyl Peroxide", "desc": "Targets and kills acne-causing bacteria directly."}
}

# Mapping products to their routine steps, with images
PRODUCTS = {
    # Skintific Products
    "Skintific 5X Ceramide Low pH Cleanser": {"type": "Cleanser", "brand": "Skintific", "image_url": "/static/images/skintific_low_ph_cleanser.png"},
    "Skintific 3X Acid Acne Gel Cleanser": {"type": "Cleanser", "brand": "Skintific", "image_url": "/static/images/skintific_3x_acid_cleanser.png"},
    "Skintific White Truffle Cleansing Essence": {"type": "Cleanser", "brand": "Skintific", "image_url": "/static/images/skintific_white_truffle_cleanser.png"},
    "Skintific 5X Ceramide Barrier Repair Moisture Gel": {"type": "Moisturizer", "brand": "Skintific", "image_url": "/static/images/skintific_5x_ceramide_moisturizer.png"},
    "Skintific 4D Hyaluronic Acid Barrier Essence Toner": {"type": "Toner/Serum", "brand": "Skintific", "image_url": "/static/images/skintific_ha_essence_toner.png"}, 
    "Skintific Gentle Retinol Renewal Serum": {"type": "Toner/Serum", "brand": "Skintific", "image_url": "/static/images/skintific_retinol_serum.png"},
    "Skintific 5% AHA BHA PHA Exfoliating Toner": {"type": "Toner/Serum", "brand": "Skintific", "image_url": "/static/images/skintific_exfoliating_toner.png"},
    "Skintific 10% Niacinamide Brightening Serum": {"type": "Toner/Serum", "brand": "Skintific", "image_url": "/static/images/skintific_niacinamide_serum.png"},
    "Skintific Glycolic Acid Daily Clarifying Toner": {"type": "Toner/Serum", "brand": "Skintific", "image_url": "/static/images/skintific_glycolic_toner.png"},
    "Skintific 5X Ceramide Serum Sunscreen": {"type": "Sunscreen", "brand": "Skintific", "image_url": "/static/images/skintific_5x_sunscreen.png"},
    "Skintific Ultra Light Serum Sunscreen": {"type": "Sunscreen", "brand": "Skintific", "image_url": "/static/images/skintific_ultra_light_sunscreen.png"},
    
    # Wardah Products
    "Wardah C-Defense Brightening Fluffy Cleanser": {"type": "Cleanser", "brand": "Wardah", "image_url": "/static/images/wardah_cdefense_cleanser.png"},
    "Wardah SymRadiance 399 + 5% Niacinamide Moisture Gel": {"type": "Moisturizer", "brand": "Wardah", "image_url": "/static/images/wardah_symradiance_moisturizer.png"},
    "Wardah C-Defense Vitamin C Serum": {"type": "Toner/Serum", "brand": "Wardah", "image_url": "/static/images/wardah_cdefense_serum.png"},
    "Wardah Renew You Anti-Aging Intensive Serum": {"type": "Toner/Serum", "brand": "Wardah", "image_url": "/static/images/wardah_renew_you_serum.png"},
    "Wardah UV Shield Essential Sunscreen Gel": {"type": "Sunscreen", "brand": "Wardah", "image_url": "/static/images/wardah_uv_essential_sunscreen.png"},
    "Wardah UV Shield Light Matte Sun Stick": {"type": "Sunscreen", "brand": "Wardah", "image_url": "/static/images/wardah_uv_matte_sunstick.png"},
    
    # Glad2Glow Products
    "Glad2Glow Blueberry Ceramide Gentle Cleanser": {"type": "Cleanser", "brand": "Glad2Glow", "image_url": "/static/images/glad2glow_blueberry_cleanser.png"},
    "Glad2Glow Blueberry 5X Ceramide Moisture Gel": {"type": "Moisturizer", "brand": "Glad2Glow", "image_url": "/static/images/glad2glow_blueberry_moisturizer.png"},
    "Glad2Glow Yuja Symwhite 377 Dark Spot Moisturizer": {"type": "Moisturizer", "brand": "Glad2Glow", "image_url": "/static/images/glad2glow_yuja_moisturizer.png"},
    "Glad2Glow Centella Soothing Gel Moisturizer": {"type": "Moisturizer", "brand": "Glad2Glow", "image_url": "/static/images/glad2glow_centella_moisturizer.png"},
    "Glad2Glow Centella 2% Salicylic Acid Acne Serum": {"type": "Toner/Serum", "brand": "Glad2Glow", "image_url": "/static/images/glad2glow_salicylic_serum.png"},
    "Glad2Glow Ultra Light Sunscreen SPF 50": {"type": "Sunscreen", "brand": "Glad2Glow", "image_url": "/static/images/glad2glow_sunscreen.png"}
}

ROUTINES = {
    1: {
        "cleanser": "Skintific 5X Ceramide Low pH Cleanser",
        "moisturizer": "Skintific 5X Ceramide Barrier Repair Moisture Gel",
        "toner_serum": "Skintific 4D Hyaluronic Acid Barrier Essence Toner",
        "sunscreen": "Skintific 5X Ceramide Serum Sunscreen",
        "desc": "This routine uses a ultra-gentle wash to preserve natural oils, followed by a deeply hydrating toner to quench skin thirst. A barrier-repairing gel then locks in that water, while a protective daily shield keeps sensitive skin safe from sun damage without irritation."
    },
    2: {
        "cleanser": "Skintific 5X Ceramide Low pH Cleanser",
        "moisturizer": "Skintific 5X Ceramide Barrier Repair Moisture Gel",
        "toner_serum": "Skintific Gentle Retinol Renewal Serum",
        "sunscreen": "Wardah UV Shield Essential Sunscreen Gel",
        "desc": "Designed to fight signs of aging, this setup uses a non-drying wash and a strengthening gel to create a resilient, healthy skin base. A gentle cell-renewing treatment then smooths out wrinkles, while a vital sun shield prevents further loss of firmness and skin bounce."
    },
    3: {
        "cleanser": "Wardah C-Defense Brightening Fluffy Cleanser",
        "moisturizer": "Wardah SymRadiance 399 + 5% Niacinamide Moisture Gel",
        "toner_serum": "Wardah C-Defense Vitamin C Serum",
        "sunscreen": "Wardah UV Shield Light Matte Sun Stick",
        "desc": "A fully brightening routine that starts with a vitamin-rich foaming wash to wake up tired skin, paired with a specialized dark spot serum and gel to actively fade stubborn discoloration. It finishes with a convenient anti-shine shield to stop the sun from darkening spots."
    },
    4: {
        "cleanser": "Glad2Glow Blueberry Ceramide Gentle Cleanser",
        "moisturizer": "Glad2Glow Blueberry 5X Ceramide Moisture Gel",
        "toner_serum": "Skintific 5% AHA BHA PHA Exfoliating Toner",
        "sunscreen": "Glad2Glow Ultra Light Sunscreen SPF 50",
        "desc": "This combo uses a soothing berry wash and a cooling gel to keep skin calm, balanced, and perfectly comfortable. A mild skin-smoothing liquid gently melts away rough skin flakes, while a lightweight daily shield protects the fresh, smooth skin underneath."
    },
    5: {
        "cleanser": "Wardah C-Defense Brightening Fluffy Cleanser",
        "moisturizer": "Glad2Glow Yuja Symwhite 377 Dark Spot Moisturizer",
        "toner_serum": "Skintific 10% Niacinamide Brightening Serum",
        "sunscreen": "Skintific Ultra Light Serum Sunscreen",
        "desc": "Ideal for clearing up marks, this routine pairs a fresh brightening foam with a high-strength tone-evening concentrate and a targeted spot gel to fade old scars. A weightless, water-light daily shield keeps your glowing results protected all day."
    },
    6: {
        "cleanser": "Skintific 3X Acid Acne Gel Cleanser",
        "moisturizer": "Glad2Glow Centella Soothing Gel Moisturizer",
        "toner_serum": "Glad2Glow Centella 2% Salicylic Acid Acne Serum",
        "sunscreen": "Glad2Glow Ultra Light Sunscreen SPF 50",
        "desc": "Built to stop heavy breakouts, this routine deploys a deep-cleansing acid wash and a targeted oil-clearing concentrate to shrink active pimples and clean deep inside pores. A light botanical gel instantly calms down the redness, while a non-greasy shield protects acne-prone skin from sun irritation."
    },
    7: {
        "cleanser": "Skintific White Truffle Cleansing Essence",
        "moisturizer": "Skintific 5X Ceramide Barrier Repair Moisture Gel",
        "toner_serum": "Skintific Glycolic Acid Daily Clarifying Toner",
        "sunscreen": "Skintific Ultra Light Serum Sunscreen",
        "desc": "This routine smooths out bumpy skin by starting with a luxury hydrating wash and a water-rich gel that plumps away rough textures. A daily exfoliating fluid sweeps away stubborn bumps on the surface, while a weightless shield ensures the sun doesn't worsen uneven areas."
    },
    8: {
        "cleanser": "Skintific 5X Ceramide Low pH Cleanser",
        "moisturizer": "Skintific 5X Ceramide Barrier Repair Moisture Gel",
        "toner_serum": "Wardah Renew You Anti-Aging Intensive Serum",
        "sunscreen": "Skintific 5X Ceramide Serum Sunscreen",
        "desc": "This setup targets sagging skin by using a balanced wash and a strengthening gel to deeply lock in hydration. A rich, firming peptide liquid works from within to plump up fine lines, while a daily bounce-preserving shield blocks UV rays that break down skin youthfulness."
    },
    9: {
        "cleanser": "Skintific 3X Acid Acne Gel Cleanser",
        "moisturizer": "Glad2Glow Blueberry 5X Ceramide Moisture Gel",
        "toner_serum": "Glad2Glow Centella 2% Salicylic Acid Acne Serum",
        "sunscreen": "Glad2Glow Ultra Light Sunscreen SPF 50",
        "desc": "A safe, balanced routine for teenagers that uses a mild acne-fighting wash and a pore-clearing concentrate to stop breakouts and blackheads before they grow. A lightweight, refreshing gel keeps the face moisturized without clogs, and an easy daily shield protects young skin cleanly."
    },
    10: {
        "cleanser": "Skintific 3X Acid Acne Gel Cleanser",
        "moisturizer": "Skintific 5X Ceramide Barrier Repair Moisture Gel",
        "toner_serum": "Skintific 5% AHA BHA PHA Exfoliating Toner",
        "sunscreen": "Wardah UV Shield Light Matte Sun Stick",
        "desc": "An intensive skin-clearing system that uses a strong acid wash and a multi-acid exfoliating fluid to deeply clean out large pores and resurface the face. A comforting, defensive gel keeps the skin completely calm, while a handy matte shield blocks sun sensitivity."
    }
}


# ==========================================
# 2. THE RULE ENGINE
# ==========================================
# Instead of 84 IF statements, we store rules as a list of dictionaries.
# I have added the first few rules here as an example. You will paste the rest here.
RULES = [
    # ---------------------------------------------------------
    # PART 1 : TEEN (AGE 15 – 19)
    # ---------------------------------------------------------
    # Base Skin: Tight/dry > Dry
    {"rule": 1, "age": "teen", "feel": "tight/dry", "concern": "acne", "type": "Dry", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 2, "age": "teen", "feel": "tight/dry", "concern": "texture", "type": "Dry", "ingredients": [3, 8, 9], "routine_id": 4},
    {"rule": 3, "age": "teen", "feel": "tight/dry", "concern": "tone", "type": "Dry", "ingredients": [4, 5, 8], "routine_id": 5},
    {"rule": 4, "age": "teen", "feel": "tight/dry", "concern": "aging", "type": "Dry", "ingredients": [9, 8, 5], "routine_id": 1},

    # Base Skin: Shiny - All area > Oily
    {"rule": 5, "age": "teen", "feel": "shiny_all", "concern": "acne", "type": "Oily", "ingredients": [1, 10, 5], "routine_id": 6},
    {"rule": 6, "age": "teen", "feel": "shiny_all", "concern": "texture", "type": "Oily", "ingredients": [1, 3, 8], "routine_id": 9},
    {"rule": 7, "age": "teen", "feel": "shiny_all", "concern": "tone", "type": "Oily", "ingredients": [4, 5, 8], "routine_id": 5},
    {"rule": 8, "age": "teen", "feel": "shiny_all", "concern": "aging", "type": "Oily", "ingredients": [9, 8, 5], "routine_id": 1},

    # Base Skin: Shiny - T-zone area > Combination
    {"rule": 9, "age": "teen", "feel": "shiny_tzone", "concern": "acne", "type": "Combination", "ingredients": [1, 10, 5], "routine_id": 6},
    {"rule": 10, "age": "teen", "feel": "shiny_tzone", "concern": "texture", "type": "Combination", "ingredients": [1, 3, 8], "routine_id": 9},
    {"rule": 11, "age": "teen", "feel": "shiny_tzone", "concern": "tone", "type": "Combination", "ingredients": [4, 5, 8], "routine_id": 5},
    {"rule": 12, "age": "teen", "feel": "shiny_tzone", "concern": "aging", "type": "Combination", "ingredients": [9, 8, 5], "routine_id": 1},

    # Base Skin: Irritated - Very often red > Sensitive
    {"rule": 13, "age": "teen", "feel": "red_very_often", "concern": "acne", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 14, "age": "teen", "feel": "red_very_often", "concern": "texture", "type": "Sensitive", "ingredients": [8, 9, 5], "routine_id": 1},
    {"rule": 15, "age": "teen", "feel": "red_very_often", "concern": "tone", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 16, "age": "teen", "feel": "red_very_often", "concern": "aging", "type": "Sensitive", "ingredients": [9, 8, 5], "routine_id": 1},

    # Base Skin: Irritated - Sometimes red > Sensitive
    {"rule": 17, "age": "teen", "feel": "red_sometimes", "concern": "acne", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 18, "age": "teen", "feel": "red_sometimes", "concern": "texture", "type": "Sensitive", "ingredients": [3, 8, 9], "routine_id": 4},
    {"rule": 19, "age": "teen", "feel": "red_sometimes", "concern": "tone", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 20, "age": "teen", "feel": "red_sometimes", "concern": "aging", "type": "Sensitive", "ingredients": [9, 8, 5], "routine_id": 1},

    # Base Skin: Irritated - Rarely red > Sensitive
    {"rule": 21, "age": "teen", "feel": "red_rarely", "concern": "acne", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 22, "age": "teen", "feel": "red_rarely", "concern": "texture", "type": "Sensitive", "ingredients": [3, 8, 9], "routine_id": 4},
    {"rule": 23, "age": "teen", "feel": "red_rarely", "concern": "tone", "type": "Sensitive", "ingredients": [4, 5, 8], "routine_id": 5},
    {"rule": 24, "age": "teen", "feel": "red_rarely", "concern": "aging", "type": "Sensitive", "ingredients": [9, 8, 5], "routine_id": 1},

    # Base Skin: Comfortable > Normal
    {"rule": 25, "age": "teen", "feel": "comfortable", "concern": "acne", "type": "Normal", "ingredients": [1, 10, 5], "routine_id": 6},
    {"rule": 26, "age": "teen", "feel": "comfortable", "concern": "texture", "type": "Normal", "ingredients": [1, 3, 8], "routine_id": 9},
    {"rule": 27, "age": "teen", "feel": "comfortable", "concern": "tone", "type": "Normal", "ingredients": [4, 5, 8], "routine_id": 5},
    {"rule": 28, "age": "teen", "feel": "comfortable", "concern": "aging", "type": "Normal", "ingredients": [9, 8, 5], "routine_id": 1},

    # ---------------------------------------------------------
    # PART 2 : YOUNG ADULT (AGE 20 – 39)
    # ---------------------------------------------------------
    # Base Skin: Tight/dry > Dry
    {"rule": 29, "age": "young_adult", "feel": "tight/dry", "concern": "acne", "type": "Dry", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 30, "age": "young_adult", "feel": "tight/dry", "concern": "texture", "type": "Dry", "ingredients": [2, 3, 8], "routine_id": 7},
    {"rule": 31, "age": "young_adult", "feel": "tight/dry", "concern": "tone", "type": "Dry", "ingredients": [4, 5, 2], "routine_id": 3},
    {"rule": 32, "age": "young_adult", "feel": "tight/dry", "concern": "aging", "type": "Dry", "ingredients": [6, 7, 9], "routine_id": 2},

    # Base Skin: Shiny - All area > Oily
    {"rule": 33, "age": "young_adult", "feel": "shiny_all", "concern": "acne", "type": "Oily", "ingredients": [1, 10, 5], "routine_id": 6},
    {"rule": 34, "age": "young_adult", "feel": "shiny_all", "concern": "texture", "type": "Oily", "ingredients": [2, 1, 3], "routine_id": 10},
    {"rule": 35, "age": "young_adult", "feel": "shiny_all", "concern": "tone", "type": "Oily", "ingredients": [4, 5, 2], "routine_id": 3},
    {"rule": 36, "age": "young_adult", "feel": "shiny_all", "concern": "aging", "type": "Oily", "ingredients": [6, 7, 9], "routine_id": 2},

    # Base Skin: Shiny - T-zone area > Combination
    {"rule": 37, "age": "young_adult", "feel": "shiny_tzone", "concern": "acne", "type": "Combination", "ingredients": [1, 10, 5], "routine_id": 6},
    {"rule": 38, "age": "young_adult", "feel": "shiny_tzone", "concern": "texture", "type": "Combination", "ingredients": [2, 1, 3], "routine_id": 10},
    {"rule": 39, "age": "young_adult", "feel": "shiny_tzone", "concern": "tone", "type": "Combination", "ingredients": [4, 5, 2], "routine_id": 3},
    {"rule": 40, "age": "young_adult", "feel": "shiny_tzone", "concern": "aging", "type": "Combination", "ingredients": [6, 7, 9], "routine_id": 2},

    # Base Skin: Irritated - Very often red > Sensitive
    {"rule": 41, "age": "young_adult", "feel": "red_very_often", "concern": "acne", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 42, "age": "young_adult", "feel": "red_very_often", "concern": "texture", "type": "Sensitive", "ingredients": [8, 9, 5], "routine_id": 1},
    {"rule": 43, "age": "young_adult", "feel": "red_very_often", "concern": "tone", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 44, "age": "young_adult", "feel": "red_very_often", "concern": "aging", "type": "Sensitive", "ingredients": [7, 9, 8], "routine_id": 8},

    # Base Skin: Irritated - Sometimes red > Sensitive
    {"rule": 45, "age": "young_adult", "feel": "red_sometimes", "concern": "acne", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 46, "age": "young_adult", "feel": "red_sometimes", "concern": "texture", "type": "Sensitive", "ingredients": [3, 8, 9], "routine_id": 4},
    {"rule": 47, "age": "young_adult", "feel": "red_sometimes", "concern": "tone", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 48, "age": "young_adult", "feel": "red_sometimes", "concern": "aging", "type": "Sensitive", "ingredients": [7, 9, 8], "routine_id": 8},

    # Base Skin: Irritated - Rarely red > Sensitive
    {"rule": 49, "age": "young_adult", "feel": "red_rarely", "concern": "acne", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 50, "age": "young_adult", "feel": "red_rarely", "concern": "texture", "type": "Sensitive", "ingredients": [3, 8, 9], "routine_id": 4},
    {"rule": 51, "age": "young_adult", "feel": "red_rarely", "concern": "tone", "type": "Sensitive", "ingredients": [4, 5, 8], "routine_id": 5},
    {"rule": 52, "age": "young_adult", "feel": "red_rarely", "concern": "aging", "type": "Sensitive", "ingredients": [6, 7, 9], "routine_id": 2},

    # Base Skin: Comfortable > Normal
    {"rule": 53, "age": "young_adult", "feel": "comfortable", "concern": "acne", "type": "Normal", "ingredients": [1, 10, 5], "routine_id": 6},
    {"rule": 54, "age": "young_adult", "feel": "comfortable", "concern": "texture", "type": "Normal", "ingredients": [2, 1, 3], "routine_id": 10},
    {"rule": 55, "age": "young_adult", "feel": "comfortable", "concern": "tone", "type": "Normal", "ingredients": [4, 5, 2], "routine_id": 3},
    {"rule": 56, "age": "young_adult", "feel": "comfortable", "concern": "aging", "type": "Normal", "ingredients": [6, 7, 9], "routine_id": 2},

    # ---------------------------------------------------------
    # PART 3 : MATURE ADULT (AGE 40 – ABOVE)
    # ---------------------------------------------------------
    # Base Skin: Tight/dry > Dry
    {"rule": 57, "age": "mature_adult", "feel": "tight/dry", "concern": "acne", "type": "Dry", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 58, "age": "mature_adult", "feel": "tight/dry", "concern": "texture", "type": "Dry", "ingredients": [2, 3, 8], "routine_id": 7},
    {"rule": 59, "age": "mature_adult", "feel": "tight/dry", "concern": "tone", "type": "Dry", "ingredients": [4, 5, 2], "routine_id": 3},
    {"rule": 60, "age": "mature_adult", "feel": "tight/dry", "concern": "aging", "type": "Dry", "ingredients": [6, 7, 9], "routine_id": 2},

    # Base Skin: Shiny - All area > Oily
    {"rule": 61, "age": "mature_adult", "feel": "shiny_all", "concern": "acne", "type": "Oily", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 62, "age": "mature_adult", "feel": "shiny_all", "concern": "texture", "type": "Oily", "ingredients": [2, 3, 8], "routine_id": 7},
    {"rule": 63, "age": "mature_adult", "feel": "shiny_all", "concern": "tone", "type": "Oily", "ingredients": [4, 5, 2], "routine_id": 3},
    {"rule": 64, "age": "mature_adult", "feel": "shiny_all", "concern": "aging", "type": "Oily", "ingredients": [6, 7, 9], "routine_id": 2},

    # Base Skin: Shiny - T-zone area > Combination
    {"rule": 65, "age": "mature_adult", "feel": "shiny_tzone", "concern": "acne", "type": "Combination", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 66, "age": "mature_adult", "feel": "shiny_tzone", "concern": "texture", "type": "Combination", "ingredients": [2, 3, 8], "routine_id": 7},
    {"rule": 67, "age": "mature_adult", "feel": "shiny_tzone", "concern": "tone", "type": "Combination", "ingredients": [4, 5, 2], "routine_id": 3},
    {"rule": 68, "age": "mature_adult", "feel": "shiny_tzone", "concern": "aging", "type": "Combination", "ingredients": [6, 7, 9], "routine_id": 2},

    # Base Skin: Irritated - Very often red > Sensitive
    {"rule": 69, "age": "mature_adult", "feel": "red_very_often", "concern": "acne", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 70, "age": "mature_adult", "feel": "red_very_often", "concern": "texture", "type": "Sensitive", "ingredients": [8, 9, 5], "routine_id": 1},
    {"rule": 71, "age": "mature_adult", "feel": "red_very_often", "concern": "tone", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 72, "age": "mature_adult", "feel": "red_very_often", "concern": "aging", "type": "Sensitive", "ingredients": [7, 9, 8], "routine_id": 8},

    # Base Skin: Irritated - Sometimes red > Sensitive
    {"rule": 73, "age": "mature_adult", "feel": "red_sometimes", "concern": "acne", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 74, "age": "mature_adult", "feel": "red_sometimes", "concern": "texture", "type": "Sensitive", "ingredients": [3, 8, 9], "routine_id": 4},
    {"rule": 75, "age": "mature_adult", "feel": "red_sometimes", "concern": "tone", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 76, "age": "mature_adult", "feel": "red_sometimes", "concern": "aging", "type": "Sensitive", "ingredients": [7, 9, 8], "routine_id": 8},

    # Base Skin: Irritated - Rarely red > Sensitive
    {"rule": 77, "age": "mature_adult", "feel": "red_rarely", "concern": "acne", "type": "Sensitive", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 78, "age": "mature_adult", "feel": "red_rarely", "concern": "texture", "type": "Sensitive", "ingredients": [3, 8, 9], "routine_id": 4},
    {"rule": 79, "age": "mature_adult", "feel": "red_rarely", "concern": "tone", "type": "Sensitive", "ingredients": [4, 5, 8], "routine_id": 5},
    {"rule": 80, "age": "mature_adult", "feel": "red_rarely", "concern": "aging", "type": "Sensitive", "ingredients": [6, 7, 9], "routine_id": 2},

    # Base Skin: Comfortable > Normal
    {"rule": 81, "age": "mature_adult", "feel": "comfortable", "concern": "acne", "type": "Normal", "ingredients": [5, 8, 9], "routine_id": 1},
    {"rule": 82, "age": "mature_adult", "feel": "comfortable", "concern": "texture", "type": "Normal", "ingredients": [2, 3, 8], "routine_id": 7},
    {"rule": 83, "age": "mature_adult", "feel": "comfortable", "concern": "tone", "type": "Normal", "ingredients": [4, 5, 2], "routine_id": 3},
    {"rule": 84, "age": "mature_adult", "feel": "comfortable", "concern": "aging", "type": "Normal", "ingredients": [6, 7, 9], "routine_id": 2}
]

# ==========================================
# 3. THE API ENDPOINT
# ==========================================
@app.route('/api/evaluate', methods=['POST'])
def evaluate_skin():
    # 1. Get data from the frontend
    user_data = request.json
    
    age = user_data.get('age')
    raw_feel = user_data.get('feel')
    shiny_area = user_data.get('shiny_area') # from Q3_shiny
    redness = user_data.get('redness')       # from Q3_irritated
    concern = user_data.get('concern')

    # 2. Format the "Feel" variable based on Q2 and Q3 branches
    feel_condition = ""
    if raw_feel == "tight/dry":
        feel_condition = "tight/dry"
    elif raw_feel == "comfortable":
        feel_condition = "comfortable"
    elif raw_feel == "shiny":
        feel_condition = "shiny_all" if shiny_area == "all area" else "shiny_tzone"
    elif raw_feel == "irritated":
        feel_condition = "red_very_often" if redness == "very often" else ("red_sometimes" if redness == "sometimes" else "red_rarely")

    # 3. Search for the matching rule
    matched_rule = None
    for rule in RULES:
        if rule['age'] == age and rule['feel'] == feel_condition and rule['concern'] == concern:
            matched_rule = rule
            break

    if not matched_rule:
        return jsonify({"error": "No matching rule found. Please check your inputs."}), 400

    # 4. Compile the output data
    skin_type_data = SKIN_TYPES[matched_rule['type']]
    
    ingredient_data = []
    for ing_id in matched_rule['ingredients']:
        ingredient_data.append(INGREDIENTS[ing_id])

    routine_data = ROUTINES[matched_rule['routine_id']]
    
    # Bundle the 4 products with their images
    product_data = [
        PRODUCTS.get(routine_data['cleanser'], {"name": routine_data['cleanser'], "image_url": ""}),
        PRODUCTS.get(routine_data['moisturizer'], {"name": routine_data['moisturizer'], "image_url": ""}),
        PRODUCTS.get(routine_data['toner_serum'], {"name": routine_data['toner_serum'], "image_url": ""}),
        PRODUCTS.get(routine_data['sunscreen'], {"name": routine_data['sunscreen'], "image_url": ""})
    ]

    # 5. Send it all back to the frontend
    return jsonify({
        "skin_type": skin_type_data,
        "ingredients": ingredient_data,
        "routine_desc": routine_data['desc'],
        "products": product_data
    })

if __name__ == '__main__':
    # Running with debug=True means it auto-restarts when you save!
    app.run(debug=True, port=5000)
