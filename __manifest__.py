{
    "name": "Product Equivalents",
    "summary": "Commercially equivalent products in product search and sales orders",
    "version": "16.0.1.0.0",
    "category": "Sales/Sales",
    "author": "Community",
    "website": "",
    "license": "LGPL-3",
    "depends": ["product", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_equivalent_group_views.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
