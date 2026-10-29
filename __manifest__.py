{
    "name": "Product Equivalents",
    "summary": "Commercially equivalent products in product search and sales orders",
    "version": "18.0.2.0.0",
    "category": "Products",
    "author": "GT CONSULTORIA E TECNOLOGIA",
    "website": "https://gotek.tec.br",
    "license": "LGPL-3",
    "depends": ["product", "sale_management"],
    "data": [
        "security/product_equivalent_security.xml",
        "security/ir.model.access.csv",
        "views/product_equivalent_group_views.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
