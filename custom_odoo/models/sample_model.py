# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SampleModel(models.Model):
    """
    Sample Model - Template for creating new Odoo models.

    Use this as a reference for:
    - Field definitions
    - Computed fields
    - Constraints
    - CRUD overrides
    """
    _name = 'x_custom.sample'
    _description = 'Sample Model'
    _order = 'sequence, name'

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    description = fields.Text(
        string='Description',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
    )
    amount = fields.Float(
        string='Amount',
        digits='Product Price',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
    )

    # Computed field example
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends('name', 'state')
    def _compute_display_name(self):
        for record in self:
            if record.name:
                record.display_name = f"{record.name} ({record.state})"
            else:
                record.display_name = False

    # -------------------------------------------------------------------------
    # CONSTRAINTS
    # -------------------------------------------------------------------------
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError("Amount cannot be negative!")

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name, company_id)', 'Name must be unique per company!'),
    ]

    # -------------------------------------------------------------------------
    # CRUD METHODS
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        # Add custom logic before create
        return super().create(vals_list)

    def write(self, vals):
        # Add custom logic before write
        return super().write(vals)

    def unlink(self):
        # Add custom logic before delete
        for record in self:
            if record.state == 'done':
                raise ValidationError("Cannot delete records in 'Done' state!")
        return super().unlink()

    # -------------------------------------------------------------------------
    # ACTION METHODS
    # -------------------------------------------------------------------------
    def action_confirm(self):
        """Confirm the record."""
        self.write({'state': 'confirmed'})

    def action_done(self):
        """Mark record as done."""
        self.write({'state': 'done'})

    def action_cancel(self):
        """Cancel the record."""
        self.write({'state': 'cancelled'})

    def action_draft(self):
        """Reset to draft."""
        self.write({'state': 'draft'})
