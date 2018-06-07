# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    media_ids = fields.One2many(
        'product.media.relation',
        inverse_name='product_tmpl_id',
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    variant_media_ids = fields.Many2many(
        'product.media.relation',
        compute="_compute_variant_media_ids",
        store=True)

    @api.depends('product_tmpl_id.media_ids', 'attribute_value_ids')
    def _compute_variant_media_ids(self):
        for variant in self:
            res = self.env['product.media.relation'].browse([])
            for media in variant.media_ids:
                if not (media.attribute_value_ids -
                        variant.attribute_value_ids):
                    res |= media
            variant.variant_media_ids = res


class ProductMediaRelation(models.Model):
    _name = 'product.media.relation'
    _order = 'sequence, media_id'

    sequence = fields.Integer()
    media_id = fields.Many2one(
        'storage.media',
        required=True,
    )
    attribute_value_ids = fields.Many2many(
        'product.attribute.value',
        string='Attributes'
    )
    # This field will list all attribute value used by the template
    # in order to filter the attribute value available for the current media
    available_attribute_value_ids = fields.Many2many(
        'product.attribute.value',
        string='Attributes',
        compute="_compute_available_attribute"
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
    )
    media_type_id = fields.Many2one(
        'storage.media.type',
        'Media Type',
        related='media_id.media_type_id',
    )

    @api.depends('media_id', 'product_tmpl_id.attribute_line_ids.value_ids')
    def _compute_available_attribute(self):
        # the depend on 'media_id' only added for triggering the onchange
        for record in self:
            record.available_attribute_value_ids =\
                record.product_tmpl_id.mapped('attribute_line_ids.value_ids')
