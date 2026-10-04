from __future__ import annotations

from src.data_access import load_budgets, load_employees
from src.tools.base import Tool, ToolResult


class BudgetTool(Tool):
    name = "budget_tool"

    def run(self, request: dict) -> ToolResult:
        requester_id = request.get("requester_id")
        cost = request.get("annual_cost_usd")
        employees = load_employees()
        budgets = load_budgets()
        employee = employees[employees["employee_id"] == requester_id]
        if employee.empty:
            return ToolResult(self.name, False, error=f"Requester {requester_id} not found")
        department = str(employee.iloc[0]["department"])
        budget = budgets[budgets["department"] == department]
        if budget.empty:
            return ToolResult(self.name, False, data={"department": department}, error="Department budget not found")
        row = budget.iloc[0]
        available = float(row["available_usd"])
        result = {
            "requester_id": requester_id,
            "department": department,
            "available_usd": available,
            "annual_cost_usd": cost,
            "within_budget": None if cost is None else float(cost) <= available,
        }
        return ToolResult(self.name, True, result)
