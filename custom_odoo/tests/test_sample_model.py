# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSampleModel(TransactionCase):
    """Test cases for the Sample Model."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.SampleModel = cls.env['x_custom.sample']
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
        })

    def test_create_sample(self):
        """Test creating a sample record."""
        sample = self.SampleModel.create({
            'name': 'Test Sample',
            'partner_id': self.partner.id,
        })
        self.assertEqual(sample.state, 'draft')
        self.assertEqual(sample.name, 'Test Sample')
        self.assertTrue(sample.active)

    def test_action_confirm(self):
        """Test confirming a sample record."""
        sample = self.SampleModel.create({'name': 'Confirm Test'})
        sample.action_confirm()
        self.assertEqual(sample.state, 'confirmed')

    def test_action_done(self):
        """Test marking a sample as done."""
        sample = self.SampleModel.create({'name': 'Done Test'})
        sample.action_confirm()
        sample.action_done()
        self.assertEqual(sample.state, 'done')

    def test_action_cancel(self):
        """Test cancelling a sample record."""
        sample = self.SampleModel.create({'name': 'Cancel Test'})
        sample.action_cancel()
        self.assertEqual(sample.state, 'cancelled')

    def test_action_draft(self):
        """Test resetting a sample to draft."""
        sample = self.SampleModel.create({'name': 'Draft Test'})
        sample.action_cancel()
        sample.action_draft()
        self.assertEqual(sample.state, 'draft')

    def test_amount_constraint(self):
        """Test that negative amounts raise ValidationError."""
        sample = self.SampleModel.create({'name': 'Constraint Test'})
        with self.assertRaises(ValidationError):
            sample.write({'amount': -100})

    def test_cannot_delete_done_record(self):
        """Test that done records cannot be deleted."""
        sample = self.SampleModel.create({'name': 'Delete Test'})
        sample.action_confirm()
        sample.action_done()
        with self.assertRaises(ValidationError):
            sample.unlink()

    def test_display_name_computed(self):
        """Test that display_name is computed correctly."""
        sample = self.SampleModel.create({'name': 'Display Test'})
        self.assertEqual(sample.display_name, 'Display Test (draft)')
        sample.action_confirm()
        self.assertEqual(sample.display_name, 'Display Test (confirmed)')
