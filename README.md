# Build the backend behind “New session”

Open slide 24. The user has chosen a repository, typed a request, and clicked Send. If they close the tab a second later, how could they find that task again? Today you will give it an ID, store it, and fetch it after a server restart. You can do this entire lesson on your computer without service accounts or keys.

## 1 · Read first (10 minutes)

Open your copy of [cloud_agent.md](https://chatgpt.com/library?file_id=libfile_2165cf13ffc081919da23d41d35d96d5&account_id=personal). Jump directly to §18 “What are the frontend, backend and API?” and §21 “What does the database store?” Read those two sections. On slide 37, locate Frontend, Backend and DB. Draw the two requests a browser needs to make to submit a task and later look it up. If you want a second explanation of persistence, read §34 of [cloud-agent(4).md](https://chatgpt.com/library?file_id=libfile_a21fc8ac00608191992a27874c63619f&account_id=personal).

## 2 · Understand the architecture (10 minutes)

| Component | Job in our Python implementation | Source folder |
|---|---|---|
| Browser and API | Today the interactive API page plays the role of the frontend. Enter the repository name and task, get a session ID, and use it to request status. | cloud_agent/main.py and models.py |
| Database | Save the request and its status on disk. Later it also holds ownership, job claims, and events. | cloud_agent/store.py and generated data/ |
| Worker and model | A separate Python process will claim queued sessions. Its harness will send context to a model, validate tool requests, record observations and decide when to stop. | cloud_agent/worker/ |
| Remote sandbox | E2B will supply one isolated workspace per session. The checkout, file edits and test processes live there. | cloud_agent/sandbox/ |
| Tools and GitHub integration | Tools will run commands, edit files and ask the user for input. A trusted GitHub integration will verify access, prepare the checkout and publish the reviewed branch and draft PR. | cloud_agent/tools/ and cloud_agent/github/ |

The four integration folders are empty in this starter. The working part today is browser → API → SQLite. Your virtual environment stores Python packages for this backend. The future sandbox runs a user's project on another machine. In the sample request, code100x/vendi is a repository label. Entering it saves text. Connecting to GitHub comes in a later lesson.

## 3 · Open the project and install the packages (10 minutes)

Extract the archive, open the vendi-python folder in your editor, then open a terminal in the folder containing requirements.txt. Use Python 3.11 or newer. Python 3.12 was used for the lesson. Create a virtual environment so this project's packages have their own home.

Windows PowerShell (activation is unnecessary):

    py -3 -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe -m uvicorn cloud_agent.main:app --reload

macOS or Linux:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python -m uvicorn cloud_agent.main:app --reload

Leave that terminal running. Open http://127.0.0.1:8000/docs in your browser. The address refers to your own computer. The installation command needs internet access, as does the default Swagger UI for its browser assets.

| Package | Why it is in requirements.txt |
|---|---|
| uvicorn | Listens for HTTP requests and serves the application. In cloud_agent.main:app, the left side names the Python module and the right side names its app object. |
| fastapi | Maps a method and path to a Python function. Also generates the interactive API page. |
| pydantic | Describes which fields a session request needs and checks their values. |
| sqlite3, uuid, pathlib, contextlib | Included in Python. These provide disk storage, IDs, paths and resource management. |

Later packages follow the lesson that needs them. For our chosen stack, httpx makes GitHub HTTP requests, PyJWT[crypto] signs the GitHub App's short-lived authentication assertion, e2b manages workspaces, and anthropic supplies a model client for tool calls. A small HTML/JavaScript page can receive progress events with the browser's EventSource API. Git is a separate program used for checkout and branches. Lesson 1 uses only the three packages in requirements.txt plus the standard library.

## 4 · See the code, then trace it (15 minutes)

Read cloud_agent/models.py, then this complete handler from cloud_agent/main.py.

~~~python
@app.post("/sessions", status_code=201)
def create_session(request: SessionRequest) -> Session:
    session = Session(id=uuid4(), **request.model_dump())
    store.save(session)
    return session
~~~

The decorator connects POST /sessions to this function. The SessionRequest type tells FastAPI to validate the incoming JSON. Whitespace-only tasks fail with HTTP 422. model_dump() gives the handler the validated repository and task fields. The two stars pass those fields to Session as named arguments. uuid4() supplies a fresh identifier and the model gives status the default queued. In cloud_agent/store.py, save inserts the row and commits it. Only then does the handler return the created session with HTTP 201.

Now read get_session in the same file. A GET with the same UUID retrieves the same row. A valid UUID with no saved row yields HTTP 404. Submitting the same text in another POST creates a second session. The unique ID belongs to one submission.

## 5 · Run an experiment on your own backend (10 minutes)

1. In /docs expand POST /sessions, click **Try it out**, enter the following JSON, then click **Execute**.

       {"repository": "code100x/vendi", "task": "Explain where the session page gets its progress updates."}

2. Under **Server response**, find 201 and copy the returned id. Expand GET /sessions/{session_id}, click **Try it out**, paste the ID and execute. Expect HTTP 200 with the same repository, task, ID and status.
3. Stop the server with Ctrl+C. Run the same Uvicorn command in the same folder. Refresh /docs, paste the old ID into GET, and execute again. Predict the result first. The database file is data/sessions.sqlite3.
4. Try a new POST with a task containing only spaces. Compare its response with a GET for an unknown, well-formed UUID such as 00000000-0000-4000-8000-000000000000. One request fails input validation. The other reaches the database.
5. Your session will stay queued throughout this lesson. Implementing the component that moves it to running is a later milestone. This local, single-user service binds to loopback. The GitHub lesson adds sign-in and repository authorization.

## 6 · Quiz (10 minutes)

Open a second terminal in this folder. Run python lessons/quiz.py using the same Python executable as above. Answer ten questions one at a time. You will predict responses, order operations, select fields, complete a route, and diagnose a failed request. Each answer unlocks an explanation. You can also take the quiz in chat.

## What to study before each next build

The numbered sections below refer to cloud_agent.md. Times are hands-on estimates. For each milestone, read the named sections first, open the matching code with one question in mind, run it, explain one result in your own words, then take the milestone quiz. The first lesson is supplied here. The rows below describe the next builds in order.

| Milestone and budget | Read first | Build and check |
|---|---|---|
| 1 · Session API, 65 min | §§18 and 21, slides 24 and 37 | Submit and retrieve one real session after a restart. |
| 2 · GitHub connection, 3 × 60 min | §§25–27 and slides 10, 11, 13 and 19 | Distinguish the signed-in user from the app installation. Connect one chosen practice repository. Check both installation access and the user's access before accepting work on it. |
| 3 · Worker and workspace, 3 × 75 min | §§5–10, 19–20 and slide 25 | Claim one authorized session, start an E2B sandbox, prepare the pinned checkout, change state, then clean up. Watch how long startup takes. |
| 4 · Tools and agent loop, 4 × 75 min | §§2–4, 12, 14 and 17, slides 52, 53 and 56 | Add shell and editor tools, then model-directed tool calls with a step limit. Ask and resume when the user needs to decide. Keep model credentials with the worker. |
| 5 · Progress screen, 2 × 75 min | §§21–24 and 36, slide 37 | Save ordered events, build a small status page and stream events from FastAPI. Close the tab mid-run, reconnect, and recover the log. |
| 6 · Draft PR and recovery, 4 × 75 min | §§25, 28–32 and 34, slides 19 and 53 | Review the diff, run checks on the candidate revision, then publish it to a branch in your practice repo. Retry after interruption and verify only one PR exists. |

For reference, the checked-in [Vendi session page](https://github.com/code100x/vendi/blob/fa685eff3479ab2179b15a5674653ce0c8622a4a/apps/web/src/pages/session/SessionPage.tsx) uses a session ID to request fresh data. When you reach milestone 5, search for refetchInterval to see exactly how often it polls. Our Python version will try server-sent events on the same kind of task. Our V1 uses one worker running the harness outside the sandbox. The lecture also explores running it inside and using several agents.

For today's two external references, look up request-body validation in [FastAPI](https://fastapi.tiangolo.com/tutorial/body/) and isolated project packages in [Python's venv guide](https://docs.python.org/3/library/venv.html).
