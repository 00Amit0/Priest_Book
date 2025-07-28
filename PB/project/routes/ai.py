# from fastapi import APIRouter, Form
# from db import db
# import requests
# import re
# from bson import ObjectId

# router = APIRouter()

# def serialize_mongo_document(doc):
#     if not doc:
#         return None
#     return {
#         key: str(value) if isinstance(value, ObjectId) else value
#         for key, value in doc.items()
#     }

# def serialize_list_of_documents(docs):
#     return [serialize_mongo_document(doc) for doc in docs]

# @router.post("/chat")
# def rag_chat(query: str = Form(...), userId: str = Form(...)):
#     query = query.lower()
#     context_parts = []
#     structured_response = {
#         "booking": None,
#         "pandits": [],
#         "palmistry": None
#     }

#     # 👤 1. User Booking Info
#     booking = db.bookings.find_one({"userId": userId})
#     if booking:
#         structured_response["booking"] = serialize_mongo_document(booking)
#         pandit = db.pandits.find_one({"panditId": booking["panditId"]})
#         if pandit:
#             context_parts.append(
#                 f"The user booked Pandit {pandit['name']} from {pandit['location']} "
#                 f"who speaks {', '.join(pandit['language'])} for {booking.get('purpose', 'some purpose')} "
#                 f"on {booking['date']} at {booking['time']}."
#             )

#     # 🔍 2. Pandit Search via Query Filters
#     if "pandit" in query:
#         query_words = re.findall(r"\b[a-zA-Z0-9]+\b", query)

#         filters = {}

#         # a. Detect location
#         known_locations = {p["location"].lower() for p in db.pandits.find({}, {"location": 1})}
#         for word in query_words:
#             if word.lower() in known_locations:
#                 filters["location"] = {"$regex": word, "$options": "i"}
#                 break

#         # b. Detect language
#         known_languages = {lang.lower() for p in db.pandits.find({}, {"language": 1}) for lang in p.get("language", [])}
#         for word in query_words:
#             if word.lower() in known_languages:
#                 filters["language"] = {"$in": [re.compile(word, re.IGNORECASE)]}
#                 break

#         # c. Detect experience
#         for i, word in enumerate(query_words):
#             if word.isdigit() and i + 1 < len(query_words) and query_words[i + 1] in {"year", "years", "experience"}:
#                 filters["experience"] = {"$gte": int(word)}
#                 break
#             if word in {"experience"} and i > 0 and query_words[i - 1].isdigit():
#                 filters["experience"] = {"$gte": int(query_words[i - 1])}
#                 break

#         # d. Query MongoDB
#         pandit_list = list(db.pandits.find(filters)) if filters else []

#         if pandit_list:
#             structured_response["pandits"] = serialize_list_of_documents(pandit_list)
#             details = []
#             for p in pandit_list:
#                 details.append(
#                     f"Pandit {p['name']} is from {p['location']} and speaks {', '.join(p['language'])}. "
#                     f"They have {p['experience']} years of experience."
#                 )
#             context_parts.append("Matching Pandits:\n" + "\n".join(details))
#         else:
#             fallback_pandits = list(db.pandits.find().sort("experience", -1).limit(3))
#             if fallback_pandits:
#                 structured_response["pandits"] = serialize_list_of_documents(fallback_pandits)
#                 details = []
#                 for p in fallback_pandits:
#                     details.append(
#                         f"Pandit {p['name']} is from {p['location']} and speaks {', '.join(p['language'])}. "
#                         f"They have {p['experience']} years of experience."
#                     )
#                 context_parts.append("No exact match found. Here are some experienced pandits:\n" + "\n".join(details))
#             else:
#                 context_parts.append("No pandits found in the system.")

#     # ✋ 3. Palm Reading
#     if "palm" in query or "hand" in query:
#         palm_data = db.palmistry.find_one({"userId": userId}, sort=[("_id", -1)])
#         if palm_data and palm_data.get("result"):
#             structured_response["palmistry"] = palm_data["result"]
#             context_parts.append(f"Palmistry result: {palm_data['result']}")
#         elif palm_data:
#             context_parts.append("Palm image uploaded but result is not available.")
#         else:
#             context_parts.append("No palmistry data available for this user.")

#     # 🧐 4. Construct AI Prompt
#     context = "\n".join(context_parts)
#     if not context:
#         context = "There is no data about this user or requested pandit in the system."

#     prompt = (
#         "You are a smart assistant for a Pandit booking platform.\n"
#         "Only use the following context to answer the user's question.\n"
#         "If something is not mentioned here, say you don't know.\n\n"
#         f"--- CONTEXT START ---\n{context}\n--- CONTEXT END ---\n\n"
#         f"User's question: {query}\n"
#         f"Answer:"
#     )

#     # 🧠 5. Call Local LLM (via Ollama)
#     try:
#         response = requests.post("http://localhost:11434/api/generate", json={
#             "model": "llama3",
#             "prompt": prompt,
#             "stream": False
#         })
#         answer = response.json().get("response", "Sorry, AI did not respond.")
#         return {
#             "response": answer,
#             "structured_data": structured_response
#         }
#     except Exception as e:
#         return {"error": f"AI service error: {str(e)}"}


from fastapi import APIRouter, Form, UploadFile, File
from db import db
import requests
import uuid
import re
from bson import ObjectId
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def serialize_mongo_document(doc):
    if not doc:
        return None
    return {
        key: str(value) if isinstance(value, ObjectId) else value
        for key, value in doc.items()
    }

def serialize_list_of_documents(docs):
    return [serialize_mongo_document(doc) for doc in docs]

# @router.post("/palmistry/upload")
# def upload_palm(userId: str = Form(...), file: UploadFile = File(...)):
#     # Create user-specific temp folder
#     user_folder = os.path.join(UPLOAD_DIR, userId)
#     os.makedirs(user_folder, exist_ok=True)

#     filename = f"{uuid.uuid4()}_{file.filename}"
#     filepath = os.path.join(user_folder, filename)
#     with open(filepath, "wb") as f:
#         f.write(file.file.read())

#     # Auto-generate palm reading using LLM
#     fake_prompt = (
#         "You are an expert palmist. Analyze the uploaded palm image based on filename only and generate a general palm reading."
#         f" The file path is: {filepath}. Use creative reasoning."
#         " End the response with: 'Note: This palm reading is AI-generated and may not be accurate.'"
#     )

#     try:
#         response = requests.post("http://localhost:11434/api/generate", json={
#             "model": "llama3",
#             "prompt": fake_prompt,
#             "stream": False
#         })
#         palm_result = response.json().get("response", None)
#     except Exception as e:
#         palm_result = None

#     db.palmistry.insert_one({
#         "userId": userId,
#         "image_path": filepath,
#         "result": palm_result
#     })

#     return {
#         "message": "Palm uploaded successfully",
#         "image_path": filepath,
#         "result": palm_result or "Palm image uploaded, but AI response not available."
#     }

@router.post("/palmistry/upload")
def upload_palm(userId: str = Form(...), file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        return {"error": "Only image files are allowed for palm reading."}

    # Create user-specific temp folder
    user_folder = os.path.join(UPLOAD_DIR, userId)
    os.makedirs(user_folder, exist_ok=True)

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(user_folder, filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())

    # Attempt LLaVA-based palm analysis
    palm_result = None
    try:
        llava_response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llava",
            "prompt": "Give a detailed palm reading based on the uploaded hand image."
                      " End the response with: 'Note: This palm reading is AI-generated and may not be accurate.'",
            "images": [filepath],
            "stream": False
        })
        if llava_response.status_code == 200:
            palm_result = llava_response.json().get("response")
    except:
        pass

    # Fallback: filename-based prompt using LLaMA
    if not palm_result:
        try:
            fallback_prompt = (
                "You are an expert palmist. Analyze the uploaded palm image based on filename only and generate a general palm reading."
                f" The file path is: {filepath}. Use creative reasoning."
                " End the response with: 'Note: This palm reading is AI-generated and may not be accurate.'"
            )
            response = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3",
                "prompt": fallback_prompt,
                "stream": False
            })
            palm_result = response.json().get("response", None)
        except:
            palm_result = None

    db.palmistry.insert_one({
        "userId": userId,
        "image_path": filepath,
        "result": palm_result
    })

    return {
        "message": "Palm uploaded successfully",
        "image_path": filepath,
        "result": palm_result or "Palm image uploaded, but AI response not available."
    }
    
@router.post("/chat")
def rag_chat(query: str = Form(...), userId: str = Form(...)):
    query = query.lower()
    context_parts = []
    structured_response = {
        "booking": None,
        "pandits": [],
        "palmistry": None,
        "history": []
    }

    # 🧠 Load last 10 Q&A from chat history
    # history_docs = list(db.chat_history.find({"userId": userId}).sort("_id", -1).limit(10))
    # history_text = "\n".join([f"Q: {h['query']}\nA: {h['response']}" for h in reversed(history_docs)])
    # if history_text:
    #     context_parts.append("Conversation history:\n" + history_text)
    #     structured_response["history"] = [
    #         {"query": h['query'], "response": h['response']} for h in reversed(history_docs)
    #     ]
    # 🧠 Load last 10 Q&A from chat history (used only for memory/context, not overriding real data)
    # history_docs = list(db.chat_history.find({"userId": userId}).sort("_id", -1).limit(10))
    # history_text = "\n".join([f"Q: {h['query']}\nA: {h['response']}" for h in reversed(history_docs)])

    # if history_text:
    #     context_parts.append("Past conversation history (for context only):\n" + history_text)
    #     structured_response["history"] = [
    #         {"query": h['query'], "response": h['response']} for h in reversed(history_docs)
    #     ]

    # 👤 1. User Booking Info
    booking = db.bookings.find_one({"userId": userId})
    if booking:
        structured_response["booking"] = serialize_mongo_document(booking)
        pandit = db.pandits.find_one({"panditId": booking["panditId"]})
        if pandit:
            context_parts.append(
                f"The user booked Pandit {pandit['name']} from {pandit['location']} "
                f"who speaks {', '.join(pandit['language'])} for {booking.get('purpose', 'some purpose')} "
                f"on {booking['date']} at {booking['time']}."
            )

    # 🔍 2. Pandit Search via Query Filters
    if "pandit" in query:
        query_words = re.findall(r"\b[a-zA-Z0-9]+\b", query)

        filters = {}

        # a. Detect location
        known_locations = {p["location"].lower() for p in db.pandits.find({}, {"location": 1})}
        for word in query_words:
            if word.lower() in known_locations:
                filters["location"] = {"$regex": word, "$options": "i"}
                break

        # b. Detect language
        known_languages = {lang.lower() for p in db.pandits.find({}, {"language": 1}) for lang in p.get("language", [])}
        for word in query_words:
            if word.lower() in known_languages:
                filters["language"] = {"$in": [re.compile(word, re.IGNORECASE)]}
                break

        # c. Detect experience
        for i, word in enumerate(query_words):
            if word.isdigit() and i + 1 < len(query_words) and query_words[i + 1] in {"year", "years", "experience"}:
                filters["experience"] = {"$gte": int(word)}
                break
            if word in {"experience"} and i > 0 and query_words[i - 1].isdigit():
                filters["experience"] = {"$gte": int(query_words[i - 1])}
                break

        # d. Query MongoDB
        # pandit_list = list(db.pandits.find(filters)) if filters else []
        pandit_list = list(db.pandits.find(filters)) if filters else list(db.pandits.find())

        if pandit_list:
            structured_response["pandits"] = serialize_list_of_documents(pandit_list)
            details = []
            for p in pandit_list:
                details.append(
                    f"Pandit {p['name']} is from {p['location']} and speaks {', '.join(p['language'])}. "
                    f"They have {p['experience']} years of experience."
                )
            context_parts.append("Matching Pandits:\n" + "\n".join(details))
        else:
            fallback_pandits = list(db.pandits.find().sort("experience", -1).limit(3))
            if fallback_pandits:
                structured_response["pandits"] = serialize_list_of_documents(fallback_pandits)
                details = []
                for p in fallback_pandits:
                    details.append(
                        f"Pandit {p['name']} is from {p['location']} and speaks {', '.join(p['language'])}. "
                        f"They have {p['experience']} years of experience."
                    )
                context_parts.append("No exact match found. Here are some experienced pandits:\n" + "\n".join(details))
            else:
                context_parts.append("No pandits found in the system.")

    # ✋ 3. Palm Reading
    if "palm" in query or "hand" in query:
        palm_data = db.palmistry.find_one({"userId": userId}, sort=[("_id", -1)])
        if palm_data and palm_data.get("result"):
            structured_response["palmistry"] = palm_data["result"]
            context_parts.append(f"Palmistry result: {palm_data['result']}")
        elif palm_data:
            context_parts.append("Palm image uploaded but result is not available.")
        else:
            context_parts.append("No palmistry data available for this user.")

    # 🤨 4. Construct AI Prompt
    context = "\n".join(context_parts)
    if not context:
        context = "There is no data about this user or requested pandit in the system."

    prompt = (
        "You are a smart assistant for a Pandit booking platform.\n"
        "Only use the following context to answer the user's question.\n"
        "If something is not mentioned here, say you don't know.\n\n"
        f"--- CONTEXT START ---\n{context}\n--- CONTEXT END ---\n\n"
        f"User's question: {query}\n"
        f"Answer:"
    )

    # 🧠 5. Call Local LLM (via Ollama)
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        })
        answer = response.json().get("response", "Sorry, AI did not respond.")

        # Save to chat history
        # db.chat_history.insert_one({"userId": userId, "query": query, "response": answer})

        return {
            "response": answer,
            "structured_data": structured_response
        }
    except Exception as e:
        return {"error": f"AI service error: {str(e)}"}

