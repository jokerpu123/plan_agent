import asyncio

from langgraph.checkpoint.memory import InMemorySaver
from app.graph import build_graph
from app.tools import clear_request_context, set_request_context


async def main():
    graph = build_graph(InMemorySaver())
    token = set_request_context("demo@example.com", 1)
    try:
        common = {"email": "demo@example.com", "user_id": 1, "history": [], "response": "",
                  "plan": {}, "analyses": [], "feedback": ""}
        react = await graph.ainvoke({**common, "message": "What tasks do I have today?"},
                                    {"configurable": {"thread_id": "smoke-react"}})
        print("REACT_RESULT", react.get("route"), repr(react.get("response")))
        assert react["route"] == "react" and react["response"]
        plan = await graph.ainvoke({**common, "message": "Make a coordinated five-day English study schedule for next week."},
                                   {"configurable": {"thread_id": "smoke-plan"}})
        assert plan["route"] == "plan" and plan.get("__interrupt__")
        print("REACT_OK", react["route"])
        print("PLAN_OK", plan["route"], len(plan["plan"]["tasks"]))
    finally:
        clear_request_context(token)


if __name__ == "__main__":
    asyncio.run(main())
