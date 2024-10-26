# dto_json

These tests assert that there has been no regression in:
- the format of json requests for the `choose` / `execute` endpoints of the json API
- the format of the json responses for the `choose` / `execute` endpoints
- the logic of ninja-taisen when choosing / executing moves. The optional seed field in `choose_request.json` is filled, ensuring the psuedo-random numbers are deterministic
