from __future__ import annotations

from src.data_access import load_purchase_history, load_software_catalog
from src.tools.base import Tool, ToolResult


class SoftwareTool(Tool):
    name = "software_tool"

    def run(self, request: dict) -> ToolResult:
        catalog = load_software_catalog()
        history = load_purchase_history()
        product = str(request.get("product_name", "")).lower()
        vendor = str(request.get("vendor_name", "")).lower()
        category = str(request.get("category", "")).lower()

        same_product = catalog[catalog["product_name"].str.lower() == product]
        same_vendor = catalog[catalog["vendor_name"].str.lower() == vendor]
        same_category = catalog[catalog["category"].str.lower() == category]

        candidates = same_product
        if candidates.empty:
            candidates = same_vendor
        if candidates.empty:
            candidates = same_category

        records = []
        for _, row in candidates.head(5).iterrows():
            records.append({
                "product_name": row["product_name"],
                "vendor_name": row["vendor_name"],
                "category": row["category"],
                "status": row["status"],
                "licensed_seats": int(row["licensed_seats"]),
                "scope": row["scope"],
                "notes": row["notes"],
            })

        historical = history[
            (history["vendor_name"].str.lower() == vendor)
            | (history["product_name"].str.lower() == product)
        ]
        purchase_records = historical[["department", "vendor_name", "product_name", "annual_amount_usd", "status"]].to_dict("records")

        return ToolResult(
            self.name,
            True,
            {
                "same_product": same_product.to_dict("records"),
                "alternatives": records,
                "purchase_history": purchase_records,
            },
        )
