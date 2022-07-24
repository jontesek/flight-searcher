from request_session import RequestSession


class HttpClient(RequestSession):

    def __init__(self, **kwargs):
        print("http client init called")
        if not kwargs.get("user_agent"):
            raise ValueError("You must provide user_agent")
        if not kwargs.get("max_retries"):
            kwargs["max_retries"] = 3
        if not kwargs.get("raise_for_status"):
            kwargs["raise_for_status"] = True
        if not kwargs.get("request_category"):
            kwargs["request_category"] = "general"
        super().__init__(**kwargs)
