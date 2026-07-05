#!/usr/bin/env python3
"""Run the FastAPI development server."""
import asyncio
import sys

# Windows requires SelectorEventLoop for psycopg async support
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
