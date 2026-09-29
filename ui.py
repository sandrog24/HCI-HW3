from nicegui import ui
import requests

API_URL = "http://localhost:8005"

questions = []
ui.colors(primary="#1d4ed8", negative="#b91c1c")
ui.query("body").classes("bg-slate-100 text-slate-900")
page_body = ui.column().classes("w-full max-w-3xl mx-auto gap-6 py-6")

def api_get(path):
    try:
        # Attempt to send GET request to API
        response = requests.get(f"{API_URL}{path}", timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, GET was successful so return response data
        return response.json()
    except requests.RequestException as e:
        # GET request was unsuccessful
        # Send an alert with error details to the UI and return empty list
        ui.notify(f"Could not reach API: {e}", type="negative")
        return []

def api_post(path, data):
    try:
        # Attempt to send POST request to API with data payload
        response = requests.post(f"{API_URL}{path}", json=data, timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, POST was successful so return True
        return True
    except requests.RequestException as e:
        # POST request was unsuccessful
        # Send an alert with error details to the UI and return False
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False

def api_delete(path, id):
    try:
        response = requests.delete(f"{API_URL}{path}/{id}", timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        ui.notify(f"Could not delete question: {e}", type="negative")
        return False

def api_put(path, id, data):
    try:
        response = requests.put(f"{API_URL}{path}/{id}", json=data, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        ui.notify(f"Could not update question: {e}", type="negative")
        return False

def render_question(question):
    with ui.card().classes("w-full p-5 gap-4 rounded-xl border border-slate-200 shadow-sm") as card:
        card.on("click", lambda: toggle_answer(question))
        ui.label(question["q"]).classes("text-lg font-semibold leading-relaxed")
        with ui.column().classes("w-full bg-blue-50 border-l-4 border-blue-700 p-4 gap-1 rounded") as answer:
            answer.bind_visibility_from(question["state"], "show_answer")
            ui.label("Answer").classes("text-sm font-semibold text-blue-800")
            ui.label(question["a"]).classes("text-base leading-relaxed whitespace-pre-wrap")
        with ui.row().classes("w-full items-center justify-between gap-2"):
            ui.button(icon="visibility").props("flat no-caps").bind_text_from(
                question["state"], "show_answer",
                backward=lambda shown: "Hide answer" if shown else "Show answer"
            ).on("click.stop", lambda: toggle_answer(question))
            with ui.row().classes("gap-2"):
                ui.button("Edit", icon="edit").props("outline no-caps").on(
                    "click.stop", lambda: edit_question(question))
                ui.button("Delete", icon="delete", color="negative").props("flat no-caps").on(
                    "click.stop", lambda: delete_question(question["id"]))

def edit_question(question):
    with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg p-6 gap-4 rounded-xl"):
        ui.label("Edit question").classes("text-2xl font-bold")
        new_q = ui.textarea(label="Question", value=question["q"]).props("outlined").classes("w-full")
        new_a = ui.textarea(label="Answer", value=question["a"]).props("outlined").classes("w-full")

        def update_question():
            if api_put("/update", question["id"], {
                "question": new_q.value,
                "answer": new_a.value
            }):
                dialog.close()
                render_page()

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat no-caps")
            ui.button("Update question", on_click=update_question).props("unelevated no-caps")
    dialog.on("hide", dialog.delete)
    dialog.open()

def toggle_answer(question):
    question["state"]["show_answer"] = not question["state"]["show_answer"]

def delete_question(id):
    if api_delete("/delete", id):
        render_page()

def add_new_question(question, answer):
    api_post("/add", {"question": question, "answer": answer})
    render_page()

def render_text_inputs():
    with ui.card().classes("w-full p-6 gap-4 rounded-xl border border-slate-200 shadow-sm"):
        ui.label("Add a question").classes("text-xl font-bold")
        new_question_input = ui.input(label="New question").props("outlined clearable").classes("w-full")
        new_answer_input = ui.input(label="New answer").props("outlined clearable").classes("w-full")
        ui.button(text="Add question", icon="add", on_click=lambda: add_new_question(
            question=new_question_input.value,
            answer=new_answer_input.value
        )).props("unelevated no-caps")

def init_page():
    render_page()

def render_page():
    global questions
    questions = api_get("/questions")
    page_body.clear()
    with page_body:
        with ui.column().classes("gap-1"):
            ui.label("HCI Review").classes("text-3xl font-bold")
            ui.label("Test your recall. Tap a question or choose Show answer to check it.").classes("text-base text-slate-600")
        ui.label("Review questions").classes("text-xl font-bold")
        for question in questions:
            question["state"] = {"show_answer": False}
            render_question(question)
        render_text_inputs()
    

init_page()
ui.run(port=8084, title="HCI Review Application")
