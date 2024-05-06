start:
	open "http://127.0.0.1:8000/docs" && cd src/moovitamix_fastapi && python3 -m uvicorn main:app

.PHONY: start
