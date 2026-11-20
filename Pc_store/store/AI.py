# store/AI.py
import json
from google import genai
from django.conf import settings
from store.models import Product, CartItem

# Initialize Gemini AI client
client = None
if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        print("Gemini client error:", e)


def get_store_catalog_context():
    """
    Get a simple text list of all products in our store.
    """
    lines = []
    products = Product.objects.all().order_by('part_type', 'product_price')
    for p in products:
        lines.append(f"- [ID: {p.id}] {p.product_name} | Price: Rs.{p.product_price} | Type: {p.part_type}")
    return "\n".join(lines)


def add_products_to_user_cart(product_ids, user=None):
    """
    Add products to user's cart (1 of each item, no 3x duplicate).
    """
    if not user or not user.is_authenticated:
        return False, "Please <a href='/login/' style='color:#00e676; font-weight:bold;'>Log In</a> to save this build to your cart."

    # Remove duplicates from the ID list
    unique_ids = []
    for pid in product_ids:
        if pid not in unique_ids:
            unique_ids.append(pid)

    added_items = []
    total_price = 0

    for pid in unique_ids:
        try:
            prod = Product.objects.get(id=int(pid))
            cart_item, created = CartItem.objects.get_or_create(
                user=user,
                product=prod,
                defaults={'quantity': 1}
            )
            # Ensure quantity is 1 for a PC build component
            if not created:
                cart_item.quantity = 1
                cart_item.save()

            added_items.append(prod.product_name)
            total_price += float(prod.product_price)
        except Exception:
            continue

    if added_items:
        msg = f"🛒 **Successfully added {len(added_items)} component(s) to your cart!** (Total: Rs.{total_price:,.2f})\n\n"
        msg += "<a href='/cart/' style='display:inline-block; background:linear-gradient(135deg, #00e676, #00b0ff); color:#000; font-weight:bold; padding:8px 16px; border-radius:8px; text-decoration:none;'>View Shopping Cart & Checkout ➔</a>"
        return True, msg

    return False, "Could not add the selected items to the cart."


def get_ai_parts(user_prompt: str, chat_history: list = None, user=None) -> str:
    """
    Basic AI Hardware Assistant function.
    Answers hardware questions, builds custom PCs for any budget, and adds to cart.
    """
    if not user_prompt or not user_prompt.strip():
        return "👋 Hi! I am your **NEXORIG AI Assistant** (Build Beyond Limits).\n\nAsk me anything about PC parts, custom builds for your budget, or tell me to add any build directly to your cart!"

    # 1. Check if user wants to clear cart
    lower = user_prompt.lower()
    if "clear cart" in lower or "empty cart" in lower:
        if user and user.is_authenticated:
            CartItem.objects.filter(user=user).delete()
            return "🗑️ Your cart has been cleared! What would you like to build next?"
        return "Please log in to manage your shopping cart."

    # 2. Build conversation history text
    history_text = ""
    if chat_history and isinstance(chat_history, list):
        for item in chat_history[-6:]:
            sender = "Customer" if item.get("role") == "user" else "Assistant"
            text = str(item.get("text", ""))[:200]
            if text:
                history_text += f"{sender}: {text}\n"

    # 3. Get store catalog text
    catalog_text = get_store_catalog_context()

    # 4. Create simple prompt for Gemini
    prompt = f"""You are the friendly and expert PC Hardware Assistant for 'NEXORIG' (Tagline: Build Beyond Limits - premier Indian PC components & custom rigs store at nexorig.com).

Recent conversation:
{history_text}

Customer message: "{user_prompt}"
Customer Logged In: {"Yes (" + user.username + ")" if user and user.is_authenticated else "No"}

Store Inventory:
{catalog_text}

Rules:
1. When asked to build a PC (or given a budget), pick compatible parts from our Store Inventory (CPU, Motherboard, GPU, RAM, Storage, PSU, Cabinet, Cooler).
2. Calculate the exact total price in Rs. and show the build clearly in a table.
3. If asked about any component, comparison, or accessories (like thermal paste, cables), explain clearly with prices from our inventory.
4. Welcome them to NEXORIG with enthusiastic energy.
5. If the customer asks to "add to cart", "buy this", or "add this build", include this tag at the very end:
[ADD_TO_CART: id1, id2, id3, ...]
Use the real numeric product IDs from our store list.
6. If they have not asked to add to cart yet, suggest: "Would you like me to add this build to your cart? Just say **'Add this build to cart'**!"
"""

    reply_text = ""

    # Call Gemini model
    if client:
        try:
            resp = client.models.generate_content(
                model='gemini-3.5-flash-lite',
                contents=prompt
            )
            if resp and resp.text:
                reply_text = resp.text.strip()
        except Exception as e:
            print("Gemini error:", e)

    # Simple fallback if AI is offline
    if not reply_text:
        reply_text = "Here are some top components from our store:\n\n"
        for p in Product.objects.all()[:5]:
            reply_text += f"• **{p.product_name}** — Rs.{p.product_price}\n"
        reply_text += "\nSay **'Add to cart'** to add parts to your cart!"

    # 5. Process [ADD_TO_CART: id1, id2, ...] if present
    if "[ADD_TO_CART:" in reply_text:
        start_idx = reply_text.find("[ADD_TO_CART:")
        end_idx = reply_text.find("]", start_idx)
        if end_idx != -1:
            tag = reply_text[start_idx : end_idx + 1]
            ids_str = reply_text[start_idx + 13 : end_idx]
            reply_text = reply_text.replace(tag, "").strip()

            ids = []
            for piece in ids_str.split(","):
                piece = piece.strip()
                if piece.isdigit():
                    ids.append(int(piece))

            if ids:
                success, cart_msg = add_products_to_user_cart(ids, user=user)
                reply_text += f"\n\n---\n{cart_msg}"

    return reply_text


# Backward compatibility aliases
get_ai_parts_ = get_ai_parts
get_ai_stylist_recommendation = get_ai_parts
