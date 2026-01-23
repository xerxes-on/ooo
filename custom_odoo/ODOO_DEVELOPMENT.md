# Odoo Module Development Guide

A comprehensive guide for developing Odoo 18+ modules.

---

## Module Structure

```
my_module/
├── __init__.py              # Import models, wizards, reports
├── __manifest__.py          # Module metadata and dependencies
├── models/
│   ├── __init__.py          # Import model files
│   └── my_model.py          # Model definitions
├── views/
│   └── my_views.xml         # View definitions, actions, menus
├── security/
│   ├── ir.model.access.csv  # Access control list
│   └── security.xml         # Groups and record rules
├── data/
│   └── data.xml             # Default/demo data
├── wizards/
│   ├── __init__.py          # Import wizard files
│   └── my_wizard.py         # Transient models
├── reports/
│   ├── __init__.py          # Import report files
│   └── my_report.xml        # QWeb report templates
├── static/
│   ├── description/
│   │   └── icon.png         # Module icon (128x128 or 256x256)
│   └── src/
│       ├── js/              # JavaScript files
│       └── scss/            # SCSS stylesheets
└── tests/
    ├── __init__.py          # Import test files
    └── test_my_model.py     # Unit tests
```

---

## Core Components

### 1. `__manifest__.py`

```python
{
    'name': 'Module Name',
    'version': '18.0.1.0.0',  # odoo_version.major.minor.patch
    'category': 'Category',
    'summary': 'Short description',
    'description': """Long description""",
    'author': 'Your Company',
    'website': 'https://yourwebsite.com',
    'license': 'LGPL-3',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/my_views.xml',
    ],
    'demo': ['demo/demo_data.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

### 2. Model Definition

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MyModel(models.Model):
    _name = 'x_custom.my_model'  # x_ prefix for Studio compatibility
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter
    _order = 'sequence, name'

    # Fields
    name = fields.Char(string='Name', required=True, tracking=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    line_ids = fields.One2many('x_custom.my_line', 'parent_id', string='Lines')
    tag_ids = fields.Many2many('x_custom.tag', string='Tags')
    amount = fields.Float(digits='Product Price')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    # Computed field
    total = fields.Float(compute='_compute_total', store=True)

    @api.depends('line_ids.amount')
    def _compute_total(self):
        for record in self:
            record.total = sum(record.line_ids.mapped('amount'))

    # Constraints
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError("Amount cannot be negative!")

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]

    # CRUD overrides
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    def write(self, vals):
        return super().write(vals)

    def unlink(self):
        return super().unlink()

    # Action methods
    def action_confirm(self):
        self.write({'state': 'confirmed'})
```

### 3. Extending Existing Models

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    custom_field = fields.Char(string='Custom Field')
    custom_count = fields.Integer(compute='_compute_custom_count')

    def _compute_custom_count(self):
        for partner in self:
            partner.custom_count = self.env['x_custom.my_model'].search_count([
                ('partner_id', '=', partner.id)
            ])
```

---

## Views (Odoo 18+)

### List View (replaces Tree in Odoo 18+)

```xml
<record id="my_model_view_list" model="ir.ui.view">
    <field name="name">x_custom.my_model.view.list</field>
    <field name="model">x_custom.my_model</field>
    <field name="arch" type="xml">
        <list string="My Models">
            <field name="sequence" widget="handle"/>
            <field name="name"/>
            <field name="partner_id"/>
            <field name="state" widget="badge"/>
        </list>
    </field>
</record>
```

### Form View

```xml
<record id="my_model_view_form" model="ir.ui.view">
    <field name="name">x_custom.my_model.view.form</field>
    <field name="model">x_custom.my_model</field>
    <field name="arch" type="xml">
        <form string="My Model">
            <header>
                <button name="action_confirm" string="Confirm" type="object"
                        class="btn-primary" invisible="state != 'draft'"/>
                <field name="state" widget="statusbar"/>
            </header>
            <sheet>
                <div class="oe_title">
                    <h1><field name="name"/></h1>
                </div>
                <group>
                    <group>
                        <field name="partner_id"/>
                    </group>
                    <group>
                        <field name="amount"/>
                    </group>
                </group>
                <notebook>
                    <page string="Lines" name="lines">
                        <field name="line_ids">
                            <list editable="bottom">
                                <field name="name"/>
                                <field name="amount"/>
                            </list>
                        </field>
                    </page>
                </notebook>
            </sheet>
            <chatter/>
        </form>
    </field>
</record>
```

### Search View

```xml
<record id="my_model_view_search" model="ir.ui.view">
    <field name="name">x_custom.my_model.view.search</field>
    <field name="model">x_custom.my_model</field>
    <field name="arch" type="xml">
        <search string="Search">
            <field name="name"/>
            <field name="partner_id"/>
            <filter name="draft" string="Draft" domain="[('state', '=', 'draft')]"/>
            <group expand="0" string="Group By">
                <filter name="groupby_state" string="Status" context="{'group_by': 'state'}"/>
            </group>
        </search>
    </field>
</record>
```

### Kanban View

```xml
<record id="my_model_view_kanban" model="ir.ui.view">
    <field name="name">x_custom.my_model.view.kanban</field>
    <field name="model">x_custom.my_model</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state">
            <templates>
                <t t-name="card">
                    <field name="name" class="fw-bold"/>
                    <field name="partner_id"/>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

---

## Actions and Menus

```xml
<!-- Action -->
<record id="my_model_action" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">x_custom.my_model</field>
    <field name="view_mode">list,kanban,form</field>
    <field name="context">{}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">Create your first record!</p>
    </field>
</record>

<!-- Menu -->
<menuitem id="menu_root" name="My App" sequence="100"/>
<menuitem id="menu_main" name="Main Menu" parent="menu_root" sequence="10"/>
<menuitem id="menu_my_model" name="My Models" parent="menu_main"
          action="my_model_action" sequence="10"/>
```

---

## Security

### Access Control (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_x_custom_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_x_custom_my_model,base.group_system,1,1,1,1
```

### Record Rules (security.xml)

```xml
<record id="my_model_rule_company" model="ir.rule">
    <field name="name">My Model: Multi-company</field>
    <field name="model_id" ref="model_x_custom_my_model"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    <field name="global" eval="True"/>
</record>
```

---

## Wizards (Transient Models)

```python
from odoo import models, fields

class MyWizard(models.TransientModel):
    _name = 'x_custom.my_wizard'
    _description = 'My Wizard'

    name = fields.Char(required=True)
    model_ids = fields.Many2many('x_custom.my_model')

    def action_apply(self):
        for record in self.model_ids:
            record.write({'name': self.name})
        return {'type': 'ir.actions.act_window_close'}
```

---

## Testing

```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestMyModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Model = cls.env['x_custom.my_model']
        cls.record = cls.Model.create({'name': 'Test'})

    def test_create(self):
        self.assertEqual(self.record.state, 'draft')

    def test_confirm(self):
        self.record.action_confirm()
        self.assertEqual(self.record.state, 'confirmed')

    def test_constraint(self):
        with self.assertRaises(ValidationError):
            self.record.write({'amount': -100})
```

---

## Best Practices

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Model name | `x_custom.model_name` | `x_custom.sale_order_line` |
| Field name | `snake_case` | `total_amount` |
| XML ID | `module_name.type_model_name` | `custom_odoo.view_sale_order_form` |
| Python file | `snake_case.py` | `sale_order.py` |

### Odoo 18+ Changes

- Use `list` instead of `tree` in view types
- Use `invisible` instead of `attrs={'invisible': ...}`
- Verify field existence with `fields_get()` before using in domains
- `company_id` may be `company_ids` (Many2many) in some models

### Performance Tips

- Use `@api.depends` only on fields that truly need recomputation
- Use `store=True` for computed fields used in search/filter
- Avoid `search()` inside loops; use `search()` once and filter
- Use `read_group()` for aggregations instead of iterating

---

## Useful Commands

```python
# Search records
records = self.env['res.partner'].search([('is_company', '=', True)], limit=10)

# Read specific fields
data = records.read(['name', 'email'])

# Create record
new = self.env['res.partner'].create({'name': 'New Partner'})

# Update records
records.write({'active': False})

# Delete records
records.unlink()

# Execute raw SQL (use sparingly)
self.env.cr.execute("SELECT id FROM res_partner WHERE active = true")

# Get current user/company
user = self.env.user
company = self.env.company
```

---

## Resources

- [Odoo Documentation](https://www.odoo.com/documentation/18.0/)
- [Odoo ORM Reference](https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html)
- [Odoo Views Reference](https://www.odoo.com/documentation/18.0/developer/reference/backend/views.html)
